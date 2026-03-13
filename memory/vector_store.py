from datetime import datetime, timezone
import os

from sentence_transformers import SentenceTransformer
import chromadb

model = SentenceTransformer("all-MiniLM-L6-v2")

_db_path = os.path.join(os.path.dirname(__file__), "chroma_db")
os.makedirs(_db_path, exist_ok=True)

client = chromadb.PersistentClient(path=_db_path)

collection = client.get_or_create_collection("customer_memory")


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def store_message(customer_id, text, metadata=None):

    embedding = model.encode(text).tolist()
    meta = metadata or {}
    meta.update({"customer_id": customer_id, "timestamp": _now_iso()})

    collection.add(
        documents=[text],
        embeddings=[embedding],
        metadatas=[meta],
        ids=[f"{customer_id}-{hash(text)}"]
    )
