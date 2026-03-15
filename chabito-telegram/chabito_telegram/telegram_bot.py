import base64
import logging
from typing import Any, Dict, Optional, Tuple

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from .backend_ws_client import BackendWebSocketClient
from .config import Settings


def _pick_answer(response: Any) -> str:
    if isinstance(response, dict):
        return (
            response.get("answer")
            or response.get("reply")
            or (response.get("payload") or {}).get("message")
            or str(response)
        )
    return str(response)


async def _extract_message_and_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Tuple[str, Optional[str], Optional[str]]:
    msg = update.effective_message
    if msg is None:
        return "", None, None

    # Text
    if msg.text:
        return msg.text, None, None

    # Photo (Telegram photos are delivered as JPEG sizes)
    if msg.photo:
        photo = msg.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        data = await file.download_as_bytearray()
        caption = msg.caption or ""
        return caption or "[image]", "image/jpeg", base64.b64encode(bytes(data)).decode("ascii")

    # Voice
    if msg.voice:
        file = await context.bot.get_file(msg.voice.file_id)
        data = await file.download_as_bytearray()
        mime = getattr(msg.voice, "mime_type", None) or "audio/ogg"
        caption = msg.caption or ""
        return caption or "[voice]", mime, base64.b64encode(bytes(data)).decode("ascii")

    # Document
    if msg.document:
        file = await context.bot.get_file(msg.document.file_id)
        data = await file.download_as_bytearray()
        mime = msg.document.mime_type or "application/octet-stream"
        caption = msg.caption or msg.document.file_name or ""
        return caption or "[document]", mime, base64.b64encode(bytes(data)).decode("ascii")

    return "[unsupported_message]", None, None


class TelegramBot:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._backend = BackendWebSocketClient(
            ws_url=settings.backend_ws_url, timeout_sec=settings.backend_ws_timeout_sec
        )

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("Listo. Enviame un mensaje y lo reenvio al backend.")

    async def on_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        msg = update.effective_message
        if msg is None:
            return

        message_text, mime_type, file_b64 = await _extract_message_and_file(update, context)

        chat_id = update.effective_chat.id if update.effective_chat else "unknown"
        from_user = update.effective_user
        user_id = f"telegram:{chat_id}"
        sender_jid = f"telegram:{from_user.id}" if from_user else None
        sender_nickname = from_user.full_name if from_user else None

        input_message: Dict[str, Any] = {
            "message": message_text,
            "user_id": user_id,
            "sender_nickname": sender_nickname,
            "sender_jid": sender_jid,
            "mime_type": mime_type,
            "file_base64": file_b64,
        }

        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

        try:
            response = await self._backend.send_input_message(input_message)
            await msg.reply_text(_pick_answer(response))
        except Exception as exc:
            logging.exception("Backend WS error")
            await msg.reply_text(f"⚠️ Error conectando al backend WS: {exc}")

    def build_app(self) -> Application:
        app = Application.builder().token(self._settings.telegram_bot_token).build()
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, self.on_message))
        return app

