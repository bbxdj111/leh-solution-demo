import os
import requests

GREEN_API_INSTANCE_ID = os.getenv("GREEN_API_INSTANCE_ID", "")
GREEN_API_TOKEN = os.getenv("GREEN_API_TOKEN", "")

def send_whatsapp_message(phone_number: str, message: str) -> dict:
    """
    Отправка WhatsApp сообщения клиенту через Green API.
    Если токены не заданы в .env, функция работает в режиме симуляции (лог в консоль).
    """
    if not GREEN_API_INSTANCE_ID or not GREEN_API_TOKEN:
        print(f"📱 [WhatsApp Simulation] Сообщение на {phone_number}:\n{message}\n")
        return {"status": "simulated", "phone": phone_number, "message": message}

    # Очистка номера от лишних символов
    clean_phone = "".join(filter(str.isdigit, phone_number))
    chat_id = f"{clean_phone}@c.us"

    url = f"https://api.green-api.com/waInstance{GREEN_API_INSTANCE_ID}/sendMessage/{GREEN_API_TOKEN}"
    
    payload = {
        "chatId": chat_id,
        "message": message
    }
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Ошибка отправки WhatsApp: {e}")
        return {"status": "error", "message": str(e)}

def send_invoice_and_tracking_link(phone_number: str, client_name: str, order_title: str, order_id: str, domain: str = "http://localhost:8000") -> dict:
    """
    Формирует и отправляет клиенту ссылки на PDF-счёт и онлайн-трекинг мастера.
    """
    tracking_url = f"{domain}/client_track.html?order_id={order_id}"
    invoice_url = f"{domain}/api/invoices/generate/{order_id}"

    message = (
        f"Здравствуйте, {client_name}!\n\n"
        f"Статус вашего заказа '{order_title}' обновлён.\n\n"
        f"📍 Отследить местоположение мастера: {tracking_url}\n"
        f"📄 Скачать квитанцию / PDF Rechnung: {invoice_url}\n\n"
        f"С уважением, Ваша сервисная служба!"
    )

    return send_whatsapp_message(phone_number, message)