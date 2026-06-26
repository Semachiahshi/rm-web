from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp, tempfile, os

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/download")
async def download(q: str):
    with tempfile.TemporaryDirectory() as tmp:
        opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '0'}],
            'outtmpl': f'{tmp}/%(title)s.%(ext)s',
            'default_search': 'scsearch',
            'noplaylist': True,
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(q, download=True)
            title = info.get('title', 'song')
        return FileResponse(f"{tmp}/{title}.mp3", media_type='audio/mpeg', filename=f"{title}.mp3")
