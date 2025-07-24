import os
from utils import get_env_var
from backend.fetchData.summarise_feed import give_text
from supabase import create_client, Client
from speech.polly import use_polly
import tempfile
def generate_speech(text, voice_id,output_path="output/output1.mp3"):
    print("Generating now")
    url = get_env_var("SUPABASE_URL")
    key = get_env_var("SUPABASE_KEY")
    supabase= create_client(url, key)
    print(url,key)

    print("Generating now")
    audio_bytes = use_polly(text)
    print("Generating now")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio_file:
        temp_audio_file.write(audio_bytes)
        temp_audio_path = temp_audio_file.name  # Get the path to the temp file
    print("Audio saved at:", temp_audio_path)
    response =temp_audio_path
    return response
