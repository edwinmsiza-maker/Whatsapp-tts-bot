from flask import Flask, request
import os, requests
from gtts import gTTS

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "tts-fun")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
GROQ_KEY = os.environ.get("GROQ_KEY")

def ask_groq(q):
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_KEY}"},
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role":"system","content":"Answer in 2 short sentences. Will be spoken aloud."},
                {"role":"user","content": q}
            ]
        }, timeout=20)
    return r.json()['choices'][0]['message']['content']

def send_voice(to, text):
    tts = gTTS(text=text, lang='en')
    tts.save("/tmp/reply.mp3")
    up = requests.post(
        f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/media",
        headers={"Authorization": f"Bearer {WHATSAPP_TOKEN}"},
        files={"file": ("reply.mp3", open("/tmp/reply.mp3","rb"), "audio/mpeg")},
        data={"messaging_product":"whatsapp","type":"audio/mpeg"}
    ).json()
    media_id = up.get("id")
    requests.post(
        f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages",
        headers={"Authorization": f"Bearer {WHATSAPP_TOKEN}","Content-Type":"application/json"},
        json={"messaging_product":"whatsapp","to":to,"type":"audio","audio":{"id":media_id}}
    )

@app.route('/')
def home():
    return "Bot Live - Funny Voice Ready!", 200

@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get('hub.verify_token') == VERIFY_TOKEN:
        return request.args.get('hub.challenge'), 200
    return "Verification failed", 403

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    try:
        msg = data['entry'][0]['changes'][0]['value']['messages'][0]
        from_num = msg['from']
        text = msg['text']['body'] if msg['type']=='text' else "Tell me a joke"
        ans = ask_groq(text)
        send_voice(from_num, ans)
    except Exception as e:
        print(e)
    return "ok", 200
