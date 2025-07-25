import requests
import json
import sys
import os
from utils import get_env_var
import time
from heygen.generate_video_audio import generate
from heygen.generate_video_text import generate_video_text
from fetchData.summarise_feed import give_text
import aiohttp
import asyncio

async def generate_heygen_video(avatar_id,voice_id,a=0,text=None,input_path="output/output1.mp3"):
    HEYGEN_API_KEY = get_env_var("HEYGEN_API_KEY")
    if(a==1):
        video_id = generate(input_path=input_path,avatar_id=avatar_id)
    else:
        if text is None:
            text = await give_text()
        video_id = await generate_video_text(text=text, title="try",avatar_id=avatar_id, voice_id=voice_id)
    print("Video ID:", video_id)
    if not video_id:
        print("Video ID not returned.")
        return

    url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"
    headers = {
        "accept": "application/json",
        "x-api-key": HEYGEN_API_KEY
    }
    timeout=aiohttp.ClientTimeout(900)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        i=0
        while i <= 50:
            async with session.get(url, headers=headers) as res:
                result = await res.json()  # ✅ Await .json()
                status = result.get("data", {}).get("status")
                print("Current status:", status)

                if status == "completed":
                    video_url = result.get("data", {}).get("video_url")
                    print("Video URL:", video_url)
                    return video_url
                elif status == "failed":
                    print("Video generation failed.")
                    return "failed"

            await asyncio.sleep(5)  # ✅ Non-blocking sleep
            i += 1

        return "failed"