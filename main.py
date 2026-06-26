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
            'outtmpl': f'{tmp}/%(title)s.%(ext)s',
            'default_search': 'scsearch',
            'noplaylist': True,
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(q, download=True)
        
        mp3 = [f for f in os.listdir(tmp) if f.endswith('.mp3')][0]
        mp3_path = os.path.join(tmp, mp3)
        background_tasks.add_task(cleanup, tmp)
        return FileResponse(mp3_path, media_type='audio/mpeg', filename=mp3)
    except Exception as e:
        shutil.rmtree(tmp, ignore_errors=True)
        raise
