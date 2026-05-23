---
description: What to do at the start and end of every session
---

# Session discipline

## Session start (every session)

1. Read the files listed under "Always read at session start" in `CLAUDE.md`.
2. Read the 3 most recent entries in `05-sessions/` (sorted by filename date).
3. Skim `07-questions/open-questions.md` for unresolved questions.
4. In one short paragraph, state:
   - What context was loaded.
   - Any unresolved questions worth flagging to the analyst.

Do this silently and concisely. Do not list every file read. One paragraph is enough.

## Session end (substantive sessions only)

A session is "substantive" if any of the following occurred:
- A KQL detection was generated or revised.
- A schema file was added or updated.
- A lesson was captured.
- An ADR was written.
- A significant design decision was made.

If substantive, before the session context is lost:

1. Write `05-sessions/YYYY-MM-DD-<short-slug>.md` with:
   - **What was requested** — the analyst's detection goal.
   - **What was produced** — queries, rules, schemas added.
   - **Lessons captured** — lesson IDs written this session.
   - **Open questions** — anything unresolved that should carry forward.
   - **Files modified** — list of files written or updated.

2. Update any relevant `_index.md` files (e.g., `08-generated/_index.md` if a new detection was saved).

3. Mention in one line what was written: "Session journal written to 05-sessions/2026-05-23-kerberoasting.md."

## Do not ask permission

Write the session journal automatically. The analyst does not need to request it.

## File naming

Session journals: `YYYY-MM-DD-<kebab-case-topic>.md`
Example: `2026-05-23-password-spray-detection.md`

If multiple sessions occur on the same date, append a sequence number: `2026-05-23-02-lateral-movement.md`.
