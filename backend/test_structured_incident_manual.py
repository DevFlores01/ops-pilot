import asyncio
import json

from app.agents.structured_incident_service import StructuredIncidentService


async def main():
    service = StructuredIncidentService()

    evidence = [
        {
            "document_key": "runbooks/kubernetes-pod-runbook.md",
            "chunk_index": 0,
            "similarity": 0.7862,
            "content": (
                "Kubernetes CrashLoopBackOff runbook. "
                "Possible causes include application crashes, "
                "OOMKilled containers, and failed readiness probes. "
                "Investigation: inspect pod events, container logs, "
                "resource limits, and recent deployments. "
                "Human approval is required before restarting "
                "workloads or rolling back deployments."
            ),
        }
    ]

    result = await service.generate(
        question="Why is my kuberneted pod in CrashLoopBackOff?",
        evidence=evidence,
    )

    print(
        json.dumps(
            result.model_dump(),
            indent=2,
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
