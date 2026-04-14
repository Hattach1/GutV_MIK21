import re


EMOTIONAL_WORDS = {
    "важно", "срочно", "лучший", "невероятный", "потрясающий", "удивительный",
    "яркий", "мощный", "эффективный", "простой", "быстрый", "удобный",
    "уникальный", "впечатляющий", "интересный", "полезный", "крутой"
}

CTA_WORDS = {
    "попробуй", "попробуйте", "узнай", "узнайте", "смотри", "смотрите",
    "подпишись", "подпишитесь", "закажи", "закажите", "открой", "откройте",
    "скачай", "скачайте", "выбери", "выберите", "начни", "начните"
}


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def split_sentences(text: str) -> list[str]:
    sentences = re.split(r"[.!?]+", text)
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def extract_words(text: str) -> list[str]:
    return re.findall(r"[А-Яа-яA-Za-zЁё]+", text.lower())


def safe_divide(a: float, b: float) -> float:
    return a / b if b else 0.0


def clamp(value: float, min_value: float = 0.0, max_value: float = 1.0) -> float:
    return max(min_value, min(value, max_value))