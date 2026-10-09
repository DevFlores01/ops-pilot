from app.models.incident import IncidentAnalysis

incident = IncidentAnalysis(
    summary="Payment API is failing",
    severity="high",
    probable_cause="PostgreSQL connection exhaustion",
    evidence=[
        "HTTP 500 errors",
        "Database connection slots exhausted"
    ],
    recommended_actions=[
        "Check active database connections",
        "Review connection pool settings"
    ],
    requires_human_approval=False
)

print(incident.model_dump_json(indent=2))