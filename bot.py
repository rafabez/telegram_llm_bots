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
from dotenv import load_dotenv
import certifi

# Configurações do sistema
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise EnvironmentError("O token do bot não foi configurado. Defina 'TELEGRAM_TOKEN' corretamente no arquivo .env.")
if not TELEGRAM_TOKEN:
    raise EnvironmentError("O token do bot não foi configurado. Defina 'TELEGRAM_TOKEN' corretamente.")

SYSTEM_PROMPT = ("O seu nome é Aia. Uma carismática e sarcástica IA meio troll. SPEAK only PORTUGUESE")

# Função para chamada à API Pollinations via GET
def call_pollinations_api_get(prompt: str, system: str = SYSTEM_PROMPT) -> str:
    """
    Envia a mensagem do usuário para a API Pollinations (método GET) e retorna a resposta.
    """
    try:
        url = f"https://text.pollinations.ai/{requests.utils.quote(prompt)}"
        params = {
            "model": "evil",
            "json": "true",
        }
        if system:
            params["system"] = requests.utils.quote(system)
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        # Prioriza a chave "text" e depois "response"
        if "text" in data and data["text"]:
            return data["text"].strip()
        if "response" in data and data["response"]:
            return data["response"].strip()
        # Se nenhuma das chaves existir ou estiver vazia, retorna somente os valores (sem prefixos)
        return "\n".join([str(value).strip() for value in data.values() if value])
    except requests.RequestException:
        return "Houve um problema ao processar sua solicitação. Tente novamente mais tarde."

# Função para chamada à API Pollinations via POST
def call_pollinations_api_post(prompt: str, system: str = SYSTEM_PROMPT) -> str:
    """
    Envia a mensagem do usuário para a API Pollinations (método POST) e retorna a resposta.
    """
    try:
        url = "https://text.pollinations.ai/"
        payload = {
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "model": "evil",
            "seed": 42,
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
                return "\n".join([f"{key}: {value}" for key, value in data.items()])
            return f"{str(data).strip()}"
        except ValueError:
            return f"{response.text.strip()}"
    except requests.RequestException:
        return "Houve um problema ao processar sua solicitação. Tente novamente mais tarde."

from collections import defaultdict

# Maintain conversation history by user/group
conversation_history = defaultdict(list)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Lida com a mensagem recebida, chama a API Pollinations (POST) e retorna a resposta,
    mantendo histórico de conversação.
    """
    user_id = update.message.chat_id
    user_message = update.message.text

    # Update conversation history
    conversation_history[user_id].append({"role": "user", "content": user_message})

    SEND_PROCESSING_MESSAGE = False
    if SEND_PROCESSING_MESSAGE:
        await update.message.reply_text("Processando sua mensagem...")

    # Executa a chamada bloqueante em um executor para não travar o loop assíncrono
    loop = asyncio.get_running_loop()
    # Use conversation memory in API call
    history = conversation_history[user_id] + [{"role": "system", "content": SYSTEM_PROMPT}]
    api_response = await loop.run_in_executor(None, call_pollinations_api_post, user_message, history)

    # Save bot response to history
    conversation_history[user_id].append({"role": "assistant", "content": api_response})

    await update.message.reply_text(api_response.strip())

# Função principal para iniciar o bot
def main():
    """
    Configura e executa o bot do Telegram.
    """
    # Configuração do contexto SSL (caso seja necessário)
    ssl_context = ssl.create_default_context(cafile=certifi.where())

    # Configura o aplicativo do Telegram
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    from telegram.ext import filters
    bot_username = "@Aia001_Bot"
    mention_filter = filters.Regex(bot_username) | filters.TEXT & ~filters.COMMAND
    application.add_handler(MessageHandler(mention_filter, handle_message))

    print("O bot do Telegram está funcionando...")
    application.run_polling()

if __name__ == "__main__":
    main()
