import json
from typing import Any, Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from app.dto import InputMessageDTO


app = FastAPI(title="chabito-backend-2", version="1.0.0")


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


def dump_model(model: InputMessageDTO) -> Dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


@app.websocket("/ws/echo")
async def websocket_echo(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            raw_message = await websocket.receive_text()
            try:
                payload = json.loads(raw_message)
            except json.JSONDecodeError:
                await websocket.send_json(
                    {"error": "invalid_json", "detail": "Payload must be valid JSON"}
                )
                continue

            try:
                input_message = InputMessageDTO(**payload)
            except ValidationError as exc:
                await websocket.send_json(
                    {
                        "error": "invalid_payload",
                        "detail": "Payload does not match InputMessageDTO",
                        "validation_errors": exc.errors(),
                    }
                )
                continue

            await websocket.send_json(
                {"type": "echo", "payload": dump_model(input_message)}
            )
    except WebSocketDisconnect:
        return

