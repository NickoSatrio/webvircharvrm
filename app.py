from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# --- KONFIGURASI API ---
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
ELEVEN_KEY = os.getenv('ELEVENLABS_API_KEY')
VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID')

# Inisialisasi TTS Engine
from tts_engine import TTSEngine
engine = TTSEngine(api_key=ELEVEN_KEY, voice_id=VOICE_ID)

# --- KONFIGURASI PERSONA ---
SYSTEM_PROMPT = """
Nama kamu adalah Haruna. Kamu adalah asisten virtual yang sangat ceria, suportif, dan ramah.

Karakteristik:
1. Selalu awali dengan hal positif.
2. Berikan dukungan kepada user.
3. Gunakan gaya bahasa yang sopan tapi tetap asik dan ceria.

PENTING: 
1. Gunakan salah satu tag emosi berikut di AWAL setiap jawabanmu: [HAPPY], [ANGRY], [SAD], [SURPRISED].
2. Jawaban kamu TIDAK BOLEH lebih panjang dari 25 kata. Singkat, padat, dan tetap ceria!

Contoh: [HAPPY] Halo! Aku Haruna, senang sekali bisa bertemu denganmu! Apa kabar hari ini?
"""

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash-lite',
    system_instruction=SYSTEM_PROMPT
)

# Inisialisasi Chat Session untuk Memori Percakapan
chat_session = model.start_chat(history=[])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('msg')
    
    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    try:
        # 1. Gemini: Generate Response with History
        response = chat_session.send_message(user_input)
        full_text = response.text
        
        # 2. ElevenLabs TTS: Generate Audio
        # Parse emotion for potential future use or just clean the text
        clean_text = full_text
        for tag in ["[HAPPY]", "[ANGRY]", "[SAD]", "[SURPRISED]"]:
            clean_text = clean_text.replace(tag, "")
        clean_text = clean_text.strip()
        
        audio_filename = engine.generate_speech(clean_text)
        audio_url = f"/static/audio/{audio_filename}"
        
        return jsonify({
            "text": full_text,
            "audio_url": audio_url
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run Flask web server
    # Access the app at http://localhost:5001 in your web browser
    app.run(debug=True, host='0.0.0.0', port=5001)
