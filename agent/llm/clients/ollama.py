import os
from typing import Any, List, Optional
from langchain_ollama import ChatOllama
from langchain_core.utils.function_calling import convert_to_openai_tool


from agent.llm import register_llm_client
from agent.llm.base import BaseLLMClient
from petercat_utils.data_class import MessageContent




@register_llm_client("ollama")
class ChatOllamaClient(BaseLLMClient):
    _client: ChatOllama

    def __init__(
        self,
        temperature: Optional[int] = 0.2,
        max_tokens: Optional[int] = 1500,
        streaming: Optional[bool] = False,
        api_key: Optional[str] = "",
    ):
        self._client = ChatOllama(
            base_url="http://192.168.1.168:11434",
            model_name="llama3.1:latest",
            temperature=temperature,
            streaming=streaming,
            max_tokens=max_tokens,
            stream_usage=True,
        )
        # self._client.get_lc_namespace()

    def get_client(self):
        return self._client

    def get_tools(self, tools: List[Any]):
        return [convert_to_openai_tool(tool) for tool in tools]

    def parse_content(self, content: List[MessageContent]):
        return content
        # return ChatOllama._convert_messages_to_ollama_messages(content)

