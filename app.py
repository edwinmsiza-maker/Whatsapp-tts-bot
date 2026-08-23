from flask import Flask, request
import requests
import openai

app = Flask(__name__)

# --- PUT YOUR KEYS HERE ---
WHATSAPP_TOKEN = "YOUR_META_TOKEN"
PHONE_ID = "YOUR_PHONE_ID"
ELEVENLABS_KEY = "YOUR_ELEVENLABS_KEY"
OPENAI_KEY = "YOUR_OPENAI_KEY"

openai.api_key = OPENAI_KEY
VOICE_ID = "21m00Tcm4TlvDq8ikWAM" # Change voice here

# --- 1. AI Brain (Tumi) ---
def get_ai_answer(user_text):
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are Tumi, a friendly assistant from Johannesburg. Answer briefly, in same language as user. If user speaks Sesotho, answer in Sesotho. Keep answers under 50 words so voice note is short."},
            {"role": "user", "content": user_text}
        ]
    )
    return response.choices[0].message.content

# --- 2. Text to Voice ---
def text_to_speech(text):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {"xi-api-key": ELEVENLABS_KEY, "Content-Type": "application/json"}
    data = {"text": text, "model_id": "eleven_multilingual_v2"}
    r = requests.post(url, json=data, headers=headers)
    with open("/tmp/voice.mp3", "wb") as f:
        f.write(r.content)
    return "/tmp/voice.mp3"

# --- 3. Send Voice on WhatsApp ---
def send_voice(to, audio_path):
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    upload_url = f"https://graph.facebook.com/v20.0/{PHONE_ID}/media"
    with open(audio_path, 'rb') as f:
        files = {'file': (audio_path, f, 'audio/mpeg')}
        data = {'messaging_product': 'whatsapp', 'type': 'audio'}
        media_id = requests.post(upload_url, headers=headers, files=files, data=data).json()['id']

    send_url = f"https://graph.facebook.com/v20.0/{PHONE_ID}/messages"
    payload = {"messaging_product": "whatsapp", "to": to, "type": "audio", "audio": {"id": media_id}}
    requests.post(send_url, json=payload, headers=headers)

@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    if request.method == "GET": # For Meta verification
        return request.args.get("hub.challenge")

    data = request.json
    try:
        msg = data['entry'][0]['changes'][0]['value']['messages'][0]
        from_num = msg['from']
        user_text = msg['text']['body']

        print(f"User said: {user_text}")
        ai_answer = get_ai_answer(user_text)
        print(f"AI answers: {ai_answer}")

        audio = text_to_speech(ai_answer)
        send_voice(from_num, audio)

    except Exception as e:
        print(e)
    return "OK", 200

app.run(host="0.0.0.0", port=5000)
