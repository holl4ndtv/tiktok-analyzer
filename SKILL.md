# Video Analyzer Skill

Analyze any video by dropping a URL. Works with TikTok, YouTube, Instagram, Twitter/X, and 1000+ other sites. Transcribes the audio and answers any question about the content.

---

## When to Use This Skill

Activate when the user:
- Shares a video URL (tiktok.com, youtube.com, instagram.com, twitter.com, x.com, etc.)
- Asks "what is this video about", "summarize this", "what are they teaching", "what's the hook", etc.
- Asks a question about a previously saved video

---

## Prerequisites Check

Before the first run, verify dependencies:

```bash
which ffmpeg && python3 -c "import faster_whisper; print('ok')" && python3 -c "import yt_dlp; print('ok')"
```

**If anything is missing:**

Mac/local:
```bash
brew install ffmpeg
pip install faster-whisper yt-dlp
```

Linux/VPS:
```bash
apt install -y ffmpeg
pip install faster-whisper yt-dlp
```

---

## Flow

### Step 1 — Acknowledge immediately
Reply: `📡 Video received, analyzing...`

### Step 2 — Run transcription
```bash
python3 /Users/stewie/.openclaw/workspace/skills/tiktok-analyzer/transcribe.py "URL_HERE"
```

The script returns JSON:
```json
{
  "transcript": "full text here...",
  "language": "en",
  "video_id": "abc123",
  "from_cache": false
}
```

If `from_cache: true` → say "📚 Found this in your library!" instead of re-analyzing.

If there's an `"error"` key → relay the error cleanly (e.g. "This video is private or has been removed").

### Step 3 — Answer the user's question
Use the transcript text to answer whatever they asked. If they didn't ask a specific question, provide:
- **What it's about** (1-2 sentences)
- **Key points / what's being taught** (bullet list)
- **Tone / style** (educational, entertainment, story, etc.)

### Step 4 — Offer to save
Only if `from_cache: false`, ask:
> 💾 Want to save this transcript so you can ask more questions later without re-downloading? (yes/no)

If yes, run:
```bash
python3 /Users/stewie/.openclaw/workspace/skills/tiktok-analyzer/save_transcript.py "VIDEO_ID" 'JSON_DATA'
```
Replace VIDEO_ID with the video_id from step 2, and JSON_DATA with the full JSON output.

Confirm: `✅ Saved to your video library!`

---

## Searching Saved Transcripts

When the user asks about something they've analyzed before:
1. List files in `/Users/stewie/.openclaw/workspace/skills/tiktok-analyzer/transcripts/`
2. Read the relevant `.json` file(s)
3. Answer from the saved transcript

---

## Error Handling

| Error | Response |
|-------|----------|
| Private/removed video | "This video is private or has been removed. Try a different URL." |
| No ffmpeg | "You need ffmpeg installed first. Run: `brew install ffmpeg` (Mac) or `apt install ffmpeg` (Linux)" |
| No faster-whisper | "Run: `pip install faster-whisper yt-dlp` then try again." |
| Timeout | "That one took too long to download. Try a shorter video or check your connection." |

---

## Notes

- First run downloads the Whisper model (~150MB). Subsequent runs are fast.
- Transcription takes ~10-30s depending on video length.
- Non-English videos are detected and transcribed in their language.
- The skill works on **any** platform yt-dlp supports (TikTok, YouTube, Instagram, Twitter, Reddit, Vimeo, and 1000+ more).
