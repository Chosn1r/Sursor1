"""
企业微信消息加解密模块。

实现 WXBizMsgCrypt 协议：
- URL 验证（解密 echostr）
- 接收消息解密
- 回复消息加密

基于企业微信官方文档：
https://developer.work.weixin.qq.com/document/path/90968
"""

import base64
import hashlib
import socket
import struct
import time
import xml.etree.ElementTree as ET

from Crypto.Cipher import AES


class WXBizMsgCrypt:
    """企业微信回调消息加解密工具类。"""

    def __init__(self, token: str, encoding_aes_key: str, corp_id: str):
        self.token = token
        self.corp_id = corp_id
        self.aes_key = base64.b64decode(encoding_aes_key + "=")

    # ---- 签名 ----

    @staticmethod
    def _make_signature(token: str, timestamp: str, nonce: str, encrypt: str) -> str:
        parts = sorted([token, timestamp, nonce, encrypt])
        return hashlib.sha1("".join(parts).encode("utf-8")).hexdigest()

    def verify_signature(
        self, msg_signature: str, timestamp: str, nonce: str, encrypt: str
    ) -> bool:
        return self._make_signature(self.token, timestamp, nonce, encrypt) == msg_signature

    # ---- PKCS#7 Padding ----

    @staticmethod
    def _pkcs7_pad(data: bytes, block_size: int = 32) -> bytes:
        pad_len = block_size - (len(data) % block_size)
        return data + bytes([pad_len] * pad_len)

    @staticmethod
    def _pkcs7_unpad(data: bytes) -> bytes:
        pad_len = data[-1]
        return data[:-pad_len]

    # ---- 加密 / 解密 ----

    def _encrypt(self, plaintext: str) -> str:
        text = plaintext.encode("utf-8")
        rand_bytes = hashlib.md5(str(time.time()).encode()).digest()
        content = rand_bytes + struct.pack("!I", len(text)) + text + self.corp_id.encode("utf-8")
        padded = self._pkcs7_pad(content)
        cipher = AES.new(self.aes_key, AES.MODE_CBC, self.aes_key[:16])
        encrypted = cipher.encrypt(padded)
        return base64.b64encode(encrypted).decode("utf-8")

    def _decrypt(self, ciphertext: str) -> str:
        cipher = AES.new(self.aes_key, AES.MODE_CBC, self.aes_key[:16])
        decrypted = cipher.decrypt(base64.b64decode(ciphertext))
        plaintext = self._pkcs7_unpad(decrypted)
        msg_len = struct.unpack("!I", plaintext[16:20])[0]
        msg = plaintext[20 : 20 + msg_len].decode("utf-8")
        from_corp_id = plaintext[20 + msg_len :].decode("utf-8")
        if from_corp_id != self.corp_id:
            raise ValueError(f"CorpId mismatch: expected {self.corp_id}, got {from_corp_id}")
        return msg

    # ---- 公开 API ----

    def decrypt_echostr(
        self, msg_signature: str, timestamp: str, nonce: str, echostr: str
    ) -> str:
        """URL 验证时解密 echostr 并返回明文。"""
        if not self.verify_signature(msg_signature, timestamp, nonce, echostr):
            raise ValueError("Signature verification failed for echostr")
        return self._decrypt(echostr)

    def decrypt_message(
        self, msg_signature: str, timestamp: str, nonce: str, post_data: str
    ) -> str:
        """解密接收到的 XML 消息体，返回明文 XML。"""
        root = ET.fromstring(post_data)
        encrypt_node = root.find("Encrypt")
        if encrypt_node is None:
            raise ValueError("Missing <Encrypt> in post data")
        encrypt = encrypt_node.text or ""
        if not self.verify_signature(msg_signature, timestamp, nonce, encrypt):
            raise ValueError("Signature verification failed")
        return self._decrypt(encrypt)

    def encrypt_message(self, reply_msg: str, nonce: str, timestamp: str | None = None) -> str:
        """加密回复消息，返回密文 XML。"""
        ts = timestamp or str(int(time.time()))
        encrypt = self._encrypt(reply_msg)
        signature = self._make_signature(self.token, ts, nonce, encrypt)

        return (
            "<xml>"
            f"<Encrypt><![CDATA[{encrypt}]]></Encrypt>"
            f"<MsgSignature><![CDATA[{signature}]]></MsgSignature>"
            f"<TimeStamp>{ts}</TimeStamp>"
            f"<Nonce><![CDATA[{nonce}]]></Nonce>"
            "</xml>"
        )
