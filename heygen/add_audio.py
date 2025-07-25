import subprocess
import aiohttp
import whisper
import os
import json
import tempfile
from moviepy import VideoFileClip, TextClip, CompositeVideoClip
import textwrap
from pathlib import Path
import sys
import requests
import uuid
sys.path.append(str((Path(__file__).resolve().parent.parent)))
from utils import get_env_var

async def download_to_temp(url, extension=None):
    """Download file from URL to temporary file."""
    try:
        print(f"Downloading: {url}")
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=30) as response:
                response.raise_for_status()
                content = await response.read()


        # Determine extension from URL or use provided extension
        if not extension:
            if 'mp3' in url.lower():
                extension = '.mp3'
            elif 'mp4' in url.lower():
                extension = '.mp4'
            else:
                extension = '.tmp'

        with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as tmp_file:
            tmp_file.write(content)
            print(f"Downloaded to: {tmp_file.name}")
            return tmp_file.name
            
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        raise

def merge_audio_video(video_path, audio_path, output_path="merged_output.mp4"):
    """
    Merges the input video and audio files into a single video file.
    Both video_path and audio_path should be local file paths, not URLs.
    """
    try:
        print(f"Merging video: {video_path}")
        print(f"Merging audio: {audio_path}")
        print(f"Output: {output_path}")
        
        # Verify input files exist
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        command = [
            'ffmpeg',
            '-y',  # Overwrite output file if it exists
            '-i', video_path,
            '-i', audio_path,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-map', '0:v:0',
            '-map', '1:a:0',
            '-shortest',
            output_path
        ]
        
        print(f"Running command: {' '.join(command)}")
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("Merge completed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e}")
        print(f"Command: {' '.join(e.cmd)}")
        print(f"Return code: {e.returncode}")
        if e.stdout:
            print(f"Stdout: {e.stdout}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        raise
    except Exception as e:
        print(f"Unexpected error in merge_audio_video: {e}")
        raise

def transcribe_audio(audio_path, request_id=None):
    """Transcribe audio file and store segments in temporary JSON file."""
    try:
        print("Loading Whisper model...")
        model = whisper.load_model("base")
        
        print(f"Transcribing audio: {audio_path}")
        result = model.transcribe(audio_path)

        # Create unique temporary file for storing segments
        # Use request_id if provided, otherwise generate a UUID
        if not request_id:
            request_id = str(uuid.uuid4())
        
        segments_temp_file = tempfile.NamedTemporaryFile(
            mode='w', 
            suffix=f'_segments_{request_id}.json', 
            delete=False
        )
        
        with segments_temp_file as tmp_file:
            segments_data = []
            print(f"Processing {len(result['segments'])} segments...")
            
            for i, segment in enumerate(result['segments'], start=1):
                entry = {
                    "index": i,
                    "start": format_timestamp(segment["start"]),
                    "end": format_timestamp(segment["end"]),
                    "text": segment["text"].strip()
                }
                segments_data.append(entry)
            
            # Write all segments to the temporary JSON file
            json.dump(segments_data, tmp_file, indent=2)
            print(f"Stored {len(segments_data)} segments in temporary file: {segments_temp_file.name}")
        
        print("Transcription completed and stored in temporary file.")
        return segments_temp_file.name
        
    except Exception as e:
        print(f"Error during transcription: {e}")
        raise

def format_timestamp(seconds):
    """
    Formats the timestamp in SRT format.
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"

def overlay_subtitles_styled(video_path, segments_file_path, output_path="styled_output.mp4", font_file="fonts/font.ttf"):
    """Add subtitles to video using segments from the specified file."""
    # Load video
    clip = VideoFileClip(video_path)
    
    # Read segments from temporary JSON file
    if not os.path.exists(segments_file_path):
        raise FileNotFoundError(f"Segments file not found: {segments_file_path}")
    
    with open(segments_file_path, 'r') as f:
        segments = json.load(f)

    text_clips = []
    for seg in segments:
        start = parse_srt_time(seg["start"])
        end = parse_srt_time(seg["end"])
        text = seg["text"]
        print(text)
        # Wrap text manually (approx 25 characters per line for better readability)
        wrapped_lines = textwrap.wrap(text, width=20)
        total_lines = len(wrapped_lines)
        print(wrapped_lines)
        for i, line in enumerate(wrapped_lines):
            try:
                txt_clip = TextClip(
                    text=line,
                    font=font_file,
                    font_size=35,
                    color='white',
                    stroke_color='black',
                    stroke_width=5,
                    method='caption',
                    size=(clip.w, None)  # Set width to match the video width; height will be auto-calculated
                ).with_position(('center', clip.h - (clip.h*0.5) - (total_lines - i - 1) * 50)) \
                .with_start(start).with_duration(end - start)                
                text_clips.append(txt_clip)

            except Exception as e2:
                print(f"Failed to create fallback text clip: {e2}")
                continue

    # Overlay all text clips
    if text_clips:
        final = CompositeVideoClip([clip] + text_clips)
    else:
        print("No text clips created, using original video")
        final = clip
        
    final.write_videofile(output_path, codec="libx264", audio_codec="aac")

def parse_srt_time(srt_time):
    """Convert 'HH:MM:SS,mmm' to seconds (float)."""
    h, m, rest = srt_time.split(":")
    s, ms = rest.split(",")
    return int(h)*3600 + int(m)*60 + int(s) + int(ms)/1000.0

def cleanup_temp_files(*file_paths):
    """Clean up temporary files."""
    for file_path in file_paths:
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                print(f"Cleaned up: {file_path}")
        except Exception as e:
            print(f"Warning: Could not remove {file_path}: {e}")

async def add_audio_pipeline(video_url, audio_url, output_video_path="output.mp4", font_path="fonts/font.ttf", request_id=None):
    """
    Main pipeline function that downloads URLs to local files before processing.
    Each request gets unique temporary files using request_id.
    """
    # Generate unique request ID if not provided
    if not request_id:
        request_id = str(uuid.uuid4())
    
    print(f"Processing request: {request_id}")
    
    video_temp_path = None
    audio_temp_path = None
    segments_temp_file = None
    merged_video_path = f"temp_merged_video_{request_id}.mp4"
    
    try:
        # Download both video and audio to local temporary files
        print("Downloading video and audio files...")
        video_temp_path = await download_to_temp(video_url, '.mp4')
        audio_temp_path = audio_url
        
        # Merge video and audio using local file paths
        merge_audio_video(video_temp_path, audio_temp_path, merged_video_path)
        
        # Transcribe audio and get the segments file path
        segments_temp_file = transcribe_audio(audio_temp_path, request_id)
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_video_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Add subtitles using the segments file
        overlay_subtitles_styled(merged_video_path, segments_temp_file, output_path=output_video_path, font_file=font_path)
        
        print(f"Pipeline completed successfully! Output: {output_video_path}")
        
    except Exception as e:
        print(f"Pipeline failed: {e}")
        raise
    finally:
        # Clean up all temporary files
        cleanup_temp_files(video_temp_path, audio_temp_path, merged_video_path, segments_temp_file)