# Log Report Task

This repository contains a Harbor task that asks an agent to parse an Apache-style access log and produce a JSON summary report at /app/report.json.

The task is intentionally simple and deterministic: the agent must read /app/access.log, count requests, count distinct client IPs, and identify the most common request path. The verifier independently recomputes those values from the log and checks the generated JSON file, so a no-op agent fails rather than receiving a reward.

The implementation lives in the task directory, with the prompt in task/instruction.md, the verifier in task/tests, the reference solution in task/solution, and the shared container image definition in task/environment/Dockerfile.
