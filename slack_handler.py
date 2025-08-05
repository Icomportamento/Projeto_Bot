import os
import tempfile
import threading
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from pdf_utils import extract_text_from_pdf
from vector_store import store_embeddings, get_relevant_chunks, load_vector_data
from config import SLACK_BOT_TOKEN, OPENAI_MODEL
from openai import OpenAI

client = WebClient(token=SLACK_BOT_TOKEN)
openai_client = OpenAI()

BASE_DATA_PATH = "data"
processed_events = set()

def handle_event(event):
    if event.get("bot_id") or event.get("type") != "message":
        return

    event_id = event.get("event_ts") or event.get("ts")
    if event_id in processed_events:
        return
    processed_events.add(event_id)

    if "files" in event:
        for file in event["files"]:
            if file["mimetype"] == "application/pdf":
                handle_pdf_upload(file, event)

def handle_pdf_upload(file_info, event):
    try:
        file_url = file_info["url_private_download"]
        headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
        response = requests.get(file_url, headers=headers)
        if response.status_code != 200:
            raise Exception("Erro ao baixar o PDF")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(response.content)
            tmp_path = tmp_file.name

        text = extract_text_from_pdf(tmp_path)

        key = event.get("channel") or event.get("user")
        save_dir = os.path.join(BASE_DATA_PATH, key)
        os.makedirs(save_dir, exist_ok=True)

        store_embeddings(text, save_dir=save_dir, vector_id="latest")

        client.chat_postMessage(
            channel=key,
            text="PDF processado e indexado com sucesso! Use o comando /pergunta para fazer sua pergunta."
        )
    except Exception as e:
        client.chat_postMessage(
            channel=event.get("channel"),
            text=f"Erro ao processar o PDF: {str(e)}"
        )

def handle_slash_command(command_payload):
    # Responde imediatamente e inicia thread
    threading.Thread(target=processar_pergunta, args=(command_payload,)).start()
    

def processar_pergunta(command_payload):
    channel_id = command_payload.get("channel_id")
    user_question = command_payload.get("text")

    if not user_question:
        client.chat_postMessage(
            channel=channel_id,
            text="Você deve enviar uma pergunta após o comando. Exemplo:\n`/pergunta Qual é o resumo do documento?`"
        )
        return

    save_dir = os.path.join(BASE_DATA_PATH, channel_id)

    try:
        vector_data = load_vector_data(save_dir=save_dir, vector_id="latest")
    except Exception:
        client.chat_postMessage(
            channel=channel_id,
            text="Nenhum PDF foi carregado ainda neste canal. Por favor envie um PDF primeiro."
        )
        return

    chunks = get_relevant_chunks(vector_data, user_question)
    context = "\n".join(chunks[:5])
    prompt = f"Responda com base apenas no texto abaixo:\n\n{context}\n\nPergunta: {user_question}"

    try:
        response = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "Você é um assistente útil que responde apenas com base nos documentos fornecidos."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )

        answer = response.choices[0].message.content.strip()
        client.chat_postMessage(
            channel=channel_id,
            text=f"<@{command_payload['user_id']}> perguntou: {user_question}"
        )
        client.chat_postMessage(channel=channel_id, text=answer)

    except Exception as e:
        client.chat_postMessage(
            channel=channel_id,
            text=f"Erro ao gerar resposta: {str(e)}"
        )