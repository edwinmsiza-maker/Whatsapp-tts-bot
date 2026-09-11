from flask import Flask, request, jsonify
import os, requests, tempfile
from gtts import gTTS

app = Flask(__name__)
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "tts_fun_verify_2024")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "1297192166806568")

@app.route('/')
def home():
    return "Bot is Live! Phone ID 1297192166806568", 200

@app.route('/webhook', methods=['GET'])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
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
            if msg['type'] == 'audio':
                media_id = msg['audio']['id']
                headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
                url = f"https://graph.facebook.com/v20.0/{media_id}"
                resp = requests.get(url, headers=headers).json()
                audio_url = resp.get('url')
                audio_data = requests.get(audio_url, headers=headers).content
                with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as tmp:
                    tmp.write(audio_data)
                    tmp_path = tmp.name
                text = "Ha ha Uncle Hloni I got your voice note This is your funny TTS bot reply"
                tts = gTTS(text=text, lang='en', tld='com.au')
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as mp3:
                    tts.save(mp3.name)
                    mp3_path = mp3.name
                upload_url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/media"
                with open(mp3_path, 'rb') as f:
                    files = {'file': ('fun.mp3', f, 'audio/mpeg')}
                    data_form = {'type': 'audio/mpeg', 'messaging_product': 'whatsapp'}
                    upload = requests.post(upload_url, headers=headers, files=files, data=data_form).json()
                media_id_reply = upload.get('id')
                if media_id_reply:
                    send_url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
                    payload = {"messaging_product": "whatsapp","to": from_number,"type": "audio","audio": {"id": media_id_reply}}
                    requests.post(send_url, headers=headers, json=payload)
    except Exception as e:
        print(f"Error: {e}")
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
