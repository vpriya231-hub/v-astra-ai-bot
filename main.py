from flask import Flask, request
import os, requests

app = Flask(__name__)

VERIFY_TOKEN = "vastra123"
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# --- ഇതാണ് GEMINI AI MODEL LOGIC ---
def ask_ai(user_message):
    try:
        # Model: gemini-3.7-flash (2026 latest)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.7-flash:generateContent?key={GEMINI_API_KEY}"

        payload = {
            "contents": [{"parts": [{"text": user_message}]}],
            "systemInstruction": {"parts": [{"text": "You are V Astra AI, friendly helpful assistant. Reply in user's language."}]}
        }

        res = requests.post(url, json=payload, timeout=30)
        data = res.json()

        if 'candidates' in data:
            return data['candidates'][0]['content']['parts'][0]['text']
        else:
            print(f"Gemini Error: {data}")
            return "AI error, try again"

    except Exception as e:
        print(f"Error: {e}")
        return "Sorry, issue. Try again!"

def send_whatsapp(to, text):
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": to, "text": {"body": text[:4000]}}
    requests.post(url, headers=headers, json=payload)

@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge"), 200
    return "Failed", 403

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data and 'messages' in str(data):
        try:
            value = data['entry'][0]['changes'][0]['value']
            if 'messages' in value:
                from_number = value['messages'][0]['from']
                msg_body = value['messages'][0]['text']['body']
                reply = ask_ai(msg_body)
                send_whatsapp(from_number, reply)
        except Exception as e:
            print(e)
    return "OK", 200

@app.route('/')
def home():
    return "V Astra Bot Live with Gemini 2.0!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
