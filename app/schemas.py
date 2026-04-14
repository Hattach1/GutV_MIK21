from pydantic import BaseModel, Field


class TextRequest(BaseModel):
    text: str = Field(..., min_length=10, description="Text for analysis")


class TextFeatures(BaseModel):
    char_count: int
    word_count: int
    sentence_count: int
    avg_word_length: float
    avg_sentence_length: float
    exclamation_count: int
    question_count: int
    emotional_word_count: int
    cta_word_count: int
    emotional_ratio: float
    cta_ratio: float
    unique_ratio: float


class AnalysisResponse(BaseModel):
    readability_score: float
    emotional_score: float
    engagement_score: float
    overall_score: float
    features: TextFeatures
    recommendations: list[str]


class PredictionResponse(BaseModel):
    predicted_class: str
    probabilities: dict[str, float]


class FeatureSummary(BaseModel):
    text_length: int
    readability_level: str
    engagement_level: str
    emotional_level: str
    has_question: bool
    has_cta: bool


class AdvancedAnalysisResponse(BaseModel):
    predicted_class: str
    probabilities: dict[str, float]
    readability_score: float
    emotional_score: float
    engagement_score: float
    overall_score: float
    features: TextFeatures
    strengths: list[str]
    weaknesses: list[str]
    recommendations: list[str]
    top_keywords: list[str]
    feature_summary: FeatureSummary
    model_explanation: str