import os, requests, tempfile
from flask import Flask, request
from gtts import gTTS

app = Flask(__name__)

TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_ID = os.environ.get("PHONE_NUMBER_ID")
GROQ_KEY = os.environ.get("GROQ_KEY") or os.environ.get("GROQ_API_KEY")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN") or "myverify123"

def ask_groq(q):
    try:
        headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
        payload = {
            "model":"openai/gpt-oss-20b",
            "messages": [
                {"role": "system", "content": "You are witty and funny. Reply in 2 short sentences max, under 40 words."},
                {"role": "user", "content": q}
            ]
        }
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=15)
        print(f"Groq status: {r.status_code} body: {r.text[:500]}")
        j = r.json()
        return j['choices'][0]['message']['content']
    except Exception as e:
        print(f"Groq error: {e}")
        return f"My brain glitched but I heard you: {q}. Try again!"

def send_audio(to, text):
    try:
        tts = gTTS(text=text, lang='en')
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            tts.save(fp.name)
            # upload audio
            url = f"https://graph.facebook.com/v20.0/{PHONE_ID}/media"
            headers = {"Authorization": f"Bearer {TOKEN}"}
            with open(fp.name, 'rb') as f:
                files = {'file': ('audio.mp3', f, 'audio/mpeg')}
                data = {'type': 'audio/mpeg', 'messaging_product': 'whatsapp'}
                up = requests.post(url, headers=headers, files=files, data=data)
            print(f"Upload status: {up.text[:500]}")
            media_id = up.json().get('id')
            # send audio
            send_url = f"https://graph.facebook.com/v20.0/{PHONE_ID}/messages"
            payload = {"messaging_product": "whatsapp", "to": to, "type": "audio", "audio": {"id": media_id}}
            r = requests.post(send_url, headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}, json=payload)
            print(f"Send status: {r.text[:500]}")
    except Exception as e:
        print(f"Send audio error: {e}")

@app.route("/")
def home():
    return "Bot is Live!"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Verify failed", 403
    data = request.json
    print(f"Webhook data: {str(data)[:1000]}")
    try:
        entry = data['entry'][0]['changes'][0]['value']
        if 'messages' in entry:
            msg = entry['messages'][0]
            from_num = msg['from']
            text = msg['text']['body'] if msg['type'] == 'text' else "voice note"
            reply = ask_groq(text)
            send_audio(from_num, reply)
    except Exception as e:
        print(f"Webhook error: {e}")
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
