from fish_audio_sdk import Session, TTSRequest, ReferenceAudio
from typing import Optional

session = Session("9ef8152fc4c74caa9491db0fd3a61aac")
base_url = "D:/.workspace/ai/bounty/gb/chat-bot-marketplace-backend/tools/audio/cache/"
from fastapi.responses import FileResponse
import os
def tts(text , file_path:Optional[str] = ""):
    mp3_path = base_url + file_path
    # Option 1: Using a reference_id
    with open(mp3_path, "wb") as f:
        for chunk in session.tts(TTSRequest(
                reference_id="02a052d64d274c15bee6265820031073",
                text=text
        )):
            f.write(chunk)

    print("完成了tts文件" ,  mp3_path)
    print("完成了tts文件" ,  os.path.exists(file_path))

    return mp3_path

    # Option 2: Using reference audio
    # with open("reference_audio.wav", "rb") as audio_file:
    #     with open("output2.mp3", "wb") as f:
    #         for chunk in session.tts(TTSRequest(
    #                 text=text,
    #                 references=[
    #                     ReferenceAudio(
    #                         audio=audio_file.read(),
    #                         text="Text in reference audio",
    #                     )
    #                 ]
    #         )):
    #             f.write(chunk)


