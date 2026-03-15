
# chabito-telegram

Chatbot de Telegram en Python que reenvía todos los mensajes al backend vía WebSockets.

Por defecto se conecta a `ws://127.0.0.1:8001/ws/echo` (ver `chabito-backend-2`).

## Requisitos

- Python 3.11+
- Un bot de Telegram y su token (`TELEGRAM_BOT_TOKEN`)
- Backend WebSocket corriendo (`BACKEND_WS_URL`)

## Instalación

```bash
cd chabito-telegram
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuración

Copia las variables de `.env.example` a tu `.env` y ajusta valores:

- `TELEGRAM_BOT_TOKEN` (requerido)
- `BACKEND_WS_URL` (opcional)

## Ejecutar

```bash
cd chabito-telegram
source .venv/bin/activate
python main.py
```

Si el backend es el echo server:

```bash
cd chabito-backend-2
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```
