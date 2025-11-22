OpenAI Chat Client

一个轻量级的 OpenAI 风格 API 客户端，使用 Python 的 requests 库实现，支持同步调用和流式响应。

功能特性

· 🚀 轻量级实现：基于 requests 库，无复杂依赖
· 💬 聊天补全：支持 OpenAI Chat Completions API
· 📡 流式响应：支持服务器推送事件（SSE）格式的流式响应
· 🔧 易于扩展：模块化设计，易于添加新的 API 端点
· 🛡️ 错误处理：完善的网络和 API 错误处理
· 🐍 类型提示：完整的 Python 类型注解

安装要求

```bash
pip install requests
```

快速开始

基本使用

```python
from openai_chat import OpenAI, ChatMessage

# 初始化客户端（自动从环境变量读取 OPENAI_API_KEY）
client = OpenAI()

# 或者显式指定 API key 和基础 URL
client = OpenAI(
    api_key="your-api-key",
    base_url="https://api.openai.com/v1",  # 或您的兼容 API 端点
    timeout=30
)

# 准备消息
messages = [
    ChatMessage(role="system", content="你是一个有用的助手。"),
    ChatMessage(role="user", content="你好，请介绍一下你自己。")
]

# 非流式调用
response = client.chat.create(
    model="gpt-3.5-turbo",
    messages=[msg.__dict__ for msg in messages],
    stream=False
)

print(response.text)
```

流式响应

```python
# 流式调用
stream = client.chat.create(
    model="gpt-3.5-turbo",
    messages=[msg.__dict__ for msg in messages],
    stream=True
)

for chunk in stream:
    print(chunk, end="", flush=True)
print()  # 换行
```

使用字典格式的消息

```python
messages = [
    {"role": "system", "content": "你是一个有用的助手。"},
    {"role": "user", "content": "请写一个简单的 Python 函数。"}
]

response = client.chat.create(
    model="gpt-3.5-turbo",
    messages=messages,
    temperature=0.7,
    max_tokens=500
)

print(response.text)
```

高级配置

自定义请求参数

```python
response = client.chat.create(
    model="gpt-3.5-turbo",
    messages=messages,
    temperature=0.8,        # 控制随机性
    max_tokens=1000,        # 最大生成长度
    top_p=0.9,             # 核采样参数
    presence_penalty=0.1,   # 话题新鲜度
    frequency_penalty=0.1   # 重复惩罚
)
```

错误处理

```python
from openai_chat import APIError

try:
    response = client.chat.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
except APIError as e:
    print(f"API 调用失败: {e}")
except Exception as e:
    print(f"其他错误: {e}")
```

环境变量

默认情况下，客户端会从环境变量中读取 API Key：

```bash
export OPENAI_API_KEY="your-api-key-here"
```

API 参考

OpenAI 类

主客户端类。

参数：

· api_key: API 密钥（可选，默认从环境变量读取）
· base_url: API 基础 URL（默认: "https://api.openai.com"）
· timeout: 请求超时时间（默认: 30 秒）

ChatResource.create() 方法

创建聊天补全。

参数：

· model: 模型名称（如 "gpt-3.5-turbo"）
· messages: 消息列表
· stream: 是否使用流式响应
· **kwargs: 其他 OpenAI API 参数

返回：

· 非流式：ChatResponse 对象
· 流式：生成器，产出内容片段

ChatResponse 类

响应数据类。

属性：

· text: 响应文本内容
· raw: 原始 API 响应数据

兼容性

这个客户端设计为与 OpenAI API 兼容，也可以用于其他提供兼容 API 的 LLM 服务，如：

· OpenAI API
· 其他兼容 OpenAI API 的本地或云端服务

贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目。
