# Known Mistakes

Hard errors the agent has made that must be checked before every generation. This list is the first thing consulted in Step 2 of the KQL generation workflow.

**Rule:** If a mistake appears here, it must be actively guarded against — not just noted.

---

### KM-001 — Wrong time field for MDE tables

- **Applies to:** All `Device*` tables (DeviceProcessEvents, DeviceEvents, DeviceNetworkEvents, DeviceFileEvents, DeviceLogonEvents, DeviceRegistryEvents)
- **Mistake:** Using `TimeGenerated` as the time filter column.
- **Correct:** Use `Timestamp` for all MDE tables.
- **Check:** Before writing any query against a `Device*` table, verify the time field is `Timestamp`.

```kql
// WRONG
DeviceProcessEvents | where TimeGenerated > ago(1d)

// CORRECT
DeviceProcessEvents | where Timestamp > ago(1d)
```

---

<!-- Additional known mistakes appended below as they are discovered. -->
