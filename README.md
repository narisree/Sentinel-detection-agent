# Sentinel KQL Detection Agent

A persistent, self-improving Claude Code agent for SOC L2 detection engineers. Generates validated, MITRE ATT&CK-aligned KQL queries for Microsoft Sentinel.

> **Getting started?** See [INSTALL.md](./INSTALL.md) for the one-line `irm | iex` install, prerequisites, and what the bootstrap script does step-by-step.

## What this agent does

- Generates production-ready KQL Sentinel detection rules from threat descriptions or MITRE technique requests.
- Validates every query against verified table schemas before delivery — never hallucinating field names.
- Provides structured confidence breakdown per quality element, not a single number.
- Learns from analyst corrections and improves over time without being asked.
- Maintains an ever-growing knowledge base of schemas, patterns, and lessons.

## What this agent does NOT do

- Access Azure Sentinel or any live environment.
- Store client-specific data (emails, usernames, domains, IPs, company names).
- Refuse to deliver output — advisory gates only.

## How to use

Start a session and describe your detection need:
- "Detect PowerShell encoded command execution on Windows endpoints"
- "Alert on impossible travel in Azure AD sign-in logs"
- "Find potential DCSync attacks from non-domain-controller accounts"

If the required table schema is not in the knowledge base, the agent will ask you to paste a sample schema. Once provided, it's saved for all future queries from that table.

## Folder structure

```
02-knowledge/kql/            KQL syntax and functions reference
02-knowledge/sentinel-schema/ Verified table field schemas
02-knowledge/mitre-attack/   MITRE ATT&CK tactics and techniques
02-knowledge/detections/     Example detections (precedent corpus)
02-knowledge/house-style/    Query patterns and metadata standards
06-lessons/                  Lessons learned from analyst corrections
08-generated/                All generated queries
```

## Data sovereignty

MSSP environment. No client data is ever stored in this knowledge base. Provide only schemas and field structures — not actual log values containing client-identifying information.
