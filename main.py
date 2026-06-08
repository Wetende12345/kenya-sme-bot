from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

app = FastAPI(title="Kenya SME WhatsApp Bot")

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")


def send_message(to: str, text: str):
    if not ACCESS_TOKEN or not PHONE_NUMBER_ID:
        print("❌ Tokens missing")
        return
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    r = requests.post(url, json=payload, headers=headers)
    print(f"Send to {to}: {r.status_code}")


@app.get("/webhook")
async def verify(request: Request):
    if request.query_params.get("hub.verify_token") == VERIFY_TOKEN:
        print("✅ Verified")
        return int(request.query_params.get("hub.challenge"))
    raise HTTPException(403)


@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        messages = data.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {}).get("messages", [])
        
        if messages:
            msg = messages[0]
            from_number = msg.get("from")
            text = msg.get("text", {}).get("body", "").strip().lower()

            print(f"📱 From {from_number}: {text}")

            if text in ["hi", "hello", "hey", "menu", "start"]:
                reply = """👋 *Welcome to Our Store!*

1. 🆕 New Arrivals
2. 🔥 Today's Discounts
3. 📍 Our Stores / Locations
4. 💰 My Orders
5. 👟 My Size & Preferences

Reply with a *number* or type your request."""
                send_message(from_number, reply)

            elif text == "1":
                send_message(from_number, "🆕 New arrivals just came in!\n\n- Nike Air Max\n- Adidas Samba\n- Jordan 1 Low\n\nWhich one interests you?")
            elif text == "2":
                send_message(from_number, "🔥 This week discounts:\n\n• 20% off all sneakers\n• Buy 2 get 1 free on selected items\n\nReply *Discounts* for full list.")
            else:
                send_message(from_number, "Thank you! Reply with *Menu* to see options 😊")

    except Exception as e:
        print("Error:", e)

    return JSONResponse(status_code=200, content={"status": "ok"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
