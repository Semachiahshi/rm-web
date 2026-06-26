from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp, tempfile, os, shutil

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def cleanup(path: str):
    shutil.rmtree(path, ignore_errors=True)

@app.get("/download")
async def download(q: str, background_tasks: BackgroundTasks):
    tmp = tempfile.mkdtemp()
    try:
        opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '0'}],
            'outtmpl': f'{tmp}/song.%(ext)s',
            'default_search': 'scsearch',
            'noplaylist': True,
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(q, download=True)
            title = info.get('title', q)

        background_tasks.add_task(cleanup, tmp)
        return FileResponse(f'{tmp}/song.mp3', media_type='audio/mpeg', filename=f'{title}.mp3')
    except Exception as e:
        shutil.rmtree(tmp, ignore_errors=True)
        raise
