import os

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from oauth2client import file, client, tools
from config import CATEGORY_SOUNDS, DEFAULT_SOUND

YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def upload_to_youtube(video_path, title, description="Shorts bot uploaded.", tags=None):
    store = file.Storage("secrets/token.json")
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(
            "secrets/client_secrets.json", YOUTUBE_SCOPES
        )
        creds = tools.run_flow(flow, store)

    youtube = build("youtube", "v3", credentials=creds)

    if tags is None:
        tags = ["meme", "shorts", "funny"]

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": "23",
            },
            "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False},
        },
        media_body=MediaFileUpload(video_path),
    )
    response = request.execute()
    print("Uploaded:", response.get("id"))
    try:
        os.remove(video_path)
        print(f"{video_path} deleted.")
    except Exception as e:
        print(f"{video_path} could not be deleted: {e}")


def get_category_sound(title: str) -> str:
    title_lower = title.lower()
    for keywords, sound_path in CATEGORY_SOUNDS:
        if any(word in title_lower for word in keywords):
            return sound_path
    return DEFAULT_SOUND


def process_gif(file_path: str, sound_effect: str) -> str:
    import ffmpeg
    import os

    output_path = file_path.replace(".gif", ".mp4")
    ffmpeg.input(file_path).filter("scale", "trunc(iw/2)*2", "trunc(ih/2)*2").output(
        "video.mp4", vcodec="libx264", pix_fmt="yuv420p", t=9, r=10
    ).overwrite_output().run()
    ffmpeg.output(
        ffmpeg.input("video.mp4"),
        ffmpeg.input(sound_effect),
        output_path,
        vcodec="libx264",
        pix_fmt="yuv420p",
        t=9,
        r=10,
        shortest=None,
        acodec="aac",
        audio_bitrate="192k",
    ).overwrite_output().run()
    if os.path.exists("video.mp4"):
        os.remove("video.mp4")
    if os.path.exists(file_path):
        os.remove(file_path)
    return output_path


def upload_with_retry(
    output_path,
    caption,
    full_description,
    all_tags,
    max_retries=100,
    retry_wait=60 * 30,
):
    import time

    upload_success = False
    retries = 0
    while not upload_success and retries < max_retries:
        try:
            upload_to_youtube(output_path, caption, full_description, all_tags)
            upload_success = True
        except Exception as e:
            if "uploadLimitExceeded" in str(e):
                print("[WARN] YouTube upload limit reached. Waiting before retrying...")
                time.sleep(retry_wait)
                retries += 1
            else:
                print(f"[ERROR] Upload failed: {e}")
                break
