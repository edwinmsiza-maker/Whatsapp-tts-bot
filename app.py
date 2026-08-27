from flask import Flask, request
import requests
import os
import openai

app = Flask(__name__)

# --- PUT YOUR KEYS HERE - READ FROM RENDER ENV ---
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "YOUR_META_TOKEN")
PHONE_ID = os.getenv("PHONE_ID", "1308106479054362")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "ttsfun2024")
ELEVENLABS_KEY = os.getenv("ELEVENLABS_KEY", "")
OPENAI_KEY = os.getenv("OPENAI_KEY", "")

openai.api_key = OPENAI_KEY
VOICE_ID = "21m00Tcm4TlvDq8ikWAM"

# --- WEBHOOK VERIFICATION - THIS IS WHAT META NEEDS ---
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
    # here your bot logic will go
    print(data)
    return "OK", 200

@app.route('/')
def home():
    return "TTS Bot is Live!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
