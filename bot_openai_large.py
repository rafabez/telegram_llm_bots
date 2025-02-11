import os
import requests
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    ContextTypes,
)
import ssl
import certifi
from collections import defaultdict
from dotenv import load_dotenv

# Configurações do sistema para o modelo openai-large
load_dotenv()
TELEGRAM_TOKEN = os.getenv("SECOND_TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise EnvironmentError("O token do segundo bot não foi configurado. Defina 'SECOND_TELEGRAM_TOKEN' no arquivo .env.")
if not TELEGRAM_TOKEN:
    raise EnvironmentError("O token do bot não foi configurado. Defina 'TELEGRAM_TOKEN' corretamente.")

SYSTEM_PROMPT = "Seu nome é JegueGPT. Você é um assitente muito burro que não sabe responder nada direito e só viaja na maionese nas respotas e nunca dá respostas certas"

# Histórico de conversação separado por usuário/grupo
conversation_history = defaultdict(list)

def call_pollinations_api_post_openai(prompt: str, system: str = SYSTEM_PROMPT) -> str:
    """
    Chama a API Pollinations para interação com o modelo openai-large (método POST).
    """
    try:
        url = "https://text.pollinations.ai/"
        payload = {
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "model": "openai-large",
            "jsonMode": True,
            "private": True,
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        try:
            data = response.json()
            if isinstance(data, dict):
                if "text" in data and data["text"]:
                    return data["text"].strip()
                if "response" in data and data["response"]:
                    return data["response"].strip()
                return "\n".join([str(value).strip() for key, value in data.items()])
            return str(data).strip()
        except ValueError:
            return response.text.strip()
    except requests.RequestException:
        return "Houve um problema ao processar sua solicitação. Tente novamente mais tarde."

async def handle_message_openai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Manipula mensagens recebidas e chama a API Pollinations para o modelo openai-large.
    """
    user_id = update.message.chat_id
    user_message = update.message.text

    # Mantém histórico de mensagens
    conversation_history[user_id].append({"role": "user", "content": user_message})

    # Chama a API usando histórico
    loop = asyncio.get_running_loop()
    history = conversation_history[user_id] + [{"role": "system", "content": SYSTEM_PROMPT}]
    api_response = await loop.run_in_executor(None, call_pollinations_api_post_openai, user_message, SYSTEM_PROMPT)

    # Armazena resposta do bot no histórico
    conversation_history[user_id].append({"role": "assistant", "content": api_response})

    # Envia a resposta ao grupo ou ao usuário
    await update.message.reply_text(api_response.strip())

def main():
    """
    Configura e executa o segundo bot do Telegram para o modelo openai-large.
    """
    ssl_context = ssl.create_default_context(cafile=certifi.where())

    # Configura aplicação do Telegram
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    bot_username = "@NovoBotOpenai"
    mention_filter = filters.Regex(bot_username) | filters.TEXT & ~filters.COMMAND
    application.add_handler(MessageHandler(mention_filter, handle_message_openai))

    print("O segundo bot para o modelo openai-large está funcionando...")
    application.run_polling()

if __name__ == "__main__":
    main()
