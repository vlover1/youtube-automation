# YouTube Meme Automation Bot 🤖🎬

This project is a bot that automatically downloads popular meme videos and gifs from Reddit, merges them with sound effects, and uploads them as YouTube Shorts. 🚀

## Features ✨

- Fetches popular meme content in mp4 and gif format from Reddit.
- Merges videos/gifs with random sound effects.
- Automatically uploads to YouTube Shorts.
- Tracks uploaded memes to avoid duplicates.
- Waits and retries automatically if YouTube upload limit is reached.
- Easily add your own sound effects.

## Installation 🛠️

### Requirements

- Python 3.8+
- `ffmpeg` (for video/gif processing)
- Required Python packages (listed in `requirements.txt`)

### Steps

1. **Clone or download the project.**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Get your Reddit API keys and add them to a `.env` file:**
   ```env
   REDDIT_CLIENT_ID=xxx
   REDDIT_CLIENT_SECRET=xxx
   REDDIT_USER_AGENT=xxx
   ```
4. **Get Google Cloud OAuth2 client credentials for the YouTube API and place them in the `secrets/` folder:**
   - `client_secrets.json` and `token.json` (created on first run) are required.
5. **Make sure `ffmpeg` is installed:**
   ```powershell
   # For Windows, download from https://ffmpeg.org/download.html and add to PATH
   ```
   For Linux:
   ```bash
   sudo apt install ffmpeg
   ```

## Usage ▶️

```bash
python main.py
```

- The script runs in an infinite loop, finding and uploading a new meme each cycle. 🔄
- If the upload limit is reached, it waits and retries automatically. ⏱️

### Run in Background 🖥️

- You can use `tmux`, `screen`, or `nohup` to run in the background:
  ```bash
  nohup python main.py > output.log 2>&1 &
  ```

## Folders and Files 📁

- `memes/` : Downloaded meme files
- `sounds/` : Sound effects (add your own if you like)
- `secrets/` : API credentials
- `used_memes.txt` : Used meme IDs (prevents re-upload)
- `src/` : All source code and helper modules

## Notes 📝

- Only downloads mp4 and gif files hosted on Reddit.
- Files are not deleted if upload limit is reached; they are deleted after a successful upload.
- You can add your own sound effects to the `sounds/` folder. 🎵

## License 📄

MIT
