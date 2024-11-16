from RealtimeSTT import AudioToTextRecorder
import asyncio, aiohttp
import websockets
import threading
import numpy as np
from scipy.signal import resample
import json
import sys, os, logging, traceback, base64
import requests
from collections import defaultdict
# from zhipuai import ZhipuAI

# from utils.config import Config
# from utils.common import Common
# from utils.logger import Configure_logger

# from utils.search_online import SEARCH_ONLINE
# from utils.audio_player import AUDIO_PLAYER


# 为每个客户端连接创建一个消息队列
text_message_queues = defaultdict(asyncio.Queue)
audio_message_queues = defaultdict(asyncio.Queue)

# 客户端列表
text_clients = {}
audio_clients = {}
client_threads = {}

my_logger = logging.getLogger("my_logger")


async def audio_process_message_queue(client_id):
    try:
        while True:
            message = await audio_message_queues[client_id].get()

            # 处理消息
            my_logger.info(f"audio Processing message from {client_id}: {message}")
    except asyncio.CancelledError:
        print(f"客户端 audio {client_id} 的任务被取消")
        raise  # 可以重新抛出异常，也可以进行清理操作
    except Exception as e:
        my_logger.error(f"Error processing message: {e}")

async def audio_websocket_handler(websocket, path, client_id):
    # my_logger.info(f"client_id={client_id}")
    # start_client_thread(client_id, websocket, stop_event)
    audio_clients[client_id] = websocket

    task = asyncio.create_task(audio_process_message_queue(client_id))  # 启动消息处理协程

    try:
        async for message in websocket:
            await audio_message_queues[client_id].put(message)
    except websockets.exceptions.ConnectionClosed as e:
        my_logger.info(f"Audio WebSocket connection closed: {client_id}, reason: {e.reason}")
    except Exception as e:
        my_logger.error(f"Error receiving audio message: {e}")
    finally:
        # 执行断开连接后的清理工作
        my_logger.info("Audio WebSocket connection closed")

        task.cancel()  # 请求取消任务

        try:
            await task  # 等待任务处理取消
        except asyncio.CancelledError:
            my_logger.info("audio_process_message_queue任务已经被取消")


import functools


def generate_unique_client_id():
    import uuid

    return str(uuid.uuid4())



client_id = generate_unique_client_id()  # 获取或生成客户端 ID
client_id2 = generate_unique_client_id()

partial_audio_handler = functools.partial(audio_websocket_handler, path='/', client_id=client_id2)


start_audio_server = websockets.serve(partial_audio_handler, "0.0.0.0", 9002)


asyncio.get_event_loop().run_until_complete(start_audio_server)

# asyncio.get_event_loop().run_until_complete(start_text_server)
# asyncio.get_event_loop().run_forever()