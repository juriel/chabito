import os


def _getenv_int(key: str, default: int) -> int:
    raw = os.getenv(key)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


class Settings:
    def __init__(self) -> None:
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        self.backend_ws_url = os.getenv("BACKEND_WS_URL", "ws://127.0.0.1:8001/ws/echo").strip()
        self.log_level = os.getenv("LOG_LEVEL", "INFO").strip().upper()
        self.backend_ws_timeout_sec = _getenv_int("BACKEND_WS_TIMEOUT_SEC", 30)

    def validate(self) -> None:
        if not self.telegram_bot_token:
            raise RuntimeError("Missing TELEGRAM_BOT_TOKEN")

