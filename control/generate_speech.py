import os
from utils import get_env_var
from fetchData.summarise_feed import give_text
from supabase import create_client, Client
from speech.polly import use_polly
import tempfile
import asyncio

async def generate_speech(text, voice_id,output_path="output/output1.mp3"):
    print("Generating now")
    audio_bytes = use_polly(text)
    loop = asyncio.get_running_loop()
    audio_bytes = await loop.run_in_executor(None, use_polly, text)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio_file:
        temp_audio_file.write(audio_bytes)
        temp_audio_path = temp_audio_file.name
    print("Audio saved at:", temp_audio_path)
    return temp_audio_path