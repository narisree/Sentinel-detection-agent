---
description: Hard rules on external services and client data
---

# Data sovereignty

This agent operates in an MSSP environment. Client data is sensitive and must never be persisted.

> **Automated backstop (ADR-003).** A pre-commit guard scans staged changes for
> public IPs, email addresses, and UNC paths and blocks the commit on a hit. It
> is a low-false-positive net, **not** a substitute for the discipline below —
> hostnames and client domain names are out of its scope and remain your
> responsibility. Setup and limits: `tools/data-sovereignty/README.md`.
> Run an audit any time with `python3 tools/data-sovereignty/scan.py --all`.

## NEVER store in any file in this knowledge base

- Email addresses (any format)
- Usernames or account names specific to a client environment
- Domain names specific to a client (e.g., contoso.com, client-corp.local)
- Company names or client identifiers
- IP addresses that belong to a client network
- Hostnames specific to a client (e.g., WS01-CLIENT, DC01-CORP)
- Any value from a log sample that could identify a specific person or organization

## When an analyst pastes a log sample

Extract ONLY:
- Field names and their types
- The structure of dynamic/nested fields
- Example values that are clearly generic (e.g., EventID numbers, protocol names, ActionType strings)

Never save actual log line values, account names, IPs, or hostnames from client log samples.

## NOT ALLOWED — external services that process user data

- External transcription, OCR, translation services
- AI services other than Claude
- Online file converters or online tools
- Any service that requires uploading user data to a third-party endpoint

## ALLOWED

- Anthropic's Claude services
- Local Python libraries for KQL static analysis
- Read-only documentation websites

## When unsure

If a request would route data through an external service, say so explicitly and offer the local alternative.
