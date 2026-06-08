"""
企业微信 AI 客服 — Flask Webhook 服务。

接收企业微信的回调请求，解密消息后调用 AI 引擎生成回复，
再通过企业微信 API 主动发送回复消息给用户。

启动方式:
  开发环境: python -m wecom_chatbot.app
  生产环境: gunicorn wecom_chatbot.app:app -b 0.0.0.0:8080 -w 4
"""

import logging
import threading
import xml.etree.ElementTree as ET

from flask import Flask, Response, request

from . import config
from .chat_engine import ChatEngine
from .wecom_api import WeComClient
from .wecom_crypto import WXBizMsgCrypt

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

crypto = WXBizMsgCrypt(
    token=config.WECOM_TOKEN,
    encoding_aes_key=config.WECOM_ENCODING_AES_KEY,
    corp_id=config.WECOM_CORP_ID,
)
wecom_client = WeComClient()
chat_engine = ChatEngine()


@app.route("/wecom/callback", methods=["GET"])
def verify_url():
    """企业微信回调 URL 验证（首次配置时触发）。"""
    msg_signature = request.args.get("msg_signature", "")
    timestamp = request.args.get("timestamp", "")
    nonce = request.args.get("nonce", "")
    echostr = request.args.get("echostr", "")

    try:
        echo_plain = crypto.decrypt_echostr(msg_signature, timestamp, nonce, echostr)
        return Response(echo_plain, content_type="text/plain")
    except Exception:
        logger.exception("URL verification failed")
        return Response("verification failed", status=403)


@app.route("/wecom/callback", methods=["POST"])
def receive_message():
    """接收企业微信推送的用户消息。"""
    msg_signature = request.args.get("msg_signature", "")
    timestamp = request.args.get("timestamp", "")
    nonce = request.args.get("nonce", "")
    post_data = request.data.decode("utf-8")

    try:
        xml_plain = crypto.decrypt_message(msg_signature, timestamp, nonce, post_data)
    except Exception:
        logger.exception("Message decryption failed")
        return Response("decrypt error", status=400)

    root = ET.fromstring(xml_plain)
    msg_type = (root.findtext("MsgType") or "").strip()
    from_user = (root.findtext("FromUserName") or "").strip()
    content = (root.findtext("Content") or "").strip()

    logger.info("Received [%s] from %s: %s", msg_type, from_user, content[:100])

    if msg_type == "text" and from_user and content:
        # 异步处理避免阻塞企业微信的 5 秒超时
        threading.Thread(
            target=_handle_text_message,
            args=(from_user, content),
            daemon=True,
        ).start()
    elif msg_type == "event":
        event_type = (root.findtext("Event") or "").strip()
        if event_type in ("subscribe", "enter_agent"):
            threading.Thread(
                target=_handle_subscribe,
                args=(from_user,),
                daemon=True,
            ).start()

    return Response("success", content_type="text/plain")


def _handle_text_message(user_id: str, content: str) -> None:
    """处理文本消息：调用 AI 引擎后通过 API 回复。"""
    try:
        reply = chat_engine.reply(user_id, content)
        wecom_client.send_text(user_id, reply)
    except Exception:
        logger.exception("Error handling message from %s", user_id)
        try:
            wecom_client.send_text(
                user_id,
                "抱歉，系统暂时遇到了问题，请稍后再试。如需帮助请拨打客服热线。",
            )
        except Exception:
            logger.exception("Failed to send error message to %s", user_id)


def _handle_subscribe(user_id: str) -> None:
    """用户关注/进入应用时发送欢迎消息。"""
    welcome = (
        "您好！欢迎关注 ZCAMP 智能住宿舱 🏕️\n\n"
        "我是您的 AI 客服小龙虾 🦞，可以为您介绍我们的 K6 系列产品：\n\n"
        "🔹 K6 SE — 入门展示版（$5,900 起）\n"
        "🔹 K6 PRO — 主推平衡款（$7,900 起）\n"
        "🔹 K6 MAX — 高配定制款（定制报价）\n\n"
        "有任何问题随时问我！"
    )
    try:
        wecom_client.send_text(user_id, welcome)
    except Exception:
        logger.exception("Failed to send welcome to %s", user_id)


@app.route("/health", methods=["GET"])
def health_check():
    """健康检查端点，供负载均衡或监控使用。"""
    return {"status": "ok", "service": "wecom-ai-chatbot"}


if __name__ == "__main__":
    logger.info("Starting WeChat AI Chatbot on port %d", config.SERVER_PORT)
    app.run(host="0.0.0.0", port=config.SERVER_PORT, debug=True)
