import time
import os

from utils.meme_scraper import download_memes
from utils.upload import get_category_sound, process_gif, upload_with_retry
from config import DEFAULT_TAGS, WAIT_TIME


def main():
    """
    Downloads and uploads a new video meme to YouTube in each loop.
    Runs forever until manually stopped.
    """
    i = 0
    while True:
        print(f"[INFO] Starting loop {i+1}...")
        memes = download_memes(limit=1)
        if not memes:
            print("No meme found.")
            i += 1
            continue
        meme = memes[0]
        file_path = meme["file"]
        caption = meme["title"]
        description = meme["description"]
        tags = meme["tags"]
        all_tags = list(dict.fromkeys(tags + DEFAULT_TAGS))[:50]
        hashtags = " ".join([f"#{tag}" for tag in all_tags])
        full_description = f"{description}\n\n{hashtags}"
        meme_type = meme.get("type", "video")
        output_path = file_path
        sound_effect = get_category_sound(caption)
        if meme_type == "gif":
            output_path = process_gif(file_path, sound_effect)
        upload_with_retry(output_path, caption, full_description, all_tags)
        if meme_type == "gif" and os.path.exists(output_path):
            os.remove(output_path)
        print(f"[INFO] Loop {i+1} completed.")
        time.sleep(WAIT_TIME)
        i += 1


if __name__ == "__main__":
    main()
