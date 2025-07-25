ELEVENLABS_API_KEY=
HEYGEN_API_KEY=
NEWS_API_KEY=
PIPFEED_API_KEY=
SUPABASE_URL=
SUPABASE_KEY=
GOOGLE_API_KEY=
YOUTUBE_CLIENT_ID=
YOUTUBE_CLIENT_SECRET=
YOUTUBE_REFRESH_TOKEN=
AMAZON_ACCESS_KEY=
AMAZON_SECRET_KEY=
PORT=8081


/generate-minecraft(for non avatar mode)
mode (0=text must be passes,1 text is automatically generated)
text=text,
voice_id=request.voice_id,
font_path=request.font_path(fonts/font.ttf),
title=request.title,
description=request.description,
user_id=request.user_id


/generate-heygen-video(for avatar mode)
generate_video_pipeline(user_id,mode=0, text=None,audio_url="output/speech.mp3",title="N/A",description="N/A",avatar_id="de90ffeec028414a90ad2d954dc85b41", voice_id="74f0f8d1b27147c4aa9c65f690a3ead3"):
mode=0=to pass text
mode=1= should be able to upload audio and pass that
avatar_id and voice_id are already fetched make sure to pass that

/get_random_text
text
not compulsory to pass anything


asyncio.to_thread when calling sync
asyncio.create_task when calling async