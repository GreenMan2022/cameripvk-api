# server.py — простой HTTP-сервер для приёма данных
from aiohttp import web
import json
import asyncio

# Хранилище событий (в реальном проекте — база данных)
events = []
lock = asyncio.Lock()

# === Эндпоинт для WebApp ===
async def report_event(request):
    try:
        data = await request.json()
        async with lock:
            events.append({
                "type": data.get("type"),
                "camera": data.get("camera"),
                "timestamp": data.get("timestamp"),
                "user": data.get("user", {})
            })
        return web.json_response({"status": "ok"})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=400)

# === Эндпоинт для бота (получение новых событий) ===
async def get_events(request):
    async with lock:
        new_events = events.copy()
        events.clear()  # Очищаем после отправки
    return web.json_response({"events": new_events})

# === Запуск сервера ===
app = web.Application()
app.router.add_post('/report', report_event)
app.router.add_get('/events', get_events)

if __name__ == '__main__':
    web.run_app(app, port=10000)
