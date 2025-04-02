
import datetime
import os
import json
import requests
import time
import hashlib
import getpass
import uuid
import subprocess
import platform



# Get the directory where the script is located
SCRIPT_DIR_PATH = os.path.dirname(os.path.abspath(__file__))
# Update the last check file path to be relative to script location
LAST_CHECK_FILE_PATH = os.path.join(SCRIPT_DIR_PATH, "last_check.json")
API_FILE_PATH = os.path.join(SCRIPT_DIR_PATH, "api_key.txt")
CHANNEL_LIST_PATH = os.path.join(SCRIPT_DIR_PATH, "channel_list.json")


def get_latest_videos(channel_id, API_KEY, max_results=50):
    """
    Fetch the latest videos from a channel's uploads.
    """
    try:
        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&maxResults={max_results}&order=date&type=video&key={API_KEY}"
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception if the request failed
        return response.json().get("items", [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching videos: {e.__repr__()}")
        return []
    
def get_new_videos(channel_id, since_date, API_KEY):
    """
    Check for videos uploaded since a certain date.
    """
    latest_videos = get_latest_videos(channel_id, API_KEY)
    new_videos = []
    for video in latest_videos:
        published_at = video["snippet"]["publishedAt"]
        published_date = datetime.datetime.fromisoformat(published_at[:-1])
        if published_date > since_date:
            new_videos.append(video)
    return new_videos

def load_last_check():
    """
    Load the timestamp of the last check from file.
    """
    if os.path.exists(LAST_CHECK_FILE_PATH):
        with open(LAST_CHECK_FILE_PATH, "r") as f:
            data = json.load(f)
            return datetime.datetime.fromisoformat(data["last_check"])
    else:
        return datetime.datetime.now() - datetime.timedelta(weeks=1)

def save_last_check():
    """
    Save the timestamp of the current check to file.
    """
    with open(LAST_CHECK_FILE_PATH, "w") as f:
        json.dump({"last_check": datetime.datetime.now().isoformat()}, f)

def send_notification(message, ntfy_channel):
    try:
        requests.post(f"https://ntfy.sh/{ntfy_channel}",
            data=message.encode(encoding='utf-8'))
    except Exception as e:
        print(f"Failed to send notification: {e}")

def get_unique_user_string():
    """
    Generate a unique string based on the user's information.
    """
    unique_id = ''
    username = getpass.getuser()
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0,2*6,2)][::-1])

    if platform.system() == "Windows":
        try:
            cmd = "wmic baseboard get serialnumber"
            motherboard_serial = subprocess.check_output(cmd, shell=True).decode().split('\n')[1].strip()
            unique_id = f"{username}-{mac}-{motherboard_serial}"
        except:
            unique_id = f"{username}-{mac}"
    else:
        unique_id = f"{username}-{mac}"
    return unique_id

def main():
    # load the API key from the file
    # Read API key from file
    if not os.path.exists(API_FILE_PATH):
        print(f"API key file not found at {API_FILE_PATH}. Please create it with your YouTube API key.")
        return
    with open(API_FILE_PATH, 'r') as f:
        API_KEY = f.read().strip()

    # Get a unique identified string for the notification system
    script_path = os.path.abspath(__file__)
    hash_str = str(API_KEY) + script_path + get_unique_user_string()
    hash_str = hashlib.md5(hash_str.encode()).hexdigest()
    ntfy_channel = f"youtube-notification-system-{hash_str}"
    print(f"Listening in the link: https://ntfy.sh/{ntfy_channel}")
    send_notification("Starting loop", ntfy_channel)

    #Start main loop
    while True:
        # Read channel IDs from JSON file, in case it has changed
        if os.path.exists(CHANNEL_LIST_PATH):
            with open(CHANNEL_LIST_PATH, 'r') as f:
                CHANNEL_IDS = json.load(f)
        last_check = load_last_check()
        print(f"It is now {datetime.datetime.now()}. Checking for new videos since {last_check}")                
        
        # Loop through each channel and check for new uploads
        for yt_channel in CHANNEL_IDS:
            channel_id = yt_channel['channel_id']
            channel_name = yt_channel['channel_name']
            new_videos = get_new_videos(channel_id, last_check, API_KEY)
            if new_videos:
                print(f"\nNew videos found for channel {channel_name}:")
                for video in new_videos:
                    title = video["snippet"]["title"]
                    video_id = video["id"]["videoId"]
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    print(f"- {title}: {video_url}")    
                    send_notification(f"- {title}: {video_url}", ntfy_channel)            

        # Update the last check time
        save_last_check()
        time.sleep(60*60*6)  # Sleep for 6 hour (3600 seconds)

if __name__ == "__main__":
    main()
