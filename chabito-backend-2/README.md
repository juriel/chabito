# chabito-backend-2

Python WebSocket echo server with FastAPI + Uvicorn.

## Install

```bash
cd chabito-backend-2
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

## Endpoints

- `GET /health`
- `WS /ws/echo`

## Expected WebSocket Payload (`InputMessageDTO`)

```json
{
  "message": "hola",
  "user_id": "573001112233@s.whatsapp.net",
  "sender_nickname": "Juriel",
  "sender_jid": "573001112233@s.whatsapp.net",
  "mime_type": null,
  "file_base64": null
}
```

The server validates the payload and echoes it back in JSON.

