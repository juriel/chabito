# chabito-backend-2

Python WebSocket server (FastAPI + Uvicorn) que valida `InputMessageDTO` y responde usando un agente LangChain con memoria por `user_id`.

## Install

```bash
cd chabito-backend-2
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn chabito_back.webserver.webserver_main:webserver --host 127.0.0.1 --port 8001 --reload
```

## Env

- `GOOGLE_API_KEY` (requerida)
- `CHABITO_MODEL` (opcional, default: `gemini-2.0-flash`)
- `CHABITO_VERBOSE` (opcional, `1` para logs verbose)
- `CHABITO_SYSTEM_PROMPT` (opcional)

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

## Response shape

El servidor responde JSON con `answer`:

```json
{ "type": "chat", "answer": "..." }
```

En caso de error del agente:

```json
{ "error": "agent_error", "detail": "...", "payload": { "message": "...", "user_id": "..." } }
```
