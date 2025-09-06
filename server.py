# server.py
from aiohttp import web
import asyncio

# Хранилище событий
events = []
lock = asyncio.Lock()

# === Middleware для CORS ===
@web.middleware
async def cors_middleware(request, handler):
    response = await handler(request)
    response.headers['Access-Control-Allow-Origin'] = 'https://cameri-github-io.onrender.com'
    response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# === Обработка OPTIONS (preflight) ===
async def handle_options(request):
    return web.Response(
        headers={
            'Access-Control-Allow-Origin': 'https://cameri-github-io.onrender.com',
            'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
    )

# === Принимаем отчёт ===
async def report_event(request):
    try:
        data = await request.json()
        async with lock:
            events.append(data)
        return web.json_response(
            {"status": "ok"},
            headers={'Access-Control-Allow-Origin': 'https://cameri-github-io.onrender.com'}
        )
    except Exception as e:
        return web.json_response(
            {"error": str(e)},
            status=400,
            headers={'Access-Control-Allow-Origin': 'https://cameri-github-io.onrender.com'}
        )

# === Отдаём события боту ===
async def get_events(request):
    async with lock:
        new_events = events.copy()
        events.clear()
    return web.json_response(
        {"events": new_events},
        headers={'Access-Control-Allow-Origin': 'https://cameri-github-io.onrender.com'}
    )

# === Создаём приложение с CORS ===
app = web.Application(middlewares=[cors_middleware])
app.router.add_options('/report', handle_options)
app.router.add_options('/events', handle_options)
app.router.add_post('/report', report_event)
app.router.add_get('/events', get_events)

if __name__ == '__main__':
    web.run_app(app, port=10000)
