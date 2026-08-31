from flask import Flask, request
import requests
import os

app = Flask(__name__)

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
PHONE_ID = os.getenv("PHONE_ID", "1308106479054362")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "tts_fun_verify_2024")
ELEVENLABS_KEY = os.getenv("ELEVENLABS_KEY", "")
OPENAI_KEY = os.getenv("OPENAI_KEY", "")

VOICE_ID = "21m00Tcm4TlvDq8ikWAM"

@app.route('/')
def home():
    return "TTS FUN 2 Bot Running!"

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    else:
        return "Verification failed", 403

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print(data)

    try:
        entry = data['entry'][0]['changes'][0]['value']
        if 'messages' in entry:
            msg = entry['messages'][0]
            from_number = msg['from']
            text = msg.get('text', {}).get('body', '')

            if text:
                # Convert to voice with ElevenLabs if key exists, else send text
                if ELEVENLABS_KEY:
                    audio_url = text_to_speech_elevenlabs(text)
                    if audio_url:
                        send_audio(from_number, audio_url)
                    else:
                        send_text(from_number, f"🎤 You said: {text}")
                else:
                    # Fallback Google TTS link
                    send_text(from_number, f"Got it! Add ELEVENLABS_KEY to make me speak: {text}")
    except Exception as e:
        print(f"Error: {e}")

    return "OK", 200

def text_to_speech_elevenlabs(text):
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
        headers = {"xi-api-key": ELEVENLABS_KEY, "Content-Type": "application/json"}
        payload = {"text": text[:500], "model_id": "eleven_monolingual_v1"}
        r = requests.post(url, headers=headers, json=payload)
        if r.status_code == 200:
            # Upload to WhatsApp - for now save temp and return need to upload
            # Simplified: we will use a public hosting, but for quick test we send as link
            # Actually ElevenLabs returns audio binary - we need to upload to WhatsApp
            # For Render, we will save and need to handle media upload
            return None
    except Exception as e:
        print(e)
    return None

def send_text(to, text):
    url = f"https://graph.facebook.com/v20.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    data = {"messaging_product": "whatsapp", "to": to, "text": {"body": text}}
    requests.post(url, headers=headers, json=data)

def send_audio(to, audio_link):
    url = f"https://graph.facebook.com/v20.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    data = {"messaging_product": "whatsapp", "to": to, "type": "audio", "audio": {"link": audio_link}}
    requests.post(url, headers=headers, json=data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
