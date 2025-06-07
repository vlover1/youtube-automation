import os
import ffmpeg
import time
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from oauth2client import file, client, tools
from config import CATEGORY_SOUNDS, DEFAULT_SOUND, YOUTUBE_SCOPES


class Youtube:
    def __init__(self):
        self.youtube = self.verify_youtube_credentials()

    @staticmethod
    def verify_youtube_credentials():
        store = file.Storage("secrets/token.json")
        creds = store.get()

        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets(
                "secrets/client_secrets.json", YOUTUBE_SCOPES
            )
            creds = tools.run_flow(flow, store)

        return build("youtube", "v3", credentials=creds)

    @staticmethod
    def upload_video(path, title, description="Shorts bot uploaded.", tags=None):
        youtube = Youtube.verify_youtube_credentials()

        if tags is None:
            tags = ["meme", "shorts", "funny"]

        success = False

        while not success:
            try:
                request = youtube.videos().insert(
                    part="snippet,status",
                    body={
                        "snippet": {
                            "title": title,
                            "description": description,
                            "tags": tags,
                            "categoryId": "23",
                        },
                        "status": {
                            "privacyStatus": "public",
                            "selfDeclaredMadeForKids": False,
                        },
                    },
                    media_body=MediaFileUpload(path),
                )
                response = request.execute()
                print(f"Uploaded: {response.get('id')}")
                os.remove(path)
                print(f"{path} deleted.")
                success = True
            except FileNotFoundError:
                print(f"File not found: {path}")
                break
            except Exception as e:
                print(f"An error occurred during upload: {e}")
                if "uploadLimitExceeded" in str(e):
                    print("YouTube upload limit exceeded. Please try again later.")
                    time.sleep(60 * 60 * 24)
                else:
                    break

    @staticmethod
    def get_category_sound(title: str) -> str:
        title_lower = title.lower()
        for keywords, sound_path in CATEGORY_SOUNDS:
            if any(word in title_lower for word in keywords):
                return sound_path
        return DEFAULT_SOUND

    @staticmethod
    def gif_to_video(file_path: str, sound_effect: str) -> str:
        output_path = file_path.replace(".gif", ".mp4")
        # Convert GIF to MP4
        (
            ffmpeg.input(file_path)
            .filter("scale", "trunc(iw/2)*2", "trunc(ih/2)*2")
            .output("video.mp4", vcodec="libx264", pix_fmt="yuv420p", t=9, r=10)
            .overwrite_output()
            .run(quiet=True, capture_stdout=True, capture_stderr=True)
        )
        # Add sound effect to video
        (
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
            )
            .overwrite_output()
            .run(quiet=True, capture_stdout=True, capture_stderr=True)
        )
        if os.path.exists("video.mp4"):
            os.remove("video.mp4")
        if os.path.exists(file_path):
            os.remove(file_path)
        return output_path
