import os
import json
import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from utils import get_env_var
from supabase import create_client, Client

url=get_env_var("SUPABASE_URL")
key=get_env_var("SUPABASE_KEY")
supabase: Client = create_client(url, key)
# File path of the video
VIDEO_FILE = "output/output.mp4"

def get_credentials(CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN):
    creds_data = {
        "token": "",
        "refresh_token": REFRESH_TOKEN,
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scopes": ["https://www.googleapis.com/auth/youtube.upload"]
    }

    creds = Credentials.from_authorized_user_info(info=creds_data)
    if not creds.valid or creds.expired:
        request = Request()
        creds.refresh(request)
    return creds

def upload_video(file_path, title, description,user_id, tags=None):
    values= (
    supabase.table("user_api_keys")
    .select("*")
    .eq("id",user_id)
    .execute())
# "201a4aff-111e-4a65-91ef-532c6a4171cc"
    print(values.data[0]["YOUTUBE_CLIENT_ID"],values.data[0]["YOUTUBE_CLIENT_SECRET"], values.data[0]["YOUTUBE_REFRESH_TOKEN"])
    creds = get_credentials(values.data[0]["YOUTUBE_CLIENT_ID"],values.data[0]["YOUTUBE_CLIENT_SECRET"], values.data[0]["YOUTUBE_REFRESH_TOKEN"])
    youtube = build("youtube", "v3", credentials=creds)

    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": ["cybercrime", "conspiracy", "unsolved mystery", "cult",
    "espionage", "paranormal", "forbidden", "secret society", "ritual",
    "black market", "scandal", "hidden truth", "classified", "covert operation",
    "did you know", "bizarre", "unbelievable", "shocking", "unexplained"],
            "categoryId": "22"
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(file_path, resumable=True)
    upload_request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media
    )

    response = upload_request.execute()
    print(f"[✅] Video uploaded successfully: https://youtube.com/watch?v={response['id']}")
    return "success"

