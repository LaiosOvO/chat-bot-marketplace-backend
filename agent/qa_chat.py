from typing import AsyncIterator, Dict, Optional
from github import Auth
from agent.base import AgentBuilder
from agent.bot import Bot

from petercat_utils.data_class import ChatData

from agent.tools import issue, pull_request, auth, sourcecode, knowledge, git_info


import os
os.environ["http_proxy"] = "http://127.0.0.1:10809"
os.environ["https_proxy"] = "http://127.0.0.1:10809"

def get_tools(bot: Bot, auth_token: Optional[Auth.Token]):
    login_tools = auth.factory(token=auth_token)
    issue_tools = issue.factory(token=auth_token)
    pull_request_tools = pull_request.factory(token=auth_token)
    sourcecode_tools = sourcecode.factory(token=auth_token)

    return {
        "check_login": login_tools["check_login"],
        "search_knowledge": knowledge.factory(bot_id=bot.id),
        "create_issue": issue_tools["create_issue"],
        "get_issues": issue_tools["get_issues"],
        "get_file_content": pull_request_tools["get_file_content"],
        "create_review_comment": pull_request_tools["create_review_comment"],
        "create_pr_summary": pull_request_tools["create_pr_summary"],
        "search_issues": issue_tools["search_issues"],
        "search_code": sourcecode_tools["search_code"],
        "search_repo": git_info.search_repo,
    }


def agent_stream_chat(
    input_data: ChatData, auth_token: Auth.Token, bot: Bot
) -> AsyncIterator[Dict]:
    agent = AgentBuilder(
        chat_model=bot.llm,
        prompt=bot.prompt,
        tools=get_tools(bot=bot, auth_token=auth_token),
    )
    return agent.run_stream_chat(input_data)


def agent_chat(
    input_data: ChatData, auth_token: Auth.Token, bot: Bot
) -> AsyncIterator[str]:

    prompt = bot.prompt

    if input_data.prompt is not None:
        prompt = f"{prompt}\n\n{input_data.prompt}"

    agent = AgentBuilder(
        chat_model=bot.llm,
        prompt=prompt,
        tools=get_tools(bot, auth_token=auth_token),
    )

    return agent.run_chat(input_data)

from langchain_ollama import ChatOllama

def chat_ollama(query):
    llm = ChatOllama(base_url="192.168.1.168:11434",model="qwen2.5:latest")
    res = llm.invoke(query)

    print(res)
    print(res.content)
    return res.content

from tools.audio.tts.cosyvoice import tts_cosyvoice
from playsound import playsound

def chat_ollama_stream(query):
    llm = ChatOllama(base_url="192.168.1.168:11434",model="qwen2.5:latest")
    return llm.stream(query)


def handle_stream_chat(res):
    sentence = ""
    number = 0
    for chunk in res:
        if chunk:
            if chunk.content not in (".", "。", "?", "？", "!", "！"):
                sentence += chunk.content
            else:
                print(sentence)
                audio_response = tts_cosyvoice(sentence,number)
                # playsound(audio_response)
                sentence = ""
                number = number + 1


if __name__ == "__main__":
    res = chat_ollama_stream("你好你是谁")
    handle_stream_chat(res)
