#!/usr/bin/env python3
"""
Drone Nature (Pexels) + Deep House (MusicGen) → Final Video
Robust version: uses Pexels REST API (no pexelsPy dependency).

Usage:
  python drone_deep_house_creator.py
"""

import os
import time
import random
import warnings
import requests
import numpy as np
from typing import List, Tuple, Optional

from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
from moviepy.audio.fx.all import audio_loop

import torch
from audiocraft.models import MusicGen
import scipy.io.wavfile as wavfile

warnings.filterwarnings("ignore")

# ================== CONFIG ==================
# Prefer env var; fallback to inline (you pasted a key—consider using env for safety).
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "LphQjazFwXgtWDFWXXeUGf2JGQXE4WHFiPnTLF9xeo1XnHQn2W3QFNbw")

SEARCH_QUERY = "4k aerial drone nature"   # better hit-rate for 4K
RESULTS_PER_PAGE = 30                      # search more to find true 4K
VIDEO_COUNT = 2                            # 1 or 2 clips to concatenate
TARGET_DURATION_SECONDS = 60               # exact length (video+audio trimmed/looped)
OUTPUT_FILENAME = "drone_deep_house_final.mp4"
FORCE_OUTPUT_FPS = 30                      # wide compatibility

# Deep House prompt (DJ-style)
MUSIC_PROMPT = (
    "DJ-style deep house track with hypnotic bassline, punchy kick, crisp hats, "
    "atmospheric pads, subtle chords, warm analog feel, 128 bpm, club-ready, clean mixdown"
)
MUSICGEN_MODEL_ID = "facebook/musicgen-small"

SEED: Optional[int] = 128  # None for full randomness


# ================== UTILS ==================
def _rng_seed(seed: Optional[int]):
    if seed is None:
        return
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

def human_size(n: int) -> str:
    u = ["B","KB","MB","GB","TB"]
    i = 0
    v = float(n)
    while v >= 1024 and i < len(u)-1:
        v /= 1024.0
        i += 1
    return f"{v:.1f}{u[i]}"


# ================== PEXELS REST ==================
def search_pexels_videos(api_key: str, query: str, per_page: int = 15, page: int = 1) -> dict:
    """Call Pexels Videos Search REST API."""
    url = "https://api.pexels.com/videos/search"
    headers = {"Authorization": api_key}
    params = {"query": query, "per_page": per_page, "page": page}
    r = requests.get(url, headers=headers, params=params, timeout=60)
    r.raise_for_status()
    return r.json()

def select_best_files(items: List[dict], want: int) -> List[dict]:
    """
    For each video, pick the highest-res file. Rank: 4K first, then by area.
    Returns selections with url/width/height/fps/author/video_id.
    """
    candidates = []
    for v in items:
        files = v.get("video_files", []) or []
        if not files:
            continue
        best = max(files, key=lambda f: (f.get("width") or 0) * (f.get("height") or 0))
        candidates.append({
            "video_id": v.get("id"),
            "author"  : (v.get("user") or {}).get("name", "Unknown"),
            "duration": v.get("duration"),
            "width"   : best.get("width"),
            "height"  : best.get("height"),
            "fps"     : best.get("fps") or FORCE_OUTPUT_FPS,
            "url"     : best.get("link"),
            "area"    : (best.get("width") or 0) * (best.get("height") or 0),
            "is_4k"   : (best.get("width") or 0) >= 3840 and (best.get("height") or 0) >= 2160,
        })
    candidates.sort(key=lambda x: (not x["is_4k"], -x["area"]))
    return candidates[:max(1, min(want, len(candidates)))]

def download_stream(url: str, out_path: str) -> str:
    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length") or 0)
        got = 0
        t0 = time.time()
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024*256):
                if not chunk:
                    continue
                f.write(chunk)
                got += len(chunk)
                if total:
                    pct = 100.0 * got / total
                    rate = got / max(time.time() - t0, 1e-6)
                    print(f"\r {os.path.basename(out_path)}  {pct:5.1f}%  "
                          f"{human_size(got)}/{human_size(total)}  {human_size(int(rate))}/s",
                          end="")
        print("")
    return out_path

def get_pexels_clips(api_key: str, query: str, per_page: int, count: int) -> List[str]:
    print(f" Searching Pexels: '{query}'")
    data = search_pexels_videos(api_key, query, per_page=per_page, page=1)
    items = data.get("videos", []) or []
    if not items:
        raise RuntimeError("No videos returned from Pexels.")
    picks = select_best_files(items, want=count)
    if not picks:
        raise RuntimeError("No suitable video files found.")

    paths = []
    for i, p in enumerate(picks, 1):
        name = f"pexels_{p['video_id']}_{p['width']}x{p['height']}_{i}.mp4"
        print(f" Selected: {p['width']}x{p['height']} (4K={p['is_4k']}) | Author: {p['author']} | FPS: {p['fps']}")
        download_stream(p["url"], name)
        paths.append(name)
    return paths


# ================== MUSICGEN ==================
def generate_deep_house(prompt: str, duration: int, model_id: str) -> Tuple[str, int]:
    print(f" Generating Deep House ({duration}s)\n   Prompt: {prompt}")
    _rng_seed(SEED)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f" Loading MusicGen '{model_id}' on {device} ...")
    model = MusicGen.get_pretrained(model_id, device=device)

    model.set_generation_params(
        duration=duration,
        use_sampling=True,
        top_k=250,
        top_p=0.0,
        temperature=1.0,
        cfg_coef=3.0,
    )

    with torch.no_grad():
        wav = model.generate([prompt])

    audio = wav[0].detach().cpu().numpy()  # (channels, samples)
    sr = model.sample_rate

    # Peak normalize to avoid clipping
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio / peak * 0.98

    out_wav = "generated_deep_house.wav"
    wavfile.write(out_wav, sr, (audio.T).astype(np.float32))  # (nsamples, nchannels)
    print(f" Music generated → {out_wav} @ {sr} Hz")
    return out_wav, sr


# ================== EDIT / COMPOSE ==================
def build_video_timeline(paths: List[str], target_duration: int) -> VideoFileClip:
    clips = []
    for p in paths:
        c = VideoFileClip(p)
        if c.audio is not None:
            c = c.without_audio()
        clips.append(c)

    if len(clips) == 1:
        base = clips[0]
    else:
        base = concatenate_videoclips(clips, method="compose")

    if base.duration < target_duration:
        base = base.loop(duration=target_duration)
        print(f" Looped video to {target_duration}s")
    elif base.duration > target_duration:
        base = base.subclip(0, target_duration)
        print(f" Trimmed video to {target_duration}s")
    return base

def build_audio_track(path: str, target_duration: int) -> AudioFileClip:
    a = AudioFileClip(path)
    if a.duration < target_duration:
        a = a.fx(audio_loop, duration=target_duration)
        print(f" Looped audio to {target_duration}s")
    elif a.duration > target_duration:
        a = a.subclip(0, target_duration)
        print(f" Trimmed audio to {target_duration}s")
    return a

def choose_output_size(paths: List[str]) -> Tuple[int, int]:
    sizes = []
    for p in paths:
        with VideoFileClip(p) as c:
            sizes.append(tuple(c.size))
    # Prefer any 4K source
    for (w, h) in sizes:
        if w >= 3840 and h >= 2160:
            return (w, h)
    return sizes[0]  # otherwise first clip size

def mux(video: VideoFileClip, audio: AudioFileClip, out_path: str, fps: int, size: Tuple[int, int]):
    print(f" Rendering → {out_path}")
    final = video.set_audio(audio)
    if final.size != list(size):
        final = final.resize(newsize=size)
    final.write_videofile(
        out_path,
        codec="libx264",
        audio_codec="aac",
        fps=fps,
        bitrate="5000k" if size[0] < 3840 else "16000k",
        threads=max(os.cpu_count() or 4, 4),
        temp_audiofile="__temp_audio.m4a",
        remove_temp=True,
        verbose=False,
        logger=None
    )
    final.close()
    print(f" Final video created: {out_path}")


# ================== MAIN ==================
def main():
    print("="*70)
    print(" Drone Nature + Deep House (DJ) Video Creator — Pexels REST")
    print("="*70)

    if not PEXELS_API_KEY or len(PEXELS_API_KEY.strip()) < 20:
        print(" Missing/invalid PEXELS_API_KEY. Set it in env or inline in this file.")
        return

    # 1) Download 4K drone videos (1–2)
    try:
        video_paths = get_pexels_clips(
            api_key=PEXELS_API_KEY.strip(),
            query=SEARCH_QUERY,
            per_page=RESULTS_PER_PAGE,
            count=max(1, min(2, VIDEO_COUNT)),
        )
    except Exception as e:
        print(f" Video fetch failed: {e}")
        return

    # 2) Generate Deep House audio
    try:
        audio_path, _ = generate_deep_house(MUSIC_PROMPT, TARGET_DURATION_SECONDS, MUSICGEN_MODEL_ID)
    except Exception as e:
        print(f" Music generation failed: {e}")
        return

    # 3) Build timelines
    try:
        v = build_video_timeline(video_paths, TARGET_DURATION_SECONDS)
        a = build_audio_track(audio_path, TARGET_DURATION_SECONDS)
    except Exception as e:
        print(f" Timeline build failed: {e}")
        return

    # 4) Decide size and export
    try:
        size = choose_output_size(video_paths)
        mux(v, a, OUTPUT_FILENAME, fps=FORCE_OUTPUT_FPS, size=size)
    except Exception as e:
        print(f" Render failed: {e}")
        return
    finally:
        try: v.close()
        except: pass
        try: a.close()
        except: pass

    print("\n DONE!")
    print(f" {OUTPUT_FILENAME}")
    print(f" {TARGET_DURATION_SECONDS}s |  Deep House |  {len(video_paths)} clip(s)")

    # Optional cleanup (remove downloaded sources and generated wav)
    try:
        for p in video_paths:
            if os.path.exists(p): os.remove(p)
        if os.path.exists(audio_path): os.remove(audio_path)
        print(" Cleaned temp files.")
    except:
        pass


if __name__ == "__main__":
    main()
