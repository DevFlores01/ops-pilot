import re

from app.models.agent_response import StructuredIncident


class EvidenceValidationError(Exception):
    pass


def normalize_text(text: str) -> str:
    """
    Normalize whitespace and case for comparison.
    """
    return re.sub(r"\s+", " ", text).strip().casefold()


def validate_incident_evidence(
    incident: StructuredIncident,
    retrieved_evidence: list[dict],
) -> StructuredIncident:
    """
    Validate that generated evidence statements
    appear in retrieved operational documents.

    This validates extracted evidence, not the
    factual correctness of every incident conclusion.
    """

    if not retrieved_evidence:
        raise EvidenceValidationError("No retrieved evidence available")

    valid_documents = [
        item
        for item in retrieved_evidence
        if isinstance(item, dict)
        and isinstance(item.get("document_key"), str)
        and item["document_key"].strip()
        and isinstance(item.get("content"), str)
        and item["content"].strip()
    ]

    if not valid_documents:
        raise EvidenceValidationError("No valid evidence documents")

    if not incident.evidence:
        raise EvidenceValidationError("Generated incident contains no evidence")

    normalized_documents = [normalize_text(item["content"]) for item in valid_documents]

    for statement in incident.evidence:
        if not isinstance(statement, str) or not statement.strip():
            raise EvidenceValidationError(
                "Generated evidence contains an empty statement"
            )

        normalized_statement = normalize_text(statement)

        supported = any(
            normalized_statement in document for document in normalized_documents
        )

        if not supported:
            raise EvidenceValidationError(
                "Generated evidence is not found in retrieved documents"
            )

    return incident
