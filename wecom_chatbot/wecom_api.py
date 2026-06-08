"""
企业微信 API 客户端 —— 负责发送消息、管理 access_token 等。

主要功能:
- 自动获取和缓存 access_token
- 发送文本消息给指定用户
- 发送 Markdown 消息（企业微信内部支持）
"""

import logging
import threading
import time

import requests

from . import config

logger = logging.getLogger(__name__)

_TOKEN_URL = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
_SEND_MSG_URL = "https://qyapi.weixin.qq.com/cgi-bin/message/send"


class WeComClient:
    """企业微信 API 封装，线程安全地管理 access_token 并提供消息发送能力。"""

    def __init__(
        self,
        corp_id: str | None = None,
        app_secret: str | None = None,
        agent_id: str | None = None,
    ):
        self.corp_id = corp_id or config.WECOM_CORP_ID
        self.app_secret = app_secret or config.WECOM_APP_SECRET
        self.agent_id = agent_id or config.WECOM_AGENT_ID

        self._access_token: str = ""
        self._token_expires_at: float = 0
        self._lock = threading.Lock()

    # ---- Token 管理 ----

    def _fetch_token(self) -> tuple[str, int]:
        resp = requests.get(
            _TOKEN_URL,
            params={"corpid": self.corp_id, "corpsecret": self.app_secret},
            timeout=10,
        )
        data = resp.json()
        if data.get("errcode", 0) != 0:
            raise RuntimeError(f"Failed to get access_token: {data}")
        return data["access_token"], data.get("expires_in", 7200)

    @property
    def access_token(self) -> str:
        with self._lock:
            if time.time() >= self._token_expires_at - 300:
                token, expires_in = self._fetch_token()
                self._access_token = token
                self._token_expires_at = time.time() + expires_in
                logger.info("WeChat access_token refreshed, expires in %ds", expires_in)
            return self._access_token

    # ---- 发送消息 ----

    def send_text(self, user_id: str, content: str) -> dict:
        """向指定用户发送文本消息。"""
        payload = {
            "touser": user_id,
            "msgtype": "text",
            "agentid": self.agent_id,
            "text": {"content": content},
        }
        return self._post_message(payload)

    def send_markdown(self, user_id: str, content: str) -> dict:
        """向指定用户发送 Markdown 消息（仅企业微信内部可见）。"""
        payload = {
            "touser": user_id,
            "msgtype": "markdown",
            "agentid": self.agent_id,
            "markdown": {"content": content},
        }
        return self._post_message(payload)

    def _post_message(self, payload: dict) -> dict:
        resp = requests.post(
            _SEND_MSG_URL,
            params={"access_token": self.access_token},
            json=payload,
            timeout=10,
        )
        data = resp.json()
        if data.get("errcode", 0) != 0:
            logger.error("Send message failed: %s", data)
        else:
            logger.debug("Message sent to %s", payload.get("touser"))
        return data
