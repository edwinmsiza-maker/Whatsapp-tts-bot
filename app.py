
from flask import Flask, request, jsonify
import os, requests, tempfile
from gtts import gTTS

app = Flask(__name__)
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "tts_fun_verify_2024")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "1297192166806568")

@app.route('/')
def home():
    return "Bot Live 1297192166806568"

@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "fail", 403

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print(data)
    try:
        val = data['entry'][0]['changes'][0]['value']
        if 'messages' in val:
            msg = val['messages'][0]
            frm = msg['from']
            if msg['type'] == 'audio':
                mid = msg['audio']['id']
                h = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
                r = requests.get(f"https://graph.facebook.com/v20.0/{mid}", headers=h).json()
                aurl = r.get('url')
                adata = requests.get(aurl, headers=h).content
                with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as t:
                    t.write(adata)
                tts = gTTS("Ha ha Uncle Hloni I got your voice note!", lang='en', tld='com.au')
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as m:
                    tts.save(m.name)
                    mpath = m.name
                up_url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/media"
                with open(mpath, 'rb') as f:
                    files = {'file': ('a.mp3', f, 'audio/mpeg')}
                    d = {'type': 'audio/mpeg', 'messaging_product': 'whatsapp'}
                    up = requests.post(up_url, headers=h, files=files, data=d).json()
                nid = up.get('id')
                if nid:
                    s_url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
                    p = {"messaging_product": "whatsapp", "to": frm, "type": "audio", "audio": {"id": nid}}
                    requests.post(s_url, headers=h, json=p)
    except Exception as e:
        print(e)
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
