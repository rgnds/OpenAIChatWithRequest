# Minimal initial implementation of an OpenAI-like client using requests
# Structure: Client, Requestor, ChatResource, basic response parsing.

import os, json
import requests
from dataclasses import dataclass
from typing import Optional, Iterable, Generator, Any


class APIError(Exception):
    pass


class Requestor:
    def __init__(self, api_key: str, base_url: str, timeout: int = 30):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def request(self, method: str, path: str, *, json_data=None, stream=False):
        url = f"{self.base_url}{path}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            resp = requests.request(
                method,
                url,
                headers=headers,
                json=json_data,
                timeout=self.timeout,
                stream=stream,
            )
        except requests.RequestException as e:
            raise APIError(f"Network error: {e}") from e

        if not stream:
            if resp.status_code >= 400:
                raise APIError(f"API error {resp.status_code}: {resp.text}")
            return resp.json()
        else:
            # Stream chunks for server-sent style responses
            if resp.status_code >= 400:
                raise APIError(f"API error {resp.status_code}: {resp.text}")
            
            def stream_generator():
                for line in resp.iter_lines():
                    if not line:
                        continue
                    
                    decoded = line.decode("utf-8").strip()
                    
                    # 跳过空行
                    if not decoded:
                        continue
                    
                    # 处理 SSE 格式: "data: {...}"
                    if decoded.startswith("data: "):
                        data_str = decoded[6:]  # 移除 "data: " 前缀
                        # print("That's data: pattern!!")
                        # 跳过 [DONE] 标记
                        if data_str == "[DONE]":
                            break
                        
                        try:
                            parsed = json.loads(data_str)
                            choices = parsed.get("choices", [])
                            
                            if choices and "delta" in choices[0]:
                                delta = choices[0]["delta"]
                                if "content" in delta:
                                    yield delta["content"]
                        except json.JSONDecodeError:
                            continue
                    else:
                        # 尝试直接解析JSON
                        try:
                            parsed = json.loads(decoded)
                            choices = parsed.get("choices", [])
                            
                            if not choices:
                                continue
                            
                            # 流式格式：delta
                            if "delta" in choices[0]:
                                delta = choices[0]["delta"]
                                if "content" in delta:
                                    yield delta["content"]
                            # 非流式格式：message
                            elif "message" in choices[0]:
                                message = choices[0]["message"]
                                if "content" in message:
                                    yield message["content"]
                        except json.JSONDecodeError:
                            continue
    
            return stream_generator()


@dataclass
class ChatMessage:
    role: str
    content: str


@dataclass
class ChatResponse:
    text: str
    raw: Any


class ChatResource:
    def __init__(self, requestor: Requestor):
        self.requestor = requestor

    def create(
        self,
        model: str,
        messages: Iterable[dict],
        stream: bool = False,
        **kwargs,
    ) -> Any:
        json_data = {"model": model, "messages": list(messages), "stream": stream}
        json_data.update(kwargs)

        if not stream:
            data = self.requestor.request("POST", "/v1/chat/completions", json_data=json_data)
            text = data["choices"][0]["message"]["content"]
            return ChatResponse(text=text, raw=data)
        else:
            # Yield raw lines; user may parse themselves
            return self.requestor.request("POST", "/v1/chat/completions", json_data=json_data, stream=True)


class OpenAI:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.openai.com",
        timeout: int = 30,
    ):
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("API key not provided and OPENAI_API_KEY not set.")

        self.requestor = Requestor(api_key, base_url, timeout)
        self.chat = ChatResource(self.requestor)