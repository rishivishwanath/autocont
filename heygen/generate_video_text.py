import requests
import json
from utils import get_env_var
import time


def generate_video_text(text,title="try",avatar_id="de90ffeec028414a90ad2d954dc85b41", voice_id="74f0f8d1b27147c4aa9c65f690a3ead3"):
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
    response=requests.post(url,headers=headers,data=json.dumps(payload))
    if response.status_code==200:
        result = response.json()
        print(result)
        print(f"Video request successful. Video ID: {result.get('data')['video_id']}")
        return (result.get('data')['video_id'])
    else:
        print("Error creating video:", response.status_code, response.text)
        return None
