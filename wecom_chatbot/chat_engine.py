"""
AI 对话引擎 —— 基于大语言模型生成客服回复。

功能:
- 维护每个用户的对话历史（带 TTL 自动过期）
- 使用 system prompt + 产品知识库指导生成
- 支持 OpenAI 兼容接口（可切换至其他国产大模型）
"""

import logging
import threading
import time

from openai import OpenAI

from . import config
from .knowledge_base.product_info import SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class ConversationStore:
    """线程安全的用户对话历史管理，支持 TTL 过期和最大轮数限制。"""

    def __init__(
        self,
        max_turns: int = config.MAX_HISTORY_TURNS,
        ttl_seconds: int = config.HISTORY_TTL_SECONDS,
    ):
        self.max_turns = max_turns
        self.ttl = ttl_seconds
        self._store: dict[str, dict] = {}
        self._lock = threading.Lock()

    def get_history(self, user_id: str) -> list[dict]:
        with self._lock:
            entry = self._store.get(user_id)
            if entry is None:
                return []
            if time.time() - entry["last_active"] > self.ttl:
                del self._store[user_id]
                return []
            return list(entry["messages"])

    def append(self, user_id: str, role: str, content: str) -> None:
        with self._lock:
            if user_id not in self._store:
                self._store[user_id] = {"messages": [], "last_active": time.time()}
            entry = self._store[user_id]
            entry["messages"].append({"role": role, "content": content})
            entry["last_active"] = time.time()
            if len(entry["messages"]) > self.max_turns * 2:
                entry["messages"] = entry["messages"][-(self.max_turns * 2) :]

    def clear(self, user_id: str) -> None:
        with self._lock:
            self._store.pop(user_id, None)

    def cleanup_expired(self) -> int:
        """清理所有过期会话，返回清理数量。"""
        now = time.time()
        removed = 0
        with self._lock:
            expired_keys = [
                k for k, v in self._store.items() if now - v["last_active"] > self.ttl
            ]
            for k in expired_keys:
                del self._store[k]
                removed += 1
        return removed


class ChatEngine:
    """核心 AI 对话引擎。"""

    def __init__(self):
        self.client = OpenAI(
            api_key=config.OPENAI_API_KEY,
            base_url=config.OPENAI_BASE_URL,
        )
        self.model = config.OPENAI_MODEL
        self.conversations = ConversationStore()
        self._system_message = {"role": "system", "content": SYSTEM_PROMPT}

    def reply(self, user_id: str, user_message: str) -> str:
        """根据用户消息生成 AI 回复。"""
        if self._is_reset_command(user_message):
            self.conversations.clear(user_id)
            return "对话已重置，有什么可以帮您的吗？"

        self.conversations.append(user_id, "user", user_message)
        history = self.conversations.get_history(user_id)

        messages = [self._system_message] + history

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=800,
                top_p=0.9,
            )
            assistant_msg = response.choices[0].message.content or ""
            assistant_msg = assistant_msg.strip()
        except Exception:
            logger.exception("LLM API call failed for user %s", user_id)
            assistant_msg = (
                "抱歉，系统暂时遇到了一点问题，请稍后再试。"
                "如需紧急帮助，请拨打我们的客服热线。"
            )

        self.conversations.append(user_id, "assistant", assistant_msg)
        return assistant_msg

    @staticmethod
    def _is_reset_command(msg: str) -> bool:
        return msg.strip().lower() in {"重置", "reset", "清除对话", "重新开始"}
