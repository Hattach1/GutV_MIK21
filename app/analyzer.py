from app.utils import (
    CTA_WORDS,
    EMOTIONAL_WORDS,
    clamp,
    extract_words,
    normalize_text,
    safe_divide,
    split_sentences,
)


def extract_features(text: str) -> dict:
    normalized_text = normalize_text(text)
    words = extract_words(normalized_text)
    sentences = split_sentences(normalized_text)

    char_count = len(normalized_text)
    word_count = len(words)
    sentence_count = len(sentences)

    avg_word_length = safe_divide(sum(len(word) for word in words), word_count)
    avg_sentence_length = safe_divide(word_count, sentence_count)

    exclamation_count = normalized_text.count("!")
    question_count = normalized_text.count("?")

    emotional_word_count = sum(1 for word in words if word in EMOTIONAL_WORDS)
    cta_word_count = sum(1 for word in words if word in CTA_WORDS)

    emotional_ratio = safe_divide(emotional_word_count, word_count)
    cta_ratio = safe_divide(cta_word_count, word_count)

    unique_words = len(set(words))
    unique_ratio = safe_divide(unique_words, word_count)

    return {
        "char_count": char_count,
        "word_count": word_count,
        "sentence_count": sentence_count,
        "avg_word_length": round(avg_word_length, 3),
        "avg_sentence_length": round(avg_sentence_length, 3),
        "exclamation_count": exclamation_count,
        "question_count": question_count,
        "emotional_word_count": emotional_word_count,
        "cta_word_count": cta_word_count,
        "emotional_ratio": round(emotional_ratio, 3),
        "cta_ratio": round(cta_ratio, 3),
        "unique_ratio": round(unique_ratio, 3),
    }

def calculate_readability_score(features: dict) -> float:
    avg_sentence_length = features["avg_sentence_length"]
    avg_word_length = features["avg_word_length"]

    score = 1.0

    if avg_sentence_length > 22:
        score -= 0.35
    elif avg_sentence_length > 16:
        score -= 0.2
    elif avg_sentence_length < 4:
        score -= 0.15

    if avg_word_length > 7:
        score -= 0.25
    elif avg_word_length > 6:
        score -= 0.1

    return round(clamp(score), 3)


def calculate_emotional_score(features: dict) -> float:
    score = 0.0

    score += min(features["exclamation_count"] * 0.12, 0.36)
    score += min(features["emotional_ratio"] * 4, 0.5)

    return round(clamp(score), 3)


def calculate_engagement_score(features: dict) -> float:
    score = 0.0

    if features["question_count"] > 0:
        score += 0.3

    score += min(features["cta_ratio"] * 8, 0.4)

    if 30 <= features["word_count"] <= 120:
        score += 0.3
    elif 15 <= features["word_count"] < 30:
        score += 0.15
    elif features["word_count"] > 180:
        score -= 0.15

    return round(clamp(score), 3)


def generate_recommendations(features: dict, scores: dict) -> list[str]:
    recommendations = []

    word_count = features["word_count"]
    avg_sentence_length = features["avg_sentence_length"]
    question_count = features["question_count"]
    cta_word_count = features["cta_word_count"]
    exclamation_count = features["exclamation_count"]
    emotional_word_count = features["emotional_word_count"]

    if word_count < 12:
        recommendations.append("Текст слишком короткий: стоит добавить больше содержания и конкретики.")
    elif word_count > 120:
        recommendations.append("Текст получился длинным: можно сократить его для более быстрого восприятия.")

    if avg_sentence_length > 20:
        recommendations.append("Предложения слишком длинные: текст можно сделать проще и динамичнее.")
    elif avg_sentence_length < 4:
        recommendations.append("Предложения очень короткие: можно добавить немного связности между мыслями.")

    if question_count == 0 and scores["engagement_score"] < 0.5:
        recommendations.append("Для усиления вовлечения можно добавить вопрос к аудитории.")

    if cta_word_count == 0 and scores["engagement_score"] < 0.6:
        recommendations.append("Не хватает призыва к действию: можно добавить формулировки вроде «попробуйте» или «узнайте».")

    if emotional_word_count == 0 and exclamation_count == 0 and scores["emotional_score"] < 0.2:
        recommendations.append("Текст выглядит нейтрально: можно добавить более выразительные слова или акценты.")
    elif emotional_word_count > 3 and exclamation_count > 2:
        recommendations.append("Эмоциональных акцентов довольно много: стоит следить, чтобы текст не выглядел перегруженным.")

    if scores["readability_score"] < 0.5:
        recommendations.append("Читаемость можно улучшить за счёт более простых слов и более коротких предложений.")

    if scores["overall_score"] > 0.75 and len(recommendations) < 2:
        recommendations.append("Текст выглядит достаточно сильным и сбалансированным по основным критериям.")

    if not recommendations:
        recommendations.append("Текст в целом сбалансирован, серьёзных проблем по базовым критериям не обнаружено.")

    return recommendations[:4]


def analyze_text(text: str) -> dict:
    features = extract_features(text)

    readability_score = calculate_readability_score(features)
    emotional_score = calculate_emotional_score(features)
    engagement_score = calculate_engagement_score(features)

    overall_score = round(
        0.4 * readability_score +
        0.25 * emotional_score +
        0.35 * engagement_score,
        3
    )

    scores = {
        "readability_score": readability_score,
        "emotional_score": emotional_score,
        "engagement_score": engagement_score,
        "overall_score": overall_score,
    }

    recommendations = generate_recommendations(features, scores)

    return {
    "readability_score": readability_score,
    "emotional_score": emotional_score,
    "engagement_score": engagement_score,
    "overall_score": overall_score,
    "features": features,
    "recommendations": recommendations,
}


def detect_strengths_and_weaknesses(features: dict, scores: dict) -> tuple[list[str], list[str]]:
    strengths = []
    weaknesses = []

    # Читаемость
    if scores["readability_score"] > 0.7:
        strengths.append("Текст легко читается и хорошо воспринимается.")
    else:
        weaknesses.append("Читаемость можно улучшить за счёт упрощения структуры.")

    # Длина текста
    if 20 <= features["word_count"] <= 100:
        strengths.append("Длина текста оптимальна для восприятия.")
    else:
        weaknesses.append("Длина текста может быть неоптимальной для вовлечения.")

    # Вовлечение
    if features["question_count"] > 0:
        strengths.append("Используется вопрос, что повышает вовлечённость.")
    else:
        weaknesses.append("Отсутствует вопрос, можно усилить вовлечение аудитории.")

    # CTA
    if features["cta_word_count"] > 0:
        strengths.append("Присутствует призыв к действию.")
    else:
        weaknesses.append("Не хватает призыва к действию.")

    # Эмоциональность
    if scores["emotional_score"] > 0.4:
        strengths.append("Текст содержит эмоциональные акценты.")
    else:
        weaknesses.append("Текст выглядит нейтрально, можно добавить выразительности.")

    # Общая оценка
    if scores["overall_score"] > 0.75:
        strengths.append("Текст в целом выглядит эффективным.")
    elif scores["overall_score"] < 0.4:
        weaknesses.append("Текст в целом выглядит малоэффективным.")

    return strengths[:4], weaknesses[:4]