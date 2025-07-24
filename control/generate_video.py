import requests
import json
import sys
import os
from utils import get_env_var
import time
from heygen.generate_video_audio import generate
from heygen.generate_video_text import generate_video_text
from fetchData.summarise_feed import give_text

def generate_heygen_video(avatar_id,voice_id,a=0,text=None,input_path="output/output1.mp3"):
    HEYGEN_API_KEY = get_env_var("HEYGEN_API_KEY")
    if(a==1):
        video_id = generate(input_path=input_path,avatar_id=avatar_id)
    else:
        if text is None:
            text = give_text()
        video_id = generate_video_text(text=text, title="try",avatar_id=avatar_id, voice_id=voice_id)
    print("Video ID:", video_id)
    if not video_id:
        print("Video ID not returned.")
        return

    url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"
    headers = {
        "accept": "application/json",
        "x-api-key": HEYGEN_API_KEY
    }
    response = requests.get(url, headers=headers)
    result = response.json()
    status = result.get("data")['status']
    i=0
    while (status != "completed" and status != "failed"):
        response = requests.get(url, headers=headers)
        result = response.json()

        status = result.get("data")["status"]
        print("Current status:", status)
        if status == "completed":
            print("Video URL:", result.get("data")['video_url'])
            return result.get("data")['video_url']
        elif status == "failed":
            print("Video generation failed.")
            return "failed"

        time.sleep(5)
        if i>25:
            return "failed"