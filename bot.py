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

# Configurações do sistema
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if TELEGRAM_TOKEN:
    # Remove leading and trailing whitespace
    TELEGRAM_TOKEN = TELEGRAM_TOKEN.strip()
    # If it starts with an "=" character, remove it
    if TELEGRAM_TOKEN.startswith("="):
        TELEGRAM_TOKEN = TELEGRAM_TOKEN[1:].strip()

if not TELEGRAM_TOKEN:
    raise EnvironmentError("O token do bot não foi configurado. Defina 'TELEGRAM_TOKEN' corretamente nas variáveis de ambiente.")

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
            return str(data).strip()
        except ValueError:
            return response.text.strip()
    except requests.RequestException:
        return "Houve um problema ao processar sua solicitação. Tente novamente mais tarde."

# Mantém histórico de conversação por usuário/grupo
conversation_history = defaultdict(list)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Lida com a mensagem recebida, chama a API Pollinations (POST) e retorna a resposta,
    mantendo histórico de conversação.
    """
    user_id = update.message.chat_id
    user_message = update.message.text

    # Verifica se o bot foi mencionado no texto
    bot_usernames = ["@aia", "@Aia001_Bot"]
    if not any(user_message.lower().find(username.lower()) != -1 for username in bot_usernames):
        return  # Não faz nada se o bot não for mencionado

    # Atualiza o histórico de conversação
    conversation_history[user_id].append({"role": "user", "content": user_message})

    SEND_PROCESSING_MESSAGE = False
    if SEND_PROCESSING_MESSAGE:
        await update.message.reply_text("Processando sua mensagem...")

    # Executa a chamada bloqueante em um executor para não travar o loop assíncrono
    loop = asyncio.get_running_loop()
    # Aqui estamos utilizando apenas o SYSTEM_PROMPT, mas você pode adaptar para usar o histórico
    api_response = await loop.run_in_executor(None, call_pollinations_api_post, user_message, SYSTEM_PROMPT)

    # Armazena a resposta do bot no histórico
    conversation_history[user_id].append({"role": "assistant", "content": api_response})

    await update.message.reply_text(api_response.strip())

def main():
    """
    Configura e executa o bot do Telegram.
    """
    # Configuração do contexto SSL (caso seja necessário)
    ssl_context = ssl.create_default_context(cafile=certifi.where())

    # Configura o aplicativo do Telegram
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    bot_username = "@aia"
    mention_filter = filters.Regex(f"(?i){bot_username}\\b")
    application.add_handler(MessageHandler(mention_filter, handle_message))

    print("O bot do Telegram está funcionando...")
    application.run_polling()

if __name__ == "__main__":
    main()
