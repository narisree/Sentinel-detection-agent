# Project Overview

## Purpose

This repository is a persistent knowledge base and agentic workflow for a SOC L2 detection engineer working in a Managed Security Service Provider (MSSP) environment. It is used to design, generate, validate, and improve KQL detection rules for Microsoft Sentinel across multiple client tenants.

## Goals

1. **Accuracy** — Produce correct, validated KQL that can be pasted directly into Sentinel Analytics Rules without modification.
2. **Consistency** — Enforce a single house style so all rules look alike, reducing cognitive overhead during incident response.
3. **Learning** — Capture every correction and mistake so the same error is never repeated.
4. **Traceability** — Tag every rule to MITRE ATT&CK and document the reasoning behind design decisions.
5. **Data sovereignty** — Never persist client-identifying data in any knowledge file.

## Repository Structure

```
01-project/          Workflow, confidence framework, this overview.
02-knowledge/        Reference material: KQL, table schemas, MITRE, house style.
04-decisions/        Architecture Decision Records (ADRs).
05-sessions/         Session journals written at end of substantive sessions.
06-lessons/          Append-only lessons, known mistakes, and pattern library.
07-questions/        Open questions tracked across sessions.
08-generated/        Completed detection outputs, one folder per rule.
```

## Stakeholders

- **SOC L2 analysts** — Primary consumers of generated rules. They test queries in Sentinel and report errors or false positives.
- **Detection engineering lead** — Reviews ADRs and approves house-style changes.
- **MSSP clients** — Indirectly affected; their environments run the deployed rules. Client data must never appear in this knowledge base.

## Non-goals

- This repository does not manage Sentinel workspace configuration (ARM templates, workspace settings, RBAC).
- It does not automate rule deployment; that is handled by the SOC's CI/CD pipeline.
- It does not store incident tickets, SIEM alerts, or triage notes.

## Operating Model

The agent reads this knowledge base at the start of every session, follows the 7-step KQL generation workflow, and writes session journals and lessons at the end. No manual slash commands are required — the agent acts on conversational cues.
