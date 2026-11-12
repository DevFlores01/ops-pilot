# Kubernetes Pod Incident Runbook

## Symptoms

- CrashLoopBackOff
- Pod restart loops
- OOMKilled containers
- Failed readiness probes

## Investigation

1. Inspect pod events.
2. Check container logs.
3. Review resource requests and limits.
4. Investigate recent deployments.

## Remediation

- Escalate to the Kubernetes administrator.
- Require approval before restarting workloads.
- Require approval before rolling back deployments.
