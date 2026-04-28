"""
统一配置中心 —— 所有配置项从环境变量读取，支持 .env 文件。

部署前必须设置的环境变量:
  WECOM_CORP_ID        企业微信 corpid
  WECOM_APP_SECRET     应用 Secret
  WECOM_AGENT_ID       应用 AgentId
  WECOM_TOKEN          回调 Token（接收消息验证）
  WECOM_ENCODING_AES_KEY   回调 EncodingAESKey
  OPENAI_API_KEY       OpenAI（或兼容接口）的 API Key

可选:
  OPENAI_BASE_URL      自定义 API 地址（用于接入其他大模型）
  OPENAI_MODEL         模型名称，默认 gpt-4o
  SERVER_PORT          服务端口，默认 8080
  LOG_LEVEL            日志级别，默认 INFO
"""

import os
from pathlib import Path

from dotenv import load_dotenv

_env_path = Path(__file__).resolve().parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)

# ---- 企业微信 ----
WECOM_CORP_ID = os.getenv("WECOM_CORP_ID", "")
WECOM_APP_SECRET = os.getenv("WECOM_APP_SECRET", "")
WECOM_AGENT_ID = os.getenv("WECOM_AGENT_ID", "")
WECOM_TOKEN = os.getenv("WECOM_TOKEN", "")
WECOM_ENCODING_AES_KEY = os.getenv("WECOM_ENCODING_AES_KEY", "")

# ---- LLM ----
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# ---- 服务 ----
SERVER_PORT = int(os.getenv("SERVER_PORT", "8080"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ---- 对话管理 ----
MAX_HISTORY_TURNS = int(os.getenv("MAX_HISTORY_TURNS", "20"))
HISTORY_TTL_SECONDS = int(os.getenv("HISTORY_TTL_SECONDS", "1800"))
