import requests
import json
from utils import get_env_var
import time
import aiohttp

async def generate_video_text(text,title="try",avatar_id="de90ffeec028414a90ad2d954dc85b41", voice_id="74f0f8d1b27147c4aa9c65f690a3ead3"):
    HEYGEN_API_KEY = get_env_var("HEYGEN_API_KEY")
    url = "https://api.heygen.com/v2/video/generate"
    headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "x-api-key": HEYGEN_API_KEY
    }
    payload = {
        "title": title,
        "caption": False,
         "dimension": {
            "width": 720,
            "height": 1080
        },
        "video_inputs": [
            {
                "character": {
                    "type": "avatar",
                    "avatar_id":avatar_id,
                    "scale": 1.0,
                    "avatar_style": "normal",
                    "offset": {
                        "x": 0.0,
                        "y": 0.0,
                    }
                },
                "voice": {
                    "type": "text",
                    "voice_id":voice_id,
                    "input_text": text,
                    "emotion": "Excited",
                },
                "background": {
                    "type": "color",
                    "value": "#f6f6fc"
                }
            }
        ]
    }
    timeout=aiohttp.ClientTimeout(900)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(url, headers=headers, data=json.dumps(payload)) as res:
            res.raise_for_status()
            response = await res.json()  

    if res.status == 200:
        print(response)
        print(f"Video request successful. Video ID: {response.get('data', {}).get('video_id')}")
        return response.get('data', {}).get('video_id')
    else:
        print("Error creating video:", res.status, await res.text())
        return None
