import os
from twilio.rest import Client

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "YOUR_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "YOUR_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

def send_whatsapp_message(to_phone: str, message_body: str):
    if not TWILIO_ACCOUNT_SID or TWILIO_ACCOUNT_SID == "YOUR_ACCOUNT_SID":
        print("\n" + "=" * 60)
        print(f"📱 [WHATSAPP-SIMULATION DEUTSCH] An: {to_phone}")
        print("-" * 60)
        print(message_body)
        print("=" * 60 + "\n")
        return True

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        if not to_phone.startswith("whatsapp:"):
            to_phone = f"whatsapp:{to_phone}"

        message = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER, body=message_body, to=to_phone
        )
        print(f"✅ WhatsApp erfolgreich gesendet! SID: {message.sid}")
        return True
    except Exception as e:
        print(f"❌ Fehler beim Senden von WhatsApp: {e}")
        return False

def send_client_tracking_whatsapp(client_phone: str, client_name: str, order_title: str, tracking_link: str):
    message = (
        f"Hallo {client_name}! 👋\n\n"
        f"Gute Nachrichten: Unser Handwerker ist jetzt unterwegs zu Ihnen für den Auftrag: *{order_title}*.\n\n"
        f"📍 Sie können die Anfahrt live auf der Karte verfolgen:\n"
        f"{tracking_link}\n\n"
        f"Vielen Dank für Ihr Vertrauen!"
    )
    return send_whatsapp_message(client_phone, message)

def send_master_new_order_whatsapp(master_phone: str, master_name: str, order_title: str, address: str):
    message = (
        f"Hallo {master_name}! 👷‍♂️\n\n"
        f"Ihnen wurde ein neuer Auftrag zugewiesen:\n"
        f"📋 *Auftrag:* {order_title}\n"
        f"📍 *Adresse:* {address}\n\n"
        f"Bitte öffnen Sie die App, um Details einzusehen und die Anfahrt zu starten."
    )
    return send_whatsapp_message(master_phone, message)
