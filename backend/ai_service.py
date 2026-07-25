import os
import base64
from google import genai
from google.genai import types

# Инициализация клиента Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

def get_gemini_client():
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY не установлен в файле .env")
    return genai.Client(api_key=GEMINI_API_KEY)

# --- 1. AI Переводчик заметок (DE / UA / EN) ---
def translate_text(text: str, target_language: str = "DE") -> str:
    """
    Переводит технические заметки мастера на целевой язык (по умолчанию немецкий DE).
    """
    try:
        client = get_gemini_client()
        prompt = f"""
        Ты профессиональный технический переводчик для выездных сервисных инженеров.
        Переведи следующий текст на язык '{target_language}'. 
        Сохраняй технические термины, названия деталей и краткость.
        Текст для перевода:
        "{text}"
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        print(f"Ошибка AI перевода: {e}")
        return f"[Ошибка AI перевода]: {text}"

# --- 2. Gemini Vision OCR: Сканер шильдиков и оборудования ---
def scan_equipment_label(image_bytes: bytes) -> dict:
    """
    Анализирует фотографию шильдика/таблички оборудования через Gemini Vision
    и извлекает модель, серийный номер и производителя.
    """
    try:
        client = get_gemini_client()
        
        prompt = """
        Проанализируй изображение шильдика/паспортной таблички оборудования.
        Найди и извлеки следующие данные в формате текста:
        - Производитель (Brand/Manufacturer)
        - Модель (Model)
        - Серийный номер (Serial Number / S/N)
        - Сетевое напряжение / Мощность (Specs)

        Верни ответ строго в формате:
        Производитель: <текст>
        Модель: <текст>
        Серийный номер: <текст>
        Характеристики: <текст>
        """

        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type="image/jpeg"
        )

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[image_part, prompt]
        )
        
        return {
            "status": "success",
            "raw_text": response.text.strip()
        }
    except Exception as e:
        print(f"Ошибка Gemini Vision OCR: {e}")
        return {
            "status": "error",
            "message": f"Не удалось распознать текст: {str(e)}"
        }