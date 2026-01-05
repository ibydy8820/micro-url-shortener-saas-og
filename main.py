import string
import random
from typing import Dict
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import uvicorn

# 1. Инициализация приложения
app = FastAPI(
    title="Micro URL Shortener API",
    description="MVP версия сокращателя ссылок с хранением в памяти",
    version="0.1.0"
)

# 2. Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory хранилище: {short_code: original_url}
url_db: Dict[str, str] = {}

# Модели данных
class ShortenRequest(BaseModel):
    url: HttpUrl

class ShortenResponse(BaseModel):
    short_code: str
    original_url: str

# Вспомогательная функция
def generate_code(length: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    while True:
        code = "".join(random.choices(chars, k=length))
        if code not in url_db:
            return code

# 3. Эндпоинты

@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "URL Shortener API is running",
        "links_active": len(url_db)
    }

@app.post("/api/shorten", response_model=ShortenResponse, status_code=201)
async def shorten_url(payload: ShortenRequest):
    """
    Принимает URL, генерирует уникальный код и сохраняет в памяти.
    """
    # Преобразуем HttpUrl в строку для сохранения
    url_str = str(payload.url)
    
    # Генерируем код
    code = generate_code()
    
    # Сохраняем
    url_db[code] = url_str
    
    return ShortenResponse(
        short_code=code,
        original_url=url_str
    )

@app.get("/api/{short_code}")
async def redirect_to_original(short_code: str):
    """
    Перенаправляет пользователя на оригинальный URL.
    """
    if short_code not in url_db:
        raise HTTPException(status_code=404, detail="Ссылка не найдена")
    
    target_url = url_db[short_code]
    
    # Используем 307 Temporary Redirect, чтобы браузеры не кешировали редирект навсегда
    return RedirectResponse(url=target_url, status_code=307)

# 4. Запуск (для локальной отладки)
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)