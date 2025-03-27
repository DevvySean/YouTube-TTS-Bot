# YouTube TTS Bot

This bot reads YouTube live chat messages and converts them to speech, allowing you to hear chat messages in real-time.

## Setup Instructions

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up YouTube API credentials:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the YouTube Data API v3
   - Create OAuth 2.0 credentials
   - Download the client secrets file and save it as `client_secrets.json` in this directory

3. Create a `.env` file in the project directory with your YouTube video ID:
```
VIDEO_ID=your_video_id_here
```
You can find your video ID in the URL of your YouTube video: `https://www.youtube.com/watch?v=VIDEO_ID`

## Usage

1. Run the bot:
```bash
python youtube_tts_bot.py
```

2. The first time you run the bot, it will open a browser window for OAuth authentication. Follow the prompts to authorize the application.

3. The bot will connect to your YouTube live chat and start reading messages aloud.

## Features

- Real-time chat message reading
- Text-to-speech conversion
- Automatic message deduplication
- Error handling and automatic reconnection
- Configurable speech rate

## Requirements

- Python 3.7 or higher
- YouTube API credentials
- Internet connection
- Working speakers/headphones 