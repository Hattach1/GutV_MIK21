from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.analyzer import analyze_text
from app.model import predict
from app.schemas import (
    AdvancedAnalysisResponse,
    AnalysisResponse,
    PredictionResponse,
    TextRequest,
)
from app.service import analyze_advanced

app = FastAPI(
    title="Content Effectiveness API",
    description="API for analyzing textual content effectiveness",
    version="0.5.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
def root():
    return {"message": "Content Effectiveness API is running"}


@app.get("/ui", response_class=HTMLResponse)
def ui(request: Request):
    return templates.TemplateResponse(request, "index.html", {"request": request})


@app.post("/analyze", response_model=AnalysisResponse)
def analyze(request: TextRequest):
    return analyze_text(request.text)


@app.post("/predict", response_model=PredictionResponse)
def predict_endpoint(request: TextRequest):
    return predict(request.text)


@app.post("/analyze-advanced", response_model=AdvancedAnalysisResponse)
def analyze_advanced_endpoint(request: TextRequest):
    return analyze_advanced(request.text)