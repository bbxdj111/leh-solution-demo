import os
from groq import Groq

GROQ_API_KEY = "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"

try:
    client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    client = None
    print(f"Ошибка инициализации Groq: {e}")


def translate_text_with_ai(text: str, target_language: str) -> str:
    """Универсальный переводчик через Groq AI"""
    if not text or not client:
        return text

    try:
        prompt = f"""
        Ты — профессиональный технический переводчик.
        Переведи следующий текст на язык: {target_language}.
        Если текст УЖЕ написан на языке {target_language}, верни его без изменений.
        ВАЖНО: Верни ТОЛЬКО готовый текст. Без пояснений, вводных слов и кавычек.

        Текст для перевода:
        {text}
        """

        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.1,
        )

        return chat_completion.choices[0].message.content.strip()

    except Exception as e:
        print(f"Ошибка перевода через Groq: {e}")
        return text


def analyze_order_with_ai(title: str, description: str) -> str:
    """Анализ заявки через Groq"""
    if not client:
        return f"1. Приоритет: Средний\n2. Причина: Проблема с '{title}'."

    try:
        prompt = f"""
        Проанализируй проблему выездного ремонта:
        Заголовок: {title}
        Описание: {description}

        Дай краткий и четкий ответ по пунктам на русском языке:
        1. Приоритет (Низкий/Средний/Высокий)
        2. Возможная причина
        3. Рекомендуемый специалист или инструмент
        """

        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
        )

        return chat_completion.choices[0].message.content.strip()

    except Exception as e:
        print(f"Ошибка анализа: {e}")
        return "Анализ недоступен."