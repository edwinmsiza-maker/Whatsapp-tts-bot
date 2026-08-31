from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = "tts_fun_verify_2024"

@app.route('/')
def home():
    return "Bot is Live!", 200

@app.route('/webhook', methods=['GET'])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("WEBHOOK VERIFIED!")
        return challenge, 200
    return "Verification failed", 403

@app.route('/webhook', methods=['POST'])
def incoming():
    print(request.get_json())
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
