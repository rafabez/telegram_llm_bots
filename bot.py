import os
import asyncio
import logging
import urllib.parse
import ssl
import certifi
import requests

from collections import defaultdict
from telegram import Update
from telegram.constants import ChatType
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s"
)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if TELEGRAM_TOKEN:
    TELEGRAM_TOKEN = TELEGRAM_TOKEN.strip()
    if TELEGRAM_TOKEN.startswith("="):
        TELEGRAM_TOKEN = TELEGRAM_TOKEN[1:].strip()

if not TELEGRAM_TOKEN:
    raise EnvironmentError("O token do bot não foi configurado.")

SYSTEM_PROMPT = "O seu nome é Aia. Uma carismática e sarcástica IA meio troll."

def call_pollinations(prompt: str) -> str:
    try:
        # Create full prompt with system instructions
        full_prompt = f"{SYSTEM_PROMPT}\n\nUser: {prompt}"
        encoded_prompt = urllib.parse.quote(full_prompt)
        base = f"https://text.pollinations.ai/{encoded_prompt}"
        params = {"model": "evil", "referrer": "aia.bot"}
        r = requests.get(base, params=params, timeout=60)
        r.raise_for_status()
        return r.text.strip()
    except requests.RequestException as e:
        logging.error("Pollinations API falhou: %s", e)
        return "Houve um problema ao processar sua solicitação. Tente novamente mais tarde."

conversation_history = defaultdict(list)

async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if not message or not message.text:
        return
    text = message.text.strip()
    chat = update.effective_chat
    
    # Handle group chats - check for bot mention
    if chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
        low = text.lower()
        if "@aia" not in low and "@aia001_bot" not in low:
            return
    
    conversation_history[chat.id].append({"role": "user", "content": text})
    loop = asyncio.get_running_loop()
    reply = await loop.run_in_executor(None, call_pollinations, text)
    conversation_history[chat.id].append({"role": "assistant", "content": reply})
    await message.reply_text(reply)

def main():
    ssl.create_default_context(cafile=certifi.where())
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Aia está funcionando...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()