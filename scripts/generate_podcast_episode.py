import os
import subprocess
import requests
from datetime import datetime
from openai import OpenAI

def get_recent_changes():
    """Get recent changes from git history."""
    result = subprocess.run(['git', 'log', '--oneline', '--since="1 week ago"'], capture_output=True, text=True)
    return result.stdout.strip()

def generate_podcast_script(changes):
    """Generate podcast script using OpenAI."""
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    prompt = f"""
    Generate a 2-3 minute podcast script summarizing these recent changes to the AI Development Playbook:

    {changes}

    Make it engaging, highlight key improvements, and end with a call to action for listeners.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )
    return response.choices[0].message.content

def text_to_speech(script, episode_number):
    """Convert script to speech using ElevenLabs."""
    url = "https://api.elevenlabs.io/v1/text-to-speech/voice-id"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": os.getenv('ELEVENLABS_API_KEY')
    }
    data = {
        "text": script,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        filename = f"episode_{episode_number}.mp3"
        with open(filename, 'wb') as f:
            f.write(response.content)
        return filename
    else:
        raise Exception(f"TTS failed: {response.status_code}")

def upload_to_storage(filename):
    """Upload MP3 to cloud storage (placeholder for actual implementation)."""
    # This would integrate with your cloud storage provider
    # For now, return a placeholder URL
    return f"https://storage.example.com/{filename}"

def main():
    changes = get_recent_changes()
    if not changes:
        print("No recent changes, skipping episode generation.")
        return

    # Determine episode number
    episode_number = len([f for f in os.listdir('.') if f.startswith('episode_') and f.endswith('.mp3')]) + 1

    script = generate_podcast_script(changes)
    audio_file = text_to_speech(script, episode_number)
    audio_url = upload_to_storage(audio_file)

    # Save episode info for RSS update
    episode_info = {
        'number': episode_number,
        'title': f"Episode {episode_number}: Weekly Updates",
        'description': f"Weekly roundup of playbook changes and improvements. {script[:200]}...",
        'url': audio_url,
        'date': datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
    }

    with open('latest_episode.json', 'w') as f:
        import json
        json.dump(episode_info, f)

if __name__ == "__main__":
    main()