import os
import time
import subprocess
import platform
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
from dotenv import load_dotenv

# For Windows TTS
try:
    import pyttsx3
except ImportError:
    pass

# Load environment variables
load_dotenv()

# YouTube API setup
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
API_NAME = 'youtube'
API_VERSION = 'v3'
CLIENT_SECRETS_FILE = 'client_secrets.json'

# TTS Settings
TTS_VOICE = os.getenv('TTS_VOICE', 'Alex')  # Default voice is Alex for macOS
TTS_RATE = int(os.getenv('TTS_RATE', '180'))  # Default rate is 180 words per minute

# Platform detection
IS_MACOS = platform.system() == 'Darwin'
IS_WINDOWS = platform.system() == 'Windows'

def get_youtube_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            try:
                print("\nStarting OAuth flow...")
                print("A browser window will open for authentication.")
                print("Please sign in with your Google account and grant the requested permissions.")
                
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
                print("Authentication successful!")
            except Exception as e:
                print(f"\nError during authentication: {e}")
                print("\nTroubleshooting steps:")
                print("1. Make sure you're using a Desktop app OAuth 2.0 Client ID")
                print("2. Verify that client_secrets.json is in the correct location")
                print("3. Check that you're signed in with the correct Google account")
                print("4. Delete token.pickle if it exists and try again")
                raise
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build(API_NAME, API_VERSION, credentials=creds)

def get_live_chat_id(youtube, video_id):
    try:
        request = youtube.videos().list(
            part="liveStreamingDetails",
            id=video_id
        )
        response = request.execute()
        
        if not response.get('items'):
            raise ValueError(f"No video found with ID: {video_id}")
            
        video_details = response['items'][0]
        if 'liveStreamingDetails' not in video_details:
            raise ValueError("This video is not a live stream")
            
        if 'activeLiveChatId' not in video_details['liveStreamingDetails']:
            raise ValueError("Live stream has not started yet or has ended")
            
        return video_details['liveStreamingDetails']['activeLiveChatId']
    except Exception as e:
        print(f"\nError getting live chat ID: {e}")
        print("\nPlease verify:")
        print("1. The video ID is correct")
        print("2. The video is a live stream")
        print("3. The live stream is currently active")
        print("\nYou can find the video ID in the URL of your live stream:")
        print("https://www.youtube.com/watch?v=VIDEO_ID")
        raise

def get_chat_messages(youtube, live_chat_id, last_message_id=None):
    try:
        params = {
            'liveChatId': live_chat_id,
            'part': 'snippet,authorDetails',
            'maxResults': 200
        }
        
        if last_message_id:
            params['pageToken'] = last_message_id
            
        request = youtube.liveChatMessages().list(**params)
        response = request.execute()
        return response
    except Exception as e:
        print(f"Error getting chat messages: {e}")
        return None

def get_available_voices():
    """Get a list of available voices on the current platform"""
    if IS_MACOS:
        try:
            result = subprocess.run(['say', '-v', '?'], capture_output=True, text=True)
            voices = []
            for line in result.stdout.split('\n'):
                if line.strip():
                    voice_name = line.split()[0]
                    voices.append(voice_name)
            return voices
        except Exception as e:
            print(f"Error getting available voices: {e}")
            return ["Alex", "Samantha", "Tom", "Victoria", "Daniel"]  # Return some default macOS voices
    
    elif IS_WINDOWS:
        try:
            engine = pyttsx3.init()
            return [voice.name for voice in engine.getProperty('voices')]
        except Exception as e:
            print(f"Error getting available voices: {e}")
            return ["Default Windows Voice"]
    
    else:
        print("Unsupported platform for voice listing")
        return ["Default Voice"]

def speak_message(message):
    try:
        if IS_MACOS:
            # Use macOS's built-in 'say' command with the selected voice and rate
            subprocess.run(['say', '-v', TTS_VOICE, '-r', str(TTS_RATE), message])
        
        elif IS_WINDOWS:
            # Use pyttsx3 for Windows
            engine = pyttsx3.init()
            
            # Set voice if specified and available
            voices = engine.getProperty('voices')
            if voices:
                # On Windows, we need to find the voice by name in the available voices
                for voice in voices:
                    if TTS_VOICE.lower() in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
            
            # Set speaking rate (pyttsx3 uses different scale than macOS)
            # macOS rate is words per minute, pyttsx3 is relative to default (200)
            engine.setProperty('rate', TTS_RATE)
            
            # Speak the message
            engine.say(message)
            engine.runAndWait()
        
        else:
            print(f"Unsupported platform for TTS: {platform.system()}")
            print(f"Message: {message}")
            
    except Exception as e:
        print(f"Error speaking message: {e}")
        print(f"Message: {message}")

def main():
    # Initialize YouTube API
    youtube = get_youtube_service()
    
    # Print platform info and available voices
    print(f"\nRunning on {platform.system()} {platform.version()}")
    
    if IS_MACOS or IS_WINDOWS:
        print("\nAvailable TTS voices:")
        voices = get_available_voices()
        if voices:
            print(", ".join(voices[:10]) + ("..." if len(voices) > 10 else ""))
        print(f"Current voice: {TTS_VOICE} (set TTS_VOICE in .env to change)")
        print(f"Current rate: {TTS_RATE} (set TTS_RATE in .env to change)")
    else:
        print("\nTTS is not supported on this platform")
    
    # Get video ID from environment variable
    video_id = os.getenv('VIDEO_ID')
    if not video_id:
        print("Please set VIDEO_ID in your .env file")
        print("You can find the video ID in the URL of your live stream:")
        print("https://www.youtube.com/watch?v=VIDEO_ID")
        return

    print(f"\nAttempting to connect to live stream with ID: {video_id}")
    print("Make sure the live stream is currently active!")

    # Get live chat ID
    try:
        live_chat_id = get_live_chat_id(youtube, video_id)
        print(f"\nSuccessfully connected to live chat!")
    except Exception as e:
        print("\nFailed to connect to live chat. Please check the error message above.")
        return

    last_message_id = None
    processed_messages = set()

    print("\nListening for chat messages...")
    print("Press Ctrl+C to stop the bot")

    while True:
        try:
            response = get_chat_messages(youtube, live_chat_id, last_message_id)
            allowed_authors = ["Fay Boyd"]
            if response and 'items' in response:
                for item in response.get('items', []):
                    message_id = item['id']
                    if message_id not in processed_messages:
                        author = item['authorDetails']['displayName']
                        message = item['snippet']['displayMessage']
                        if author == 'Fay Boyd' and author in allowed_authors:
                            author = "Fay"
                            print(f"{author}: {message}")
                            speak_message(f"{author} says: {message}")
                        elif author in allowed_authors:
                            print(f"{author}: {message}")
                            speak_message(f"{author} says: {message}")
                        else:
                            print(f"Not allowed author: {author}: {message}")
                            
                        processed_messages.add(message_id)

                last_message_id = response.get('nextPageToken')
            
            time.sleep(5)  # Wait 5 seconds before checking for new messages

        except KeyboardInterrupt:
            print("\nBot stopped by user")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main() 