from fastapi import FastAPI, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from yt_dlp import YoutubeDL
import os
import logging
import re

# Initialize logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure 'downloads' folder exists
if not os.path.exists('downloads'):
    os.makedirs('downloads')

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to remove invalid characters."""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def download_video_task(url: str, filename: str):
    """Download video task that runs in the background."""
    ydl_opts = {
        'format': 'best',
        'outtmpl': f'downloads/{filename}.%(ext)s',  # Save video with a safe filename
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        logging.info(f"Video downloaded successfully: {filename}")
    except Exception as e:
        logging.error(f"Error during download: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to download video")

@app.post("/download")
async def download_video(url: str = Form(...), background_tasks: BackgroundTasks = BackgroundTasks()):
    """Endpoint to initiate YouTube video download."""
    if not url:
        raise HTTPException(status_code=400, detail="No URL provided")

    # Validate if the URL is a valid YouTube URL
    if not ("youtube.com" in url or "youtu.be" in url):
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    try:
        # Extract the video info to get the video title for a proper filename
        with YoutubeDL({'quiet': True}) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            video_title = info_dict.get('title', 'video')

        # Generate a safe filename from the video title
        safe_filename = sanitize_filename(video_title.replace(" ", "_"))

        # Schedule the download as a background task
        background_tasks.add_task(download_video_task, url, safe_filename)

        # Construct the download URL for the frontend
        download_url = f"http://localhost:8000/downloaded-video/{safe_filename}.mp4"

        logging.info(f"Download initiated for {url}, saving as {safe_filename}.mp4")

        return JSONResponse(content={"message": "Download initiated", "download_url": download_url})

    except Exception as e:
        logging.error(f"Error downloading video: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred during the video download")

@app.get("/downloaded-video/{filename}")
async def serve_video_file(filename: str):
    """Serve the downloaded video file."""
    file_path = os.path.join('downloads', filename)
    if os.path.exists(file_path):
        logging.info(f"Serving file: {filename}")
        return FileResponse(file_path, media_type='video/mp4', filename=filename)
    else:
        logging.error(f"File not found: {filename}")
        raise HTTPException(status_code=404, detail="File not found")
