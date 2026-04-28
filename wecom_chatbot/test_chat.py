"""
本地终端测试工具 —— 无需企业微信即可测试 AI 客服对话效果。

用法:
  1. 在 .env 中配置好 OPENAI_API_KEY（以及可选的 OPENAI_BASE_URL / OPENAI_MODEL）
  2. 运行: python -m wecom_chatbot.test_chat
  3. 在终端中输入消息即可与 AI 客服对话，输入 quit/exit 退出
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wecom_chatbot.chat_engine import ChatEngine

TEST_USER_ID = "test_user"


def main():
    engine = ChatEngine()
    print("=" * 60)
    print("  ZCAMP K6 AI 客服 — 本地测试模式")
    print("  输入消息与小龙虾对话，输入 quit 退出")
    print("=" * 60)
    print()

    while True:
        try:
            user_input = input("👤 你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if not user_input:
            continue
        if user_input.lower() in {"quit", "exit", "q"}:
            print("再见！")
            break

        reply = engine.reply(TEST_USER_ID, user_input)
        print(f"🦞 小龙虾: {reply}")
        print()


if __name__ == "__main__":
    main()
