import time
import os
from utils.reddit import reddit
from utils.youtube import Youtube
from config import DEFAULT_TAGS, WAIT_TIME


def main():
    i = 0
    while True:
        print(f"Phase {i+1} of automation has begun")
        memes = reddit.get_memes(limit=1)
        if not memes:
            print("Meme not found, waiting for new memes...")
            i += 1
            time.sleep(10)
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
        sound_effect = Youtube.get_category_sound(caption)

        if meme_type == "gif":
            output_path = Youtube.gif_to_video(file_path, sound_effect)
        elif meme_type == "image":
            output_path = Youtube.image_to_video(file_path, sound_effect)

        Youtube.upload_video(output_path, caption, full_description, all_tags)

        if meme_type in ["gif", "image"] and os.path.exists(output_path):
            os.remove(output_path)

        print(f"Phase {i+1} of automation is over")
        time.sleep(WAIT_TIME)
        i += 1


if __name__ == "__main__":
    main()
