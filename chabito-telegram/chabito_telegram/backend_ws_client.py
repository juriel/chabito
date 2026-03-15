import asyncio
import json
from typing import Any, Dict, Optional

import websockets


class BackendWebSocketClient:
    def __init__(self, ws_url: str, timeout_sec: int = 30) -> None:
        self._ws_url = ws_url
        self._timeout_sec = timeout_sec
        self._ws: Optional[Any] = None
        self._lock = asyncio.Lock()  # single in-flight request to keep send/recv paired

    async def connect(self) -> None:
        if self._ws and not self._ws.closed:
            return
        self._ws = await websockets.connect(self._ws_url)

    async def close(self) -> None:
        if self._ws and not self._ws.closed:
            await self._ws.close()
        self._ws = None

    async def send_input_message(self, payload: Dict[str, Any]) -> Any:
        async with self._lock:
            return await self._send_locked(payload)

    async def _send_locked(self, payload: Dict[str, Any]) -> Any:
        # Try once, then reconnect and retry once on connection issues.
        for attempt in (1, 2):
            try:
                await self.connect()
                assert self._ws is not None
                await self._ws.send(json.dumps(payload))
                raw = await asyncio.wait_for(self._ws.recv(), timeout=self._timeout_sec)
                if isinstance(raw, str):
                    try:
                        return json.loads(raw)
                    except json.JSONDecodeError:
                        return raw
                return raw
            except Exception:
                await self.close()
                if attempt == 2:
                    raise
        raise RuntimeError("unreachable")
