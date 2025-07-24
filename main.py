from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from fetchData.summarise_feed import give_text
from pipelines.pipeline import execute
from pipelines.video_generation_pipeline import generate_video_pipeline
from control.generate_random_text import gen_text
from utils import get_env_var

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class GenerateMinecraftRequest(BaseModel):
    mode: Optional[int] = 1
    text: Optional[str] = None
    voice_id: Optional[str] = "74f0f8d1b27147c4aa9c65f690a3ead3"
    font_path: Optional[str] = "fonts/font.ttf"
    title: Optional[str] = "You won't believe what just happened!"
    description: Optional[str] = "Stay updated with the latest news in just 30 seconds!"
    user_id: Optional[str] = None
    avatar_id: Optional[str] = "de90ffeec028414a90ad2d954dc85b41"
    audio_url: Optional[str] = None

class GenerateRandom(BaseModel):
    text: Optional[str] = None

@app.post("/generate-minecraft")
async def generate_minecraft(request: GenerateMinecraftRequest):
    try:
        text = request.text
        if request.mode != 0:
            text = give_text()
            
        execute(
            text=text,
            voice_id=request.voice_id,
            font_path=request.font_path,
            title=request.title,
            description=request.description,
            user_id=request.user_id
        )
        
        return {"status": "success", "message": "Video generated successfully!"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-heygen-video")
# generate_video_pipeline(user_id,mode=0, text=None,audio_url="output/speech.mp3",title="N/A",description="N/A",avatar_id="de90ffeec028414a90ad2d954dc85b41", voice_id="74f0f8d1b27147c4aa9c65f690a3ead3"):
async def generate_heygen_video_route(request: GenerateMinecraftRequest):
    try:
        text = request.text
        avatar_id = request.avatar_id
        voice_id = request.voice_id
        print(f"Avatar ID: {avatar_id}, Voice ID: {voice_id}")
        if request.user_id is None:
            raise HTTPException(status_code=400, detail="User ID is required")
        generate_video_pipeline(request.user_id,mode=0, text=text,audio_url=request.audio_url, title=request.title, description=request.description, avatar_id=request.avatar_id, voice_id=request.voice_id)
        return {"status": "success", "message": "Video generated successfully!"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/get_random_text")
async def get_random_text(request: GenerateRandom):
    try:
        if not request.text:
            raise HTTPException(status_code=400, detail="Text is required")
        text= request.text
        text = gen_text(text)
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/")
async def root():
    return {"message": "Video Generator API"}

if __name__ == "__main__":
    import uvicorn
    port= int(get_env_var("PORT"))
    uvicorn.run(app, host="0.0.0.0", port=port)