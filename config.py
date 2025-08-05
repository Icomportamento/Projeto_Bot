import os
from dotenv import load_dotenv

load_dotenv()  # Carrega variáveis do .env (caso esteja usando)

# Tokens do Slack
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN") or "xoxb-your-bot-token"
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET") or "your-signing-secret"

# Chave da OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or "sk-your-openai-key"
OPENAI_MODEL = os.getenv("OPENAI_MODEL") or "gpt-4"  # ou gpt-3.5-turbo
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL") or "text-embedding-3-small"

# Define a chave para o cliente OpenAI globalmente
import openai
openai.api_key = OPENAI_API_KEY
