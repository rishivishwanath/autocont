from supabase import create_client, Client
from pathlib import Path
import sys
sys.path.append(str((Path(__file__).resolve().parent.parent)))
from control.generate_speech import generate_speech
from utils import get_env_var
import random
from heygen.add_audio import add_audio_pipeline
from upload.upload_video import upload_video
import asyncio

async def get_random_video_url():
    url=get_env_var("SUPABASE_URL")
    key=get_env_var("SUPABASE_KEY")
    supabase: Client = create_client(url, key)
    random_number = random.randint(1, 15)

    def get_url():
        return supabase.storage \
            .from_("background") \
            .get_public_url(f"output_{random_number}.mp4")

    video_link = await asyncio.to_thread(get_url)
    return video_link

async def background_video_pipeline(text=None, 
            voice_id="JBFqnCBsd6RMkjVDRZzb",
            font_path="fonts/font.ttf",
            title="You won't believe what just happened!",
            description="Stay updated with the latest news in just 30 seconds!",user_id=None):
    print("Generating speech...")
        # N2lVS1w4EtoT3dr4eOWO
        # ThT5KcBeYPX3keUQqHPh dorothy
    audio_link=await generate_speech(text, voice_id)
    print("Speech generated successfully.")
    print("Audio link:", audio_link)
    video_link=await get_random_video_url()
    print(video_link)
    await add_audio_pipeline(video_link,audio_link, output_video_path="output/output.mp4", font_path=font_path)
    await upload_video(
        file_path="output/output.mp4",
        title=title,
        description=description,user_id=user_id
    )