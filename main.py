import os

from fastapi.responses import RedirectResponse
import uvicorn

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from auth.cors_middleware import AuthCORSMiddleWare

from auth.middleware import AuthMiddleWare
from petercat_utils import get_env_variable


# Import fastapi routers
# from auth import router as auth_router
from bot import router as bot_router
from chat import router as chat_router
# from rag import router as rag_router
# from task import router as task_router
# from github_app import router as github_app_router
# from aws import router as aws_router
# from user import router as user_router

AUTH0_DOMAIN = get_env_variable("AUTH0_DOMAIN")
API_AUDIENCE = get_env_variable("API_IDENTIFIER")
CLIENT_ID = get_env_variable("AUTH0_CLIENT_ID")
API_URL = get_env_variable("API_URL")
WEB_URL = get_env_variable("WEB_URL")
ENVRIMENT = get_env_variable("PETERCAT_ENV", "development")
CALLBACK_URL = f"{API_URL}/api/auth/callback"

is_dev = bool(get_env_variable("IS_DEV"))
session_secret_key = get_env_variable("FASTAPI_SECRET_KEY")
cors_origins_whitelist = get_env_variable("CORS_ORIGIN_WHITELIST") or None

app = FastAPI(title="Petercat Server", version="1.0", description="Petercat.ai APIs")

app.add_middleware(AuthMiddleWare)

app.add_middleware(
    SessionMiddleware,
    secret_key=session_secret_key
)

cors_origins = (
    ["*"] if cors_origins_whitelist is None else cors_origins_whitelist.split(",")
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers="*",
)

app.add_middleware(AuthCORSMiddleWare)

# app.include_router(rag_router.router)
app.include_router(bot_router.router)
# app.include_router(auth_router.router)
app.include_router(chat_router.router)
# app.include_router(task_router.router)
# app.include_router(github_app_router.router)
# app.include_router(aws_router.router)
# app.include_router(user_router.router)


@app.get("/")
def home_page():
    return RedirectResponse(url=WEB_URL)

@app.get("/api/health_checker")
def health_checker():
    return {
        "ENVRIMENT": ENVRIMENT,
        "API_URL": API_URL,
        "WEB_URL": WEB_URL,
        "CALLBACK_URL": CALLBACK_URL,
    }

from langchain_openai import ChatOpenAI
from core.models.characters import get_demo_character
from langchain_core.messages import SystemMessage, HumanMessage



@app.get("/mock/chat")
async def mock_chat():
    tmp = get_demo_character()
    prompt = tmp["story_string"]
    openai_base_url = "https://api.gptsapi.net/v1"  # 确保 URL 是正确的
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, base_url=openai_base_url,
                     api_key="sk-8Jd9032695209fe692c59c7f5fedb690420d671c0adVhOx2")
    systemPrompt = SystemMessage(content=prompt)
    messages = [systemPrompt] + [HumanMessage(content="Hey there! How's it going?")]

    # 假设 llm.stream 返回一个生成器，产生字符串块
    stream_generator = llm.stream(messages)

    async def event_stream():
        for chunk in stream_generator:
            if chunk:  # 确保 chunk 不是 None
                # SSE 格式的数据包括一个事件和一个数据字段，数据字段包含实际的消息
                yield f"data: {chunk}\n\n".encode('utf-8')

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# generate tts
import io
import os
import sys
import zipfile

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi import FastAPI, Request, Response, Form, File, UploadFile, BackgroundTasks

from fastapi.responses import StreamingResponse

from tools.audio.transcriber.whisper import transcribe
from tools.audio.tts.fish import tts
from fastapi import FastAPI, File, UploadFile
from agent import qa_chat
from fastapi.responses import FileResponse
from tools.audio.tts.cosyvoice import tts_cosyvoice

import time
@app.post("/asr-chat")
async def asr_chat(
    audio_file: UploadFile = File(...)
):
    file_path = f"uploads/{audio_file.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(await audio_file.read())
    # stt
    t1 = time.time()
    res = transcribe(file_path)
    query = res["text"]
    print(f"ASR耗时: {time.time() - t1} seconds")
    if(not query):
        print("人物对话识别失败")
    # llm

    t1 = time.time()
    llm_response = qa_chat.chat_ollama(query)
    print(f"llm耗时: {time.time() - t1} seconds")
    # tts
    t1 = time.time()
    audio_response = tts_cosyvoice(llm_response)
    print(f"tts耗时: {time.time() - t1} seconds")
    return FileResponse(path=audio_response, media_type="audio/wav")


from typing import Optional
@app.get("/asr-stream-chat")
@app.post("/asr-stream-chat")
async def asr_stream_chat(
    audio_file: Optional[UploadFile] = File(...)
):
    if not audio_file:
        return FileResponse()
    file_path = f"uploads/{audio_file.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(await audio_file.read())

    # stt
    t1 = time.time()
    res = transcribe(file_path)
    query = res["text"]
    print(f"ASR耗时: {time.time() - t1} seconds")
    if(not query):
        print("人物对话识别失败")
    # llm
    llm_response = qa_chat.chat_ollama_stream(query)

    async def event_stream():
        sentence = ""
        index = 0
        for chunk in llm_response:
            if chunk:  # 确保 chunk 不是 None
                if chunk.content not in (".","。","?","？","!","！"):
                    sentence += chunk.content
                else:
                    t1 = time.time()
                    audio_response = tts_cosyvoice(sentence , index)
                    sentence = ""
                    index += 1
                    print(f"tts耗时: {time.time() - t1} seconds")

                    yield f"data: {audio_response}\n\n".encode('utf-8')

    # 设置 SSE 响应头
    headers = {"Content-Type": "text/event-stream"}
    return StreamingResponse(event_stream(), media_type=None, headers=headers)


if __name__ == "__main__":
    if is_dev:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=int(os.environ.get("PORT", "8080")),
            reload=True,
        )
    else:
        uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
