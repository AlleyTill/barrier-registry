"""Seed the database with CMS National Coverage Determinations.

This script stores NCD data fetched from the CMS Coverage API.
Since the CMS API is available as a built-in tool in Claude Code,
we can also seed from pre-fetched data.
"""

import httpx
from datetime import datetime, timezone
from src.database.models import HealthPolicy, get_session, init_db

CMS_API_BASE = "https://api.cms.gov/coverage/v1"


def fetch_ncds(keyword: str = None, limit: int = 200) -> list[dict]:
    """Fetch National Coverage Determinations from CMS API."""
    url = f"{CMS_API_BASE}/national/search"
    params = {
        "document_type": "ncd",
        "limit": limit,
        "sort_by": "last_updated_sort",
        "sort_order": "desc",
    }
    if keyword:
        params["keyword"] = keyword

    try:
        response = httpx.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("items", [])
    except Exception as e:
        print(f"Error fetching NCDs: {e}")
        return []


def seed_ncds_from_api():
    """Fetch NCDs from CMS API and store in database."""
    init_db()
    session = get_session()

    print("Fetching National Coverage Determinations from CMS...")
    ncds = fetch_ncds(limit=200)
    print(f"Found {len(ncds)} NCDs")

    stored = 0
    for ncd in ncds:
        doc_id = str(ncd.get("document_id", ""))
        existing = session.query(HealthPolicy).filter_by(
            country="USA",
            source="CMS",
            policy_id_external=doc_id,
        ).first()

        if existing:
            continue

        policy = HealthPolicy(
            country="USA",
            country_name="United States",
            source="CMS",
            source_url=f"https://www.cms.gov/medicare-coverage-database{ncd.get('url', '')}",
            category="national_coverage_determination",
            title=ncd.get("title", "Unknown"),
            summary=f"NCD {ncd.get('document_display_id', '')} - {ncd.get('title', '')}. Chapter: {ncd.get('chapter', 'N/A')}. Lab test: {'Yes' if ncd.get('is_lab') else 'No'}.",
            effective_date=ncd.get("last_updated", ""),
            last_updated=ncd.get("last_updated", ""),
            fetched_at=datetime.now(timezone.utc),
            policy_id_external=doc_id,
            original_language="en",
        )
        session.add(policy)
        stored += 1

    session.commit()
    session.close()
    print(f"Stored {stored} new NCDs in database.")


def seed_from_preloaded(items: list[dict]):
    """Seed from pre-fetched CMS data (e.g., from Claude Code's built-in CMS tool)."""
    init_db()
    session = get_session()

    stored = 0
    for ncd in items:
        doc_id = str(ncd.get("document_id", ""))
        existing = session.query(HealthPolicy).filter_by(
            country="USA",
            source="CMS",
            policy_id_external=doc_id,
        ).first()

        if existing:
            continue

        policy = HealthPolicy(
            country="USA",
            country_name="United States",
            source="CMS",
            source_url=f"https://www.cms.gov/medicare-coverage-database{ncd.get('url', '')}",
            category="national_coverage_determination",
            title=ncd.get("title", "Unknown"),
            summary=f"NCD {ncd.get('document_display_id', '')} - {ncd.get('title', '')}. Chapter: {ncd.get('chapter', 'N/A')}. Lab test: {'Yes' if ncd.get('is_lab') else 'No'}.",
            effective_date=ncd.get("last_updated", ""),
            last_updated=ncd.get("last_updated", ""),
            fetched_at=datetime.now(timezone.utc),
            policy_id_external=doc_id,
            original_language="en",
        )
        session.add(policy)
        stored += 1

    session.commit()
    session.close()
    print(f"Stored {stored} new NCDs in database.")


if __name__ == "__main__":
    seed_ncds_from_api()
