# ZCAMP K6 企业微信 AI 客服 — 小龙虾 🦞

基于大语言模型的企业微信智能客服系统，专为 ZCAMP K6 智能住宿舱产品线打造。

## 功能概览

| 功能 | 说明 |
|------|------|
| 产品咨询 | 自动回答 K6 SE / PRO / MAX 的参数、价格、配置等问题 |
| 智能话术 | 内置完整的销售流程话术（问候→需求挖掘→推荐→异议处理→留资→结束） |
| 对话记忆 | 维护每个用户的对话上下文，支持多轮连续对话 |
| 消息加解密 | 完整实现企业微信回调消息加解密协议 |
| 欢迎消息 | 用户首次关注时自动发送欢迎语和产品概览 |
| 多模型支持 | 支持 OpenAI、DeepSeek、智谱 AI 等兼容 OpenAI 接口的大模型 |
| Docker 部署 | 提供 Dockerfile 和 docker-compose，一键部署 |

## 项目结构

```
wecom_chatbot/
├── __init__.py              # 包定义
├── config.py                # 统一配置中心（从环境变量读取）
├── app.py                   # Flask Webhook 服务（主入口）
├── chat_engine.py           # AI 对话引擎（LLM 调用 + 对话历史管理）
├── wecom_api.py             # 企业微信 API 客户端（发消息、管理 token）
├── wecom_crypto.py          # 企业微信消息加解密
├── test_chat.py             # 本地终端测试工具
├── knowledge_base/
│   ├── __init__.py
│   └── product_info.py      # 产品知识库 + FAQ + 话术模板 + System Prompt
├── .env.example             # 环境变量模板
├── requirements.txt         # Python 依赖
├── Dockerfile               # Docker 镜像构建
├── docker-compose.yml       # Docker Compose 编排
└── README.md                # 本文档
```

## 快速开始

### 1. 安装依赖

```bash
cd wecom_chatbot
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入实际的企业微信和 AI 配置
```

### 3. 本地测试（无需企业微信）

先配置好 `OPENAI_API_KEY`，然后：

```bash
python -m wecom_chatbot.test_chat
```

即可在终端与 AI 客服小龙虾对话，验证回复效果。

### 4. 启动服务

**开发环境：**

```bash
python -m wecom_chatbot.app
```

**生产环境：**

```bash
gunicorn wecom_chatbot.app:app -b 0.0.0.0:8080 -w 4
```

**Docker 部署：**

```bash
cd wecom_chatbot
docker-compose up -d
```

### 5. 配置企业微信

1. 登录 [企业微信管理后台](https://work.weixin.qq.com/wework_admin/frame)
2. 进入 **应用管理** → 创建自建应用
3. 记录 `AgentId` 和 `Secret`
4. 在 **企业信息** 页面获取 `CorpID`
5. 在应用的 **接收消息** 设置中：
   - URL 填写: `https://你的域名/wecom/callback`
   - Token 和 EncodingAESKey 填入 `.env` 对应的值
6. 保存后企业微信会发起 URL 验证，服务会自动处理

## 配置参数说明

| 环境变量 | 必填 | 说明 |
|----------|------|------|
| `WECOM_CORP_ID` | ✅ | 企业微信 CorpID |
| `WECOM_APP_SECRET` | ✅ | 应用 Secret |
| `WECOM_AGENT_ID` | ✅ | 应用 AgentId |
| `WECOM_TOKEN` | ✅ | 回调 Token |
| `WECOM_ENCODING_AES_KEY` | ✅ | 回调 EncodingAESKey |
| `OPENAI_API_KEY` | ✅ | LLM API Key |
| `OPENAI_BASE_URL` | ❌ | 自定义 API 地址（接入其他模型时使用） |
| `OPENAI_MODEL` | ❌ | 模型名称，默认 `gpt-4o` |
| `SERVER_PORT` | ❌ | 服务端口，默认 `8080` |
| `LOG_LEVEL` | ❌ | 日志级别，默认 `INFO` |
| `MAX_HISTORY_TURNS` | ❌ | 对话最大轮数，默认 `20` |
| `HISTORY_TTL_SECONDS` | ❌ | 对话过期时间（秒），默认 `1800` |

## 使用国产大模型

本系统支持所有兼容 OpenAI 接口的大模型，只需修改 `OPENAI_BASE_URL` 和 `OPENAI_MODEL`：

**DeepSeek：**
```env
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-chat
OPENAI_API_KEY=your_deepseek_key
```

**智谱 AI (GLM)：**
```env
OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
OPENAI_MODEL=glm-4
OPENAI_API_KEY=your_zhipu_key
```

**通义千问：**
```env
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_MODEL=qwen-max
OPENAI_API_KEY=your_dashscope_key
```

## 自定义知识库和话术

所有产品知识、FAQ、销售话术都集中在 `knowledge_base/product_info.py` 中：

- **`PRODUCT_MODELS`** — 产品参数（价格、配置、适用场景）
- **`FAQ`** — 常见问题和标准回答
- **`SALES_SCRIPTS`** — 各阶段销售话术模板
- **`SYSTEM_PROMPT`** — AI 行为指令（修改此处可调整 AI 的回复风格和规则）

运营人员只需编辑这个文件，重启服务即可生效，无需修改代码逻辑。

## 架构说明

```
企业微信用户
    │
    ▼
企业微信服务器
    │
    ▼ POST /wecom/callback (加密XML)
┌─────────────────────────┐
│  Flask Webhook 服务      │
│  ├─ 消息解密             │
│  ├─ 提取用户消息          │
│  └─ 异步处理 ──────────► │
│     ├─ ChatEngine        │  ──► LLM API (OpenAI / DeepSeek / ...)
│     │  ├─ 对话历史管理    │
│     │  └─ 生成回复        │
│     └─ WeComClient       │  ──► 企业微信 API (发送消息)
│        ├─ access_token   │
│        └─ send_text()    │
└─────────────────────────┘
```

## 健康检查

```bash
curl http://localhost:8080/health
# 返回: {"status": "ok", "service": "wecom-ai-chatbot"}
```
