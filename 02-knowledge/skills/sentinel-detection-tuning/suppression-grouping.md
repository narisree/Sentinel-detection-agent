# Suppression and Incident Grouping

Distilled from `02-knowledge/house-style/metadata-standards.md` §8 and §9.
Consult when configuring the Sentinel Analytics Rule scheduling, suppression, and incident creation settings.

---

## Suppression (Deduplication Within a Rule)

Suppression prevents the same alert from firing repeatedly for the same entity within a time window. Set this in the Analytics Rule → Suppression section.

| Scenario | Suppression period | Suppress by |
|---|---|---|
| Brute-force / ongoing attack | 1 hour | Account + Source IP |
| Malware detection | 4 hours | Device |
| Beaconing / C2 connection | 1 hour | Device + Remote IP |
| Service account anomaly | 24 hours | Account |
| Policy change (each matters) | None (disable suppression) | — |
| Privileged role assignment | None | — |

**Note:** Suppression applies within this rule only. Cross-rule deduplication happens at the incident level.

---

## Incident Grouping

Controls how multiple alerts from the same rule are grouped into incidents.

### Group into one incident when:
- The attack is ongoing and generates many alerts (brute-force, C2 beaconing).
- The same entity (account/device/IP) is the attacker or victim repeatedly.
- **Grouping key:** Account, Host, or IP entity.

### Create a new incident per alert when:
- Each occurrence is independently significant (privilege escalation, log clearing).
- Entity is unknown or highly variable.

### Recommended settings by severity

| Severity | Grouping | Time window |
|---|---|---|
| High | One incident per entity (Account or Host) | 24 hours |
| Medium | Group by Account + Source IP | 4 hours |
| Low | Group by Account | 24 hours |
| Informational | Group all | 24 hours |

---

## Entity Mapping (required for incident grouping to work)

Sentinel needs entity columns in the query output to group incidents correctly. These must be explicitly projected and named.

| Entity type | Column name to use | Example field |
|---|---|---|
| Account | `AccountName` + `AccountDomain` | `TargetUserName`, `TargetDomainName` |
| Host | `HostName` | `Computer`, `DeviceName` |
| IP | `IPAddress` | `IpAddress`, `RemoteIP` |
| URL | `Url` | Full URL string |
| File | `FileName` + `FolderPath` | From DeviceFileEvents |
| Process | `ProcessId` + `CommandLine` | From DeviceProcessEvents |

**Minimum:** Every analytics rule must map at least one entity. High-severity rules should map Account + Host + IP where available.
