from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from transformers import pipeline

app = FastAPI(title="AI Detector — Только проверка")

# Загружаем модель
try:
    detector = pipeline(
        "text-classification",
        model="cointegrated/rubert-tiny",
        tokenizer="cointegrated/rubert-tiny"
    )
except Exception as e:
    print(f"Ошибка загрузки модели: {e}")
    detector = None

# Подключаем шаблоны и статику
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/check")
async def check_text(text: str = Form(...)):
    # Ограничиваем длину текста
    truncated_text = text[:500]
    result = {"text_length": len(text)}

    if detector:
        try:
            local_result = detector(truncated_text)[0]
            result["ai_score_local"] = round(local_result['score'] * 100, 2)
            result["is_ai_local"] = local_result['label'] == 'generated'
        except Exception as e:
            result["ai_score_local"] = None
            result["error_local"] = str(e)
    else:
        result["ai_score_local"] = None
        result["error_local"] = "Модель не загружена"

    return result