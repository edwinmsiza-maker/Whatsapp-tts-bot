from flask import Flask, request
import os, requests

app = Flask(__name__)
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "tts-fun-verify-123")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")

@app.route('/')
def home():
    return "Bot Live - Funny Voice Ready!", 200

@app.route('/webhook', methods=['GET'])
def verify():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    if mode == 'subscribe' and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    try:
        msg = data['entry'][0]['changes'][0]['value']['messages'][0]
        from_number = msg['from']
        if msg['type'] == 'audio':
            audio_id = msg['audio']['id']
            # For now just reply funny text - TTS comes next
            url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
            headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
            payload = {
                "messaging_product": "whatsapp",
                "to": from_number,
                "text": {"body": "Haha! I got your voice note 😂 You sound like a chipmunk on coffee! Send another one!"}
            }
            requests.post(url, headers=headers, json=payload)
    except Exception as e:
        print(f"Error: {e}")
    return "ok", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
