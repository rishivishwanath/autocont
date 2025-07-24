import requests
import json
import sys
import os
from control.generate_video import generate_heygen_video
import tempfile
from supabase import create_client, Client
import subprocess
from upload.upload_video import upload_video

def download_to_temp(url, extension=None):
    """Download file from URL to temporary file."""
    try:
        print(f"Downloading: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # Determine extension from URL or use provided extension
        if not extension:
            if 'mp3' in url.lower():
                extension = '.mp3'
            elif 'mp4' in url.lower():
                extension = '.mp4'
            else:
                extension = '.tmp'

        with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as tmp_file:
            tmp_file.write(response.content)
            print(f"Downloaded to: {tmp_file.name}")
            return tmp_file.name
            
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        raise

def cleanup_temp_files(*file_paths):
    """Clean up temporary files."""
    for file_path in file_paths:
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                print(f"Cleaned up: {file_path}")
        except Exception as e:
            print(f"Warning: Could not remove {file_path}: {e}")

def generate_video_pipeline(user_id,mode=0, text=None,audio_url="output/speech.mp3",title="N/A",description="N/A",avatar_id="de90ffeec028414a90ad2d954dc85b41", voice_id="74f0f8d1b27147c4aa9c65f690a3ead3"):
    if mode == 0:
        result=generate_heygen_video(a=0, text=text,avatar_id=avatar_id, voice_id=voice_id)
    elif mode == 1:
        audio_temp=download_to_temp(audio_url, extension=".mp3")
        result=generate_heygen_video(a=1, input_path=audio_temp, avatar_id=avatar_id, voice_id=voice_id)
    if result != "failed":
        output_file=download_to_temp(result, extension=".mp4")
    upload_video(output_file, title=title, description=description,user_id=user_id)
    cleanup_temp_files(output_file, audio_temp if mode == 1 else None)

