import os
import praw
import requests

from dotenv import load_dotenv

load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT"),
)


def download_memes(limit=5):
    subreddit = reddit.subreddit("memes")
    os.makedirs("memes", exist_ok=True)

    results = []
    count = 0
    used_ids = set()
    used_ids_file = "used_memes.txt"
    if os.path.exists(used_ids_file):
        with open(used_ids_file, "r", encoding="utf-8") as f:
            for line in f:
                used_ids.add(line.strip())

    fail_count = 0
    max_fail = 10  # Stop if too many consecutive failures

    for post in subreddit.hot(limit=200):
        if post.id in used_ids:
            continue
        print(f"[DEBUG] Post: {post.title} - {post.url}")

        if post.is_video and post.media and "reddit_video" in post.media:
            video_url = post.media["reddit_video"]["fallback_url"]
            if not video_url.endswith(".mp4"):
                continue
            filename = f"memes/meme_video_{count}.mp4"
            try:
                response = requests.get(video_url, stream=True)
                if response.status_code == 200:
                    with open(filename, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print(f"[DEBUG] Saved video {filename}")
                    tags = [
                        tag[1:] for tag in post.title.split() if tag.startswith("#")
                    ]
                    tags += ["meme", "reddit", "shorts"]
                    hashtags = " ".join([f"#{t}" for t in tags])
                    description = (
                        f"Original Reddit meme.\nSource: {post.url}\n{hashtags}"
                    )
                    results.append(
                        {
                            "file": filename,
                            "title": post.title,
                            "description": description,
                            "tags": tags,
                            "type": "video",
                        }
                    )
                    with open(used_ids_file, "a", encoding="utf-8") as f:
                        f.write(post.id + "\n")
                    count += 1
                else:
                    print("[DEBUG] Video download failed")
            except Exception as e:
                print(f"[DEBUG] Error downloading video: {e}")
                # Always try to remove the file if it was created
                if os.path.exists(filename):
                    os.remove(filename)
                fail_count += 1
                if fail_count >= max_fail:
                    print(
                        "[ERROR] Too many failed downloads from Reddit. Stopping early."
                    )
                    break

        elif post.url.endswith((".gif", ".gifv")):
            gif_url = post.url
            if gif_url.endswith(".gifv"):
                gif_url = gif_url[:-1]
            filename = f"memes/meme_gif_{count}.gif"
            try:
                response = requests.get(gif_url, stream=True)
                if response.status_code == 200:
                    with open(filename, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print(f"[DEBUG] Saved gif {filename}")
                    tags = [
                        tag[1:] for tag in post.title.split() if tag.startswith("#")
                    ]
                    tags += ["meme", "reddit", "shorts"]
                    hashtags = " ".join([f"#{t}" for t in tags])
                    description = (
                        f"Original Reddit meme.\nSource: {post.url}\n{hashtags}"
                    )
                    results.append(
                        {
                            "file": filename,
                            "title": post.title,
                            "description": description,
                            "tags": tags,
                            "type": "gif",
                        }
                    )
                    with open(used_ids_file, "a", encoding="utf-8") as f:
                        f.write(post.id + "\n")
                    count += 1
                else:
                    print("[DEBUG] Gif download failed")
            except Exception as e:
                print(f"[DEBUG] Error downloading gif: {e}")
                # Always try to remove the file if it was created
                if os.path.exists(filename):
                    os.remove(filename)
                fail_count += 1
                if fail_count >= max_fail:
                    print(
                        "[ERROR] Too many failed downloads from Reddit. Stopping early."
                    )
                    break
        else:
            print("[DEBUG] Skipped: Not a Reddit hosted .mp4 video or gif")
        if count >= limit:
            break
    return results
