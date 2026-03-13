from .vector_store import collection, model

def retrieve_history(customer_id, query):

    embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[embedding],
        n_results=3,
        where={"customer_id": customer_id}
    )

    return results.get("documents", [[]])[0]
