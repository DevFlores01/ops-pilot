import math

from app.models.agent_response import SourceReference

MIN_SIMILARITY = 0.55


def validate_sources(
    evidence: list[dict],
) -> list[SourceReference]:
    sources = []
    seen = set()

    for item in evidence:
        if not isinstance(item, dict):
            continue

        key = item.get("document_key")
        index = item.get("chunk_index")
        similarity = item.get("similarity")
        content = item.get("content")

        if not isinstance(key, str) or not key:
            continue

        if type(index) is not int or index < 0:
            continue

        if type(similarity) not in (float, int):
            continue

        if not math.isfinite(similarity):
            continue

        if not MIN_SIMILARITY <= similarity <= 1.0:
            continue

        if not isinstance(content, str) or not content.strip():
            continue

        identity = (key, index)

        if identity in seen:
            continue

        seen.add(identity)

        sources.append(
            SourceReference(
                document_key=key,
                chunk_index=index,
                similarity=float(similarity),
            )
        )

    return sources
