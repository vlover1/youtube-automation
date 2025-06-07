import os
import praw
import requests
from config import REDDIT_MAX_FAIL
from dotenv import load_dotenv

load_dotenv()


class Reddit(praw.Reddit):
    def __init__(self, subreddit_name="memes"):
        super().__init__(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT"),
        )
        self.subreddit_name = subreddit_name
        self.subreddit = self.subreddit(subreddit_name)
        self.used_ids_file = "used_memes.txt"
        self.memes_dir = "memes"
        os.makedirs(self.memes_dir, exist_ok=True)

    def host(self, limit=100):
        return self.subreddit.new(limit=limit)

    def get_memes(self, limit=200):
        results = []
        count = 0
        used_ids = set()
        if os.path.exists(self.used_ids_file):
            with open(self.used_ids_file, "r", encoding="utf-8") as lines:
                for line in lines:
                    used_ids.add(line.strip())
        fail_count = 0
        for post in self.host(limit=limit):
            print(
                f"DEBUG: POST: id={post.id}, is_video={getattr(post, 'is_video', None)}, url={getattr(post, 'url', None)}, media={getattr(post, 'media', None)}"
            )
            if post.id in used_ids:
                continue
            # Video
            if (
                hasattr(post, "is_video")
                and post.is_video
                and post.media
                and "reddit_video" in post.media
            ):
                video_url = post.media["reddit_video"]["fallback_url"]
                if not video_url.endswith(".mp4"):
                    continue
                filename = f"{self.memes_dir}/{count}.mp4"
                try:
                    response = requests.get(video_url, stream=True)
                    if response.status_code == 200:
                        with open(filename, "wb") as chunks:
                            for chunk in response.iter_content(chunk_size=8192):
                                chunks.write(chunk)
                        tags = [
                            tag[1:] for tag in post.title.split() if tag.startswith("#")
                        ]
                        tags += ["meme", "reddit", "shorts"]
                        formatted_tags = " ".join([f"#{t}" for t in tags])
                        description = f"Original Reddit meme.\nSource: {post.url}\n{formatted_tags}"
                        results.append(
                            {
                                "file": filename,
                                "title": post.title,
                                "description": description,
                                "tags": tags,
                                "type": "video",
                            }
                        )
                        with open(self.used_ids_file, "a", encoding="utf-8") as f:
                            f.write(post.id + "\n")
                        count += 1
                    else:
                        print("Video download failed")
                except Exception as e:
                    print(f"Error downloading video: {e}")
                    if os.path.exists(filename):
                        os.remove(filename)
                    fail_count += 1
                    if fail_count >= REDDIT_MAX_FAIL:
                        print("Too many failed downloads from Reddit. Stopping early.")
                        break
            # GIF
            elif (
                hasattr(post, "url")
                and post.url
                and post.url.endswith((".gif", ".gifv"))
            ):
                gif_url = post.url
                if gif_url.endswith(".gifv"):
                    gif_url = gif_url[:-1]
                filename = f"{self.memes_dir}/{count}.gif"
                try:
                    response = requests.get(gif_url, stream=True)
                    if response.status_code == 200:
                        with open(filename, "wb") as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)
                        tags = [
                            tag[1:] for tag in post.title.split() if tag.startswith("#")
                        ]
                        tags += ["meme", "reddit", "shorts"]
                        formatted_tags = " ".join([f"#{t}" for t in tags])
                        description = f"Original Reddit meme.\nSource: {post.url}\n{formatted_tags}"
                        results.append(
                            {
                                "file": filename,
                                "title": post.title,
                                "description": description,
                                "tags": tags,
                                "type": "gif",
                            }
                        )
                        with open(self.used_ids_file, "a", encoding="utf-8") as f:
                            f.write(post.id + "\n")
                        count += 1
                    else:
                        print("Gif download failed")
                except Exception as e:
                    print(f"Error downloading gif: {e}")
                    if os.path.exists(filename):
                        os.remove(filename)
                    fail_count += 1
                    if fail_count >= REDDIT_MAX_FAIL:
                        print("Too many failed downloads from Reddit. Stopping early.")
                        break
        return results


reddit = Reddit()
