from app.analyzer import analyze_text
from app.model import predict
from app.utils import extract_words


def adapt_recommendations_by_class(predicted_class: str, recommendations: list[str]) -> list[str]:
    adapted = list(recommendations)

    if predicted_class == "low":
        adapted.insert(0, "Текст классифицирован как низкоэффективный: стоит усилить пользу, конкретику и вовлечение.")
    elif predicted_class == "medium":
        adapted.insert(0, "Текст классифицирован как среднеэффективный: базовая структура есть, но подачу можно сделать сильнее.")
    elif predicted_class == "high":
        adapted.insert(0, "Текст классифицирован как высокоэффективный: текст выглядит достаточно убедительно и понятно.")

    return adapted[:5]


def detect_strengths_and_weaknesses(features: dict, scores: dict) -> tuple[list[str], list[str]]:
    strengths = []
    weaknesses = []

    if scores["readability_score"] > 0.7:
        strengths.append("Текст легко читается.")
    else:
        weaknesses.append("Читаемость можно улучшить за счёт упрощения формулировок.")

    if 6 <= features["avg_sentence_length"] <= 18:
        strengths.append("Длина предложений выглядит сбалансированной.")
    else:
        weaknesses.append("Структура предложений может ухудшать восприятие текста.")

    if features["question_count"] > 0:
        strengths.append("Есть вопросительная конструкция, усиливающая вовлечение.")
    else:
        weaknesses.append("Не хватает вопроса, который мог бы вовлечь аудиторию.")

    if features["cta_word_count"] > 0:
        strengths.append("В тексте присутствует призыв к действию.")
    else:
        weaknesses.append("Не хватает призыва к действию.")

    if scores["overall_score"] > 0.75:
        strengths.append("Текст в целом выглядит эффективным.")
    elif scores["overall_score"] < 0.4:
        weaknesses.append("Текст в целом выглядит малоэффективным.")

    return strengths[:4], weaknesses[:4]


def get_top_keywords(text: str, limit: int = 5) -> list[str]:
    words = extract_words(text)
    stop_words = {
        "и", "в", "на", "с", "по", "для", "как", "что", "это", "к", "у", "из",
        "а", "но", "или", "не", "за", "от", "до", "под", "при", "о", "об",
        "ваш", "ваша", "ваше", "ваши", "который", "которая", "которые"
    }

    filtered = [word for word in words if len(word) > 3 and word not in stop_words]

    freq = {}
    for word in filtered:
        freq[word] = freq.get(word, 0) + 1

    sorted_words = sorted(freq.items(), key=lambda x: (-x[1], x[0]))
    return [word for word, _ in sorted_words[:limit]]


def build_feature_summary(features: dict, scores: dict) -> dict:
    return {
        "text_length": features["word_count"],
        "readability_level": "high" if scores["readability_score"] >= 0.75 else "medium" if scores["readability_score"] >= 0.45 else "low",
        "engagement_level": "high" if scores["engagement_score"] >= 0.75 else "medium" if scores["engagement_score"] >= 0.45 else "low",
        "emotional_level": "high" if scores["emotional_score"] >= 0.55 else "medium" if scores["emotional_score"] >= 0.25 else "low",
        "has_question": features["question_count"] > 0,
        "has_cta": features["cta_word_count"] > 0,
    }


def build_model_explanation(predicted_class: str, features: dict, scores: dict) -> str:
    reasons = []

    if scores["readability_score"] >= 0.75:
        reasons.append("хорошая читаемость")
    if scores["engagement_score"] >= 0.5:
        reasons.append("признаки вовлечения")
    if features["cta_word_count"] > 0:
        reasons.append("наличие призыва к действию")
    if features["question_count"] > 0:
        reasons.append("вопросительная конструкция")
    if scores["emotional_score"] >= 0.3:
        reasons.append("эмоциональные акценты")

    if not reasons:
        reasons.append("нейтральная подача без сильных убедительных сигналов")

    reasons_text = ", ".join(reasons[:4])

    if predicted_class == "high":
        return f"Модель отнесла текст к классу high, потому что в нём обнаружены {reasons_text}."
    if predicted_class == "medium":
        return f"Модель отнесла текст к классу medium: текст выглядит умеренно эффективным, так как в нём присутствуют {reasons_text}."
    return f"Модель отнесла текст к классу low, поскольку текст выглядит недостаточно выразительным и содержит только {reasons_text}."


def analyze_advanced(text: str) -> dict:
    prediction_data = predict(text)
    analysis_data = analyze_text(text)

    score_pack = {
        "readability_score": analysis_data["readability_score"],
        "emotional_score": analysis_data["emotional_score"],
        "engagement_score": analysis_data["engagement_score"],
        "overall_score": analysis_data["overall_score"],
    }

    strengths, weaknesses = detect_strengths_and_weaknesses(
        analysis_data["features"],
        score_pack,
    )

    recommendations = adapt_recommendations_by_class(
        prediction_data["predicted_class"],
        analysis_data["recommendations"],
    )

    return {
    "predicted_class": prediction_data["predicted_class"],
    "probabilities": prediction_data["probabilities"],
    "readability_score": analysis_data["readability_score"],
    "emotional_score": analysis_data["emotional_score"],
    "engagement_score": analysis_data["engagement_score"],
    "overall_score": analysis_data["overall_score"],
    "features": analysis_data["features"],
    "strengths": strengths,
    "weaknesses": weaknesses,
    "recommendations": recommendations,
    "top_keywords": get_top_keywords(text),
    "feature_summary": build_feature_summary(analysis_data["features"], score_pack),
    "model_explanation": build_model_explanation(
        prediction_data["predicted_class"],
        analysis_data["features"],
        score_pack,
    ),
}