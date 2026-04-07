"""
Embedding pipeline for policy records.
Uses Ollama's nomic-embed-text (768 dimensions) to generate embeddings,
stores them in Qdrant (local file mode, no server needed).

Usage:
    python -m src.data_ingestion.embeddings          # embed all records
    python -m src.data_ingestion.embeddings --status  # show collection stats
"""

import os
import httpx
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from src.database.models import get_session, HealthPolicy

OLLAMA_EMBED_URL = "http://localhost:11434/api/embed"
EMBED_MODEL = "nomic-embed-text"
EMBED_DIM = 768
COLLECTION_NAME = "policy_records"
QDRANT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "qdrant_store")


def get_qdrant() -> QdrantClient:
    """Get a Qdrant client using local file storage."""
    return QdrantClient(path=os.path.abspath(QDRANT_PATH))


def embed_texts(texts: list[str], batch_size: int = 32) -> list[list[float]]:
    """Embed a list of texts via Ollama nomic-embed-text. Returns list of 768-dim vectors."""
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        response = httpx.post(
            OLLAMA_EMBED_URL,
            json={"model": EMBED_MODEL, "input": batch},
            timeout=120.0,
        )
        response.raise_for_status()
        all_embeddings.extend(response.json()["embeddings"])
    return all_embeddings


def embed_query(text: str) -> list[float]:
    """Embed a single query string. Returns 768-dim vector."""
    return embed_texts([text])[0]


def _policy_to_text(record) -> str:
    """Convert a policy record to embeddable text. Combines title + summary."""
    parts = [record.title]
    if record.summary:
        parts.append(record.summary)
    return " — ".join(parts)


def ensure_collection(client: QdrantClient):
    """Create the policy_records collection if it doesn't exist."""
    collections = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in collections:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
        )
        print(f"Created collection '{COLLECTION_NAME}' (dim={EMBED_DIM}, cosine)")
    else:
        print(f"Collection '{COLLECTION_NAME}' already exists")


def embed_all_records(force: bool = False):
    """Embed all policy records and store in Qdrant.
    If force=False, skips records that already have embeddings."""
    client = get_qdrant()
    ensure_collection(client)

    session = get_session()
    records = session.query(HealthPolicy).filter(
        HealthPolicy.verification_status != "failed"
    ).all()

    if not force:
        # Check which record IDs are already embedded
        existing_count = client.count(collection_name=COLLECTION_NAME).count
        if existing_count >= len(records):
            print(f"All {len(records)} records already embedded ({existing_count} in Qdrant). Use --force to re-embed.")
            session.close()
            client.close()
            return

    print(f"Embedding {len(records)} policy records...")

    # Prepare texts and metadata
    texts = [_policy_to_text(r) for r in records]
    print(f"Generating embeddings via {EMBED_MODEL}...")
    embeddings = embed_texts(texts)

    # Build Qdrant points
    points = []
    for record, embedding in zip(records, embeddings):
        points.append(PointStruct(
            id=record.id,
            vector=embedding,
            payload={
                "record_id": record.id,
                "country": record.country,
                "category": record.category,
                "title": record.title,
                "summary": (record.summary or "")[:500],
                "source": record.source,
                "source_url": record.source_url,
                "original_language": record.original_language,
                "last_updated": record.last_updated,
                "verification_status": record.verification_status,
            },
        ))

    # Upsert in batches
    batch_size = 100
    for i in range(0, len(points), batch_size):
        batch = points[i:i + batch_size]
        client.upsert(collection_name=COLLECTION_NAME, points=batch)
        print(f"  Upserted {min(i + batch_size, len(points))}/{len(points)}")

    print(f"Done. {len(points)} records embedded and stored.")
    session.close()
    client.close()


def search_semantic(query: str, country: str = "", category: str = "", limit: int = 20) -> list[dict]:
    """Semantic search over policy embeddings.
    Returns top matches with scores, optionally filtered by country/category."""
    client = get_qdrant()
    query_vector = embed_query(query)

    # Build filters
    conditions = []
    if country:
        conditions.append(FieldCondition(key="country", match=MatchValue(value=country.upper())))
    if category:
        conditions.append(FieldCondition(key="category", match=MatchValue(value=category)))

    search_filter = Filter(must=conditions) if conditions else None

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        query_filter=search_filter,
        limit=limit,
    )
    client.close()

    return [
        {
            "record_id": hit.payload["record_id"],
            "country": hit.payload["country"],
            "category": hit.payload["category"],
            "title": hit.payload["title"],
            "summary": hit.payload["summary"],
            "source": hit.payload["source"],
            "source_url": hit.payload["source_url"],
            "original_language": hit.payload["original_language"],
            "last_updated": hit.payload["last_updated"],
            "verification_status": hit.payload["verification_status"],
            "similarity_score": round(hit.score, 4),
        }
        for hit in results.points
    ]


def show_status():
    """Print collection stats."""
    client = get_qdrant()
    try:
        info = client.get_collection(COLLECTION_NAME)
        print(f"Collection: {COLLECTION_NAME}")
        print(f"  Vectors: {info.points_count}")
        print(f"  Dimensions: {info.config.params.vectors.size}")
        print(f"  Distance: {info.config.params.vectors.distance}")
    except Exception as e:
        print(f"Collection not found: {e}")
    client.close()


if __name__ == "__main__":
    import sys
    if "--status" in sys.argv:
        show_status()
    else:
        force = "--force" in sys.argv
        embed_all_records(force=force)
