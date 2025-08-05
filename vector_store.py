import faiss
import numpy as np
import json
import os
from openai import OpenAI
from config import OPENAI_MODEL, EMBEDDING_MODEL

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Usamos chunks de texto para vetorização
def chunk_text(text, max_tokens=500):
    paragraphs = text.split("\n")
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) <= max_tokens:
            current_chunk += para + "\n"
        else:
            chunks.append(current_chunk.strip())
            current_chunk = para + "\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def get_embedding(text):
    response = openai_client.embeddings.create(
        input=[text],
        model=EMBEDDING_MODEL
    )
    return np.array(response.data[0].embedding, dtype=np.float32)

def store_embeddings(text, save_dir="data", vector_id="default"):
    chunks = chunk_text(text)
    embeddings = [get_embedding(chunk) for chunk in chunks]

    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))

    os.makedirs(save_dir, exist_ok=True)

    # Salva índice FAISS
    faiss.write_index(index, os.path.join(save_dir, f"{vector_id}.index"))

    # Salva os chunks
    with open(os.path.join(save_dir, f"{vector_id}_chunks.json"), "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    return {
        "index": index,
        "chunks": chunks,
        "embeddings": embeddings
    }

def load_vector_data(save_dir="data", vector_id="default"):
    index = faiss.read_index(os.path.join(save_dir, f"{vector_id}.index"))
    with open(os.path.join(save_dir, f"{vector_id}_chunks.json"), "r", encoding="utf-8") as f:
        chunks = json.load(f)

    return {
        "index": index,
        "chunks": chunks
    }

def get_relevant_chunks(vector_data, query, top_k=5):
    query_vector = get_embedding(query)
    D, I = vector_data["index"].search(np.array([query_vector]), top_k)
    results = [vector_data["chunks"][i] for i in I[0]]
    return results
