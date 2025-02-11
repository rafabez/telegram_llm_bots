# Telegram Bot com Integração à API [Pollinations](https://pollinations.ai/referral?topic=pollinations)

Este projeto implementa um bot do Telegram que se integra com a API de geração de texto **Pollinations**. O bot recebe mensagens de usuários no Telegram, envia essas mensagens para a API e retorna respostas geradas diretamente para o chat.

## Funcionalidades
- **Envio de mensagens**: Usuários interagem diretamente com o bot enviando mensagens de texto.
- **Processamento de texto gerado**: As mensagens são enviadas para a [API Pollinations](https://pollinations.ai/referral?topic=pollinations), que processa e retorna textos gerados.
- **Métodos GET e POST**: O código está estruturado para se integrar com a API da Pollinations por meio de requisições GET e POST.

## Pré-Requisitos
1. Python 3.10 ou superior;
2. Virtualenv configurado (opcional, mas recomendado);
3. Token de acesso do bot do Telegram gerado via [BotFather](https://core.telegram.org/bots#botfather);
4. Pacotes listados em `requirements.txt`:

   ```
   python-telegram-bot
   requests
   ```

## Configuração
1. Clone este repositório:  
   ```bash
   git clone https://github.com/seu-usuario/seu-repositorio.git
   cd seu-repositorio
   ```

2. (Opcional) Crie um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Para Windows: venv\Scripts\activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure o token do bot no código (temporário para testes) ou use uma variável de ambiente:
   - Se optar pela variável de ambiente:
     ```bash
     export TELEGRAM_TOKEN="SEU_TOKEN"  # No Windows: set TELEGRAM_TOKEN=
     ```
   - Ou insira o token diretamente no código `bot.py` na variável `TELEGRAM_TOKEN`.

## Execução
Inicie o bot executando o script principal:
```bash
python bot.py
```

Após a execução bem-sucedida, você verá no terminal:
```
Telegram bot is running...
```

O bot agora estará escutando mensagens no Telegram.

## Estrutura do Código
- **`bot.py`**: Script principal do bot:
  - Configuração e conexão com a API do Telegram;
  - Funções auxiliares para comunicação com a API [Pollinations](https://pollinations.ai/referral?topic=pollinations);
  - Lógica principal para envio e recepção de mensagens.

- **Comunicação com a API Pollinations**:
  1. **GET**: Simples e rápido, envia o texto direto no endpoint.
  2. **POST**: Suporte a mensagens complexas e parâmetros adicionais no corpo da requisição.

## Solução de Problemas
1. **Timeout ou falhas de conexão**:
   - Verifique sua conexão com a Internet e se há firewalls ou proxy bloqueando o acesso aos servidores do Telegram.
   - Tente aumentar o valor de timeout no método:
     ```python
     application.run_polling(timeout=60)
     ```

2. **Configuração do token**: Certifique-se de que o token está correto e ativo.

3. **Ambiente virtual**: Use um ambiente virtual isolado para evitar conflitos de dependências.

## Como Contribuir
1. Faça um fork do repositório;
2. Crie uma branch para sua feature:
   ```bash
   git checkout -b minha-feature
   ```
3. Envie seu PR com as alterações.

## Licença
Projeto open-source. Licenciado sob [MIT](LICENSE).

## Referências
- [API Pollinations](https://pollinations.ai/): Documentação oficial.
- [Telegram Bot API](https://core.telegram.org/bots/api): Guia de desenvolvimento de bots no Telegram.
