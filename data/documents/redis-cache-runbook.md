# Redis Cache Incident Runbook

## Symptoms

- Increased cache misses
- High Redis memory utilization
- Slow cache responses
- Application latency increases

## Investigation

1. Check Redis memory usage.
2. Review cache hit and miss rates.
3. Inspect Redis eviction policies.
4. Check Redis connection counts.

## Remediation

- Escalate to the responsible engineer.
- Review cache expiration policies.
- Require approval before restarting Redis.
