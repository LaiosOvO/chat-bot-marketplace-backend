import json
import wave
import pyaudio

import requests
from typing import Optional

def save_audio_from_response(url, data, output_file):
    """执行推理并保存音频"""
    try:
        response = requests.post(url, data=data)

        print(response)
        if response.status_code == 200:
            with open(output_file, "wb") as f:
                f.write(response.content)
            return output_file
        else:
            print(response.status_code)
    except Exception as e:
        print(e)

def play_wav_file(wav_file):
    # 打开WAV文件
    wf = wave.open(wav_file, 'rb')

    # 创建PyAudio对象
    p = pyaudio.PyAudio()

    # 打开音频流
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # 读取数据并播放
    data = wf.readframes(1024)
    while len(data) > 0:
        stream.write(data)
        data = wf.readframes(1024)

    # 停止和关闭音频流
    stream.stop_stream()
    stream.close()

    # 关闭PyAudio
    p.terminate()


def tts_cosyvoice(text,index:Optional[int] = None):
    base_url = "http://192.168.1.54:9233/clone_eq"
    data = {
        "reference_text": "都是有这个想法的，只不过现在是把我一直以来准备的东西，一直以来我的另外一面。放在桌子上而已，没有一个标签，要把我给关死吗？我觉得不用的，我不希望有一个字去标签自己。我觉得有不好的声音，也不一定是一件坏事。最不能乱的是自己听完let's make history.今晚一起创造历史。",
        "reference_audio": "data.wav",
        "text": f"{text}",
        "role": "男"
    }
    path = "cache/cosyvoice"
    if index is not None:
        path += str(index)

    file = save_audio_from_response(base_url,data,path+".wav")
    with open(file, 'rb') as f:
        return f.read()


