Este projeto é um bot para Slack que permite:

- Fazer upload de arquivos PDF diretamente no Slack
- Indexar automaticamente o conteúdo do PDF com embeddings da OpenAI
- Consultar o conteúdo por meio de um comando `/pergunta`, com respostas baseadas no conteúdo enviado
- Acessar um painel web para gerenciar os arquivos por canal (upload e remoção)

---

##  Funcionalidades

###  No Slack
- Envie um PDF para o canal
- Ele será processado e indexado automaticamente
- Use `/pergunta Sua pergunta aqui` para consultar com base no conteúdo do PDF

###  Interface Web
- Upload manual de PDFs por canal
- Visualização de arquivos processados
- Remoção de arquivos diretamente no painel
- Acesso somente a canais autorizados (em breve)

---

## 🧱 Estrutura do Projeto

```
📁 projeto/
│
├── app.py                  # App Flask principal
├── slack_handler.py        # Lida com eventos do Slack e comandos
├── vector_store.py         # Geração e busca de embeddings
├── pdf_utils.py            # Extração de texto de PDFs
├── config.py               # Tokens e variáveis de ambiente
├── requirements.txt        # Dependências do projeto
│
├── templates/
│   └── painel.html         # Interface web de administração
│
└── data/
    └── <canal_id>/
        ├── latest.index    # Index FAISS do canal
        ├── latest_chunks.json
        └── original.pdf    # PDF original (opcional)
```

---

## ⚙ Requisitos

- Python 3.9+
- Conta na OpenAI (para usar embeddings e GPT)
- Conta no Slack + App de desenvolvedor configurado
- (Opcional) VPS com acesso público ou uso de ngrok

---

##  Instalação

1. **Clone o projeto:**

```bash
git clone https://github.com/seu-usuario/seu-repo.git
cd seu-repo
```

2. **Crie e ative um ambiente virtual:**

```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS
```

3. **Instale as dependências:**

```bash
pip install -r requirements.txt
```

4. **Configure suas variáveis no `config.py`:**

```python
SLACK_BOT_TOKEN = "xoxb-..."
SLACK_SIGNING_SECRET = "..."
OPENAI_API_KEY = "sk-..."
OPENAI_MODEL = "gpt-4"  # ou gpt-3.5-turbo
EMBEDDING_MODEL = "text-embedding-3-small"
```

5. **Execute o app:**

```bash
python app.py
```

---

## 🌐 Acesso via ngrok (modo desenvolvimento)

```bash
ngrok http 3000
```

- Copie o link HTTPS gerado
- Cole no seu app do Slack em:
  - **Request URL (eventos):** `https://xxxx.ngrok.io/slack/events`
  - **Slash command /pergunta:** `https://xxxx.ngrok.io/slack/commands`

---

##  Permissões do Slack

Certifique-se de adicionar estas permissões no app do Slack:

- `commands`
- `chat:write`
- `files:read`
- `files:write`
- `channels:history`
- `groups:history`
- `im:history`
- `mpim:history`

---

##  Custos da OpenAI

- Os embeddings usam tokens e **geram custos por 1.000 tokens enviados**
- Use o modelo `text-embedding-3-small` para otimizar

---

##  Futuras melhorias

- Controle de acesso (admins vs. usuários comuns)
- Lista de canais permitidos
- Logs na interface web
- Upload e resposta com imagens
