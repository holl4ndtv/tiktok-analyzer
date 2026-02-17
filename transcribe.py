#!/usr/bin/env python3
"""
Video Analyzer - Transcription Engine
Works with TikTok, YouTube, Instagram, Twitter, and 1000+ sites via yt-dlp
"""

import sys
import os
import json
import tempfile
import subprocess
import hashlib
from pathlib import Path

SKILL_DIR = Path(__file__).parent
TRANSCRIPTS_DIR = SKILL_DIR / "transcripts"
TRANSCRIPTS_DIR.mkdir(exist_ok=True)


def get_video_id(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()[:12]


def download_audio(url: str, output_path: str) -> tuple[bool, str]:
    cmd = [
        "yt-dlp",
        "--extract-audio",
        "--audio-format", "mp3",
        "--audio-quality", "5",
        "--output", output_path,
        "--no-playlist",
        "--quiet",
        "--no-warnings",
        url
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        err = result.stderr.strip() or "Unknown error"
        if "private" in err.lower():
            return False, "Video is private or unavailable."
        if "not available" in err.lower() or "removed" in err.lower():
            return False, "Video has been removed or is unavailable."
        return False, f"Download failed: {err[:200]}"
    return True, ""


def transcribe_audio(audio_path: str) -> dict:
    try:
        from faster_whisper import WhisperModel
        model = WhisperModel("base", device="cpu", compute_type="int8")
        segments, info = model.transcribe(audio_path, beam_size=5)
        parts = [seg.text.strip() for seg in segments]
        return {
            "engine": "faster-whisper",
            "language": info.language,
            "transcript": " ".join(parts)
        }
    except ImportError:
        pass

    # Fallback: standard whisper
    try:
        import whisper
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        return {
            "engine": "whisper",
            "language": result.get("language", "unknown"),
            "transcript": result.get("text", "").strip()
        }
    except ImportError:
        pass

    return {"error": "No transcription engine found. Run: pip install faster-whisper"}


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: transcribe.py <URL>"}))
        sys.exit(1)

    url = sys.argv[1]
    video_id = get_video_id(url)
    cache_file = TRANSCRIPTS_DIR / f"{video_id}.json"

    # Check cache
    if cache_file.exists():
        with open(cache_file) as f:
            cached = json.load(f)
        cached["from_cache"] = True
        print(json.dumps(cached))
        return

    # Download
    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = os.path.join(tmpdir, "audio.mp3")
        ok, err = download_audio(url, audio_path)
        if not ok:
            print(json.dumps({"error": err}))
            sys.exit(1)

        result = transcribe_audio(audio_path)
        if "error" in result:
            print(json.dumps(result))
            sys.exit(1)

    result["url"] = url
    result["video_id"] = video_id
    result["from_cache"] = False
    print(json.dumps(result))


if __name__ == "__main__":
    main()
