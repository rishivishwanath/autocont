import os
from utils import get_env_var
from fetchData.summarise_feed import give_text
from supabase import create_client, Client
from speech.polly import use_polly
import tempfile
import asyncio

async def generate_speech(text, voice_id,output_path="output/output1.mp3"):
    print("Generating now")
    audio_bytes = await asyncio.to_thread(use_polly,text)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio_file:
        temp_audio_file.write(audio_bytes)
        temp_audio_path = temp_audio_file.name
    print("Audio saved at:", temp_audio_path)
    return temp_audio_path
# cost of switching threads is greater than blocking write