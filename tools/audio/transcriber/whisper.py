import logging
import os
import json
log = logging.getLogger(__name__)

def transcribe(file_path):
    if(not file_path):
        file_path = "D:/.workspace/ai/bounty/gb/chat-bot-marketplace-backend/agent/zh_prompt.wav"
    print("transcribe", file_path)
    filename = os.path.basename(file_path)
    file_dir = os.path.dirname(file_path)
    id = filename.split(".")[0]

    from faster_whisper import WhisperModel

    whisper_kwargs = {
        "model_size_or_path": "base",
        "device": "cpu",
        "compute_type": "int8",
        "download_root": "D:/.workspace/ai/bounty/gb/chat-bot-marketplace-backend/agent/cache/whisper/",
        "local_files_only": not "true",
    }

    log.debug(f"whisper_kwargs: {whisper_kwargs}")

    try:
        model = WhisperModel(**whisper_kwargs)
    except Exception:
        log.warning(
            "WhisperModel initialization failed, attempting download with local_files_only=False"
        )
        whisper_kwargs["local_files_only"] = False
        model = WhisperModel(**whisper_kwargs)

    segments, info = model.transcribe(file_path, beam_size=5)
    log.info(
        "Detected language '%s' with probability %f"
        % (info.language, info.language_probability)
    )

    transcript = "".join([segment.text for segment in list(segments)])

    data = {"text": transcript.strip()}

    # save the transcript to a json file
    transcript_file = f"{file_dir}/{id}.json"
    with open(transcript_file, "w") as f:
        json.dump(data, f)

    print(data)
    return data



# text = transcribe("D:/.workspace/ai/bounty/gb/chat-bot-marketplace-backend/agent/zh_prompt.wav")
# print(text)