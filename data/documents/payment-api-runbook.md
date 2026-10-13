# Payment API Incident Runbook

## Symptoms

- HTTP 500 errors
- PostgreSQL connection exhaustion
- High API latency

## Investigation

1. Check application logs.
2. Inspect PostgreSQL active connections.
3. Review recent deployments.
4. Check connection pool configuration.

## Remediation

- Escalate to the responsible engineer.
- Require approval before restarting services.
- Require approval before rolling back deployments.
