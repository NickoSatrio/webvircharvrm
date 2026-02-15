import os
import time
from elevenlabs.client import ElevenLabs
from elevenlabs import save

class TTSEngine:
    def __init__(self, api_key, voice_id):
        self.client = ElevenLabs(api_key=api_key)
        self.voice_id = voice_id
        self.output_dir = os.path.join("static", "audio")
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_speech(self, text, filename=None):
        if not filename:
            filename = f"speech_{int(time.time())}.mp3"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # ElevenLabs v2.x synthesis
        audio_generator = self.client.text_to_speech.convert(
            text=text,
            voice_id=self.voice_id,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )
        
        # Collect chunks and save
        with open(filepath, "wb") as f:
            for chunk in audio_generator:
                if chunk:
                    f.write(chunk)
            
        return filename

# Note: The engine instance should now be initialized in app.py with keys
engine = None
