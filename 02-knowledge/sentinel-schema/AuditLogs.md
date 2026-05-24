# AuditLogs — Microsoft Sentinel Schema Reference

**Table description:** Azure Active Directory (Microsoft Entra ID) audit logs. Captures all administrative and configuration changes made within the directory: user management, group management, application registration, role assignment, conditional access changes, and more.

**Data connector:** Azure Active Directory (Entra ID) — Audit Logs
**Primary time field:** `TimeGenerated` (datetime)
**Related tables:** `SigninLogs`, `AADNonInteractiveUserSignInLogs`, `AADServicePrincipalSignInLogs`
**Workspace table type:** Log Analytics workspace table

---

## Column Schema

| Column | Type | Description | Example Value |
|--------|------|-------------|---------------|
| `TimeGenerated` | datetime | Time the event was ingested into Log Analytics | `2024-06-01T14:23:11Z` |
| `ActivityDateTime` | datetime | Time the activity occurred in Azure AD | `2024-06-01T14:23:10Z` |
| `OperationName` | string | High-level operation category name | `Add member to role` |
| `ActivityDisplayName` | string | Specific activity name | `Add member to role` |
| `Category` | string | Log category | `RoleManagement` |
| `Result` | string | Operation result | `success`, `failure`, `timeout` |
| `ResultReason` | string | Reason for the result | `" "`, `"User was blocked"` |
| `Id` | string | Unique ID for the audit event (GUID) | `aaaa-bbbb-cccc-dddd` |
| `CorrelationId` | string | Correlation ID linking related events | `eeee-ffff-...` |
| `Identity` | string | Display name of the actor | `John Admin` |
| `LoggedByService` | string | Service that logged the event | `Core Directory`, `B2C`, `PIM`, `Invited User Experience`, `Access Reviews`, `Terms Of Use`, `Microsoft Managed Desktop` |
| `InitiatedBy` | dynamic | Actor who performed the operation (user or app) | `{"user":{"id":"...","displayName":"John Admin","userPrincipalName":"jadmin@contoso.com","ipAddress":"203.0.113.1"},"app":null}` |
| `TargetResources` | dynamic | Array of resources affected by the operation | `[{"id":"...","displayName":"Jane Doe","type":"User","userPrincipalName":"jdoe@contoso.com","groupType":null,"modifiedProperties":[...]}]` |
| `AdditionalDetails` | dynamic | Array of key-value pairs for extra details | `[{"key":"UserType","value":"Member"},{"key":"ipaddr","value":"10.0.0.1"}]` |
| `Type` | string | Table name identifier | `AuditLogs` |

---

## `InitiatedBy` Field Structure

> **IMPORTANT — parse_json(tostring()) required (production-verified):**
> `InitiatedBy.user` is sometimes stored as a doubly-serialized JSON string within the dynamic column.
> Direct dot notation (`InitiatedBy.user.userPrincipalName`) silently returns null in those cases.
> Always use `parse_json(tostring(InitiatedBy.user)).fieldName` to force explicit re-parsing.

```kql
// CORRECT — production-verified pattern
AuditLogs
| extend Actor = tostring(parse_json(tostring(InitiatedBy.user)).userPrincipalName)

// WRONG — direct dot notation; silently returns null when user sub-object is doubly-serialized
// | extend Actor = tostring(InitiatedBy.user.userPrincipalName)
```

```kql
// Access user actor fields (use parse_json(tostring()) pattern)
AuditLogs
| extend ActorUPN          = tostring(parse_json(tostring(InitiatedBy.user)).userPrincipalName)
| extend ActorDisplayName  = tostring(parse_json(tostring(InitiatedBy.user)).displayName)
| extend ActorId           = tostring(parse_json(tostring(InitiatedBy.user)).id)
| extend ActorIPAddress    = tostring(parse_json(tostring(InitiatedBy.user)).ipAddress)

// Access app actor fields (service principal / managed identity)
| extend AppDisplayName    = tostring(InitiatedBy.app.displayName)
| extend AppId             = tostring(InitiatedBy.app.appId)
| extend AppServicePrincipalId = tostring(InitiatedBy.app.servicePrincipalId)
| extend AppServicePrincipalName = tostring(InitiatedBy.app.servicePrincipalName)

// Actor is either a user or app; one will be null
| extend ActorName = coalesce(
    tostring(parse_json(tostring(InitiatedBy.user)).userPrincipalName),
    tostring(InitiatedBy.app.displayName),
    "Unknown"
  )
```

---

## `TargetResources` Field Structure

`TargetResources` is a **dynamic array**. Each element has:

```json
{
  "id": "<object-id-guid>",
  "displayName": "Jane Doe",
  "type": "User",
  "userPrincipalName": "jdoe@contoso.com",
  "groupType": null,
  "modifiedProperties": [
    {
      "displayName": "AccountEnabled",
      "oldValue": "[\"True\"]",
      "newValue": "[\"False\"]"
    }
  ]
}
```

**Type values:** `User`, `Group`, `Application`, `ServicePrincipal`, `Device`, `Role`, `Policy`, `Other`

```kql
// Access first target resource (most operations have one primary target)
AuditLogs
| extend TargetId    = tostring(TargetResources[0].id)
| extend TargetName  = tostring(TargetResources[0].displayName)
| extend TargetType  = tostring(TargetResources[0].type)
| extend TargetUPN   = tostring(TargetResources[0].userPrincipalName)

// Expand all targets (for multi-target operations)
| mv-expand TargetResources
| extend TargetName = tostring(TargetResources.displayName)
| extend TargetType = tostring(TargetResources.type)
```

---

## `AdditionalDetails` Field — Operation-Specific Values

`AdditionalDetails` is a dynamic array of key-value pairs. Array index and key content vary by operation.

### "Add service principal" operation

```kql
// AppId of the newly added service principal is at index [1]
AuditLogs
| where OperationName == "Add service principal"
| extend AppId = tostring(AdditionalDetails[1].value)
```

> **Verified:** `AdditionalDetails[1].value` holds the Application (client) ID — the most useful field
> for follow-up investigation of the service principal created.

### Generic key-value access (when index is unknown)

```kql
// Expand and filter by key name
AuditLogs
| mv-expand AdditionalDetails
| extend KeyName  = tostring(AdditionalDetails.key)
| extend KeyValue = tostring(AdditionalDetails.value)
| where KeyName == "AppId"
```

---

## `modifiedProperties` Parsing

Each modified property has `displayName`, `oldValue`, and `newValue`. Values are JSON-encoded strings (e.g., `"[\"True\"]"`).

> **IMPORTANT — doubly-serialized (production-verified):**
> `TargetResources[0].modifiedProperties` is stored as a serialized JSON string within the dynamic column.
> Access requires two layers of `parse_json(tostring(...))`.
> The role name entry is at **index [1]**.
> For **add** operations use `newValue`; for **remove** operations use `oldValue`.

### Role name extraction (production-verified pattern)

```kql
// For "Add member to role" — role name is in newValue
AuditLogs
| where OperationName == "Add member to role"
| where Identity <> "MS-PIM"   // exclude PIM-initiated events
| extend User = tostring(TargetResources[0].userPrincipalName)
| extend Role = tostring(parse_json(tostring(parse_json(tostring(TargetResources[0].modifiedProperties))[1].newValue)))

// For "Remove member from role" — role name is in oldValue (NOT newValue)
AuditLogs
| where OperationName == "Remove member from role"
| where Identity <> "MS-PIM"
| extend User = tostring(TargetResources[0].userPrincipalName)
| extend Role = tostring(parse_json(tostring(parse_json(tostring(TargetResources[0].modifiedProperties))[1].oldValue)))
```

### PIM exclusion

Azure AD PIM-initiated role operations set `Identity == "MS-PIM"`. Always filter `| where Identity <> "MS-PIM"` in role assignment detections to suppress PIM noise.

---

## Common `ActivityDisplayName` Values

### User Management
| ActivityDisplayName | Description |
|--------------------|-------------|
| `Add user` | New user created in directory |
| `Update user` | User attributes updated |
| `Delete user` | User account deleted |
| `Reset user password` | Admin reset a user's password |
| `Change user password` | User changed their own password |
| `Update StsRefreshTokenValidFrom Timestamp` | All refresh tokens revoked (forced signout) |
| `Disable account` | User account disabled |
| `Enable account` | User account enabled |
| `Set force change user password` | Force password change on next logon |

### Group Management
| ActivityDisplayName | Description |
|--------------------|-------------|
| `Add group` | New group created |
| `Update group` | Group properties updated |
| `Delete group` | Group deleted |
| `Add member to group` | Member added to group |
| `Remove member from group` | Member removed from group |
| `Add owner to group` | Owner added to group |
| `Remove owner from group` | Owner removed |

### Role Management
| ActivityDisplayName | Description |
|--------------------|-------------|
| `Add member to role` | User/SP added to a directory role |
| `Remove member from role` | User/SP removed from a directory role |
| `Add eligible member to role` | PIM eligible role assignment added |
| `Remove eligible member from role` | PIM eligible role removed |
| `Add scoped member to role` | Scoped role assignment |

### Application Management
| ActivityDisplayName | Description |
|--------------------|-------------|
| `Add application` | New app registration created |
| `Update application` | App properties updated |
| `Delete application` | App registration deleted |
| `Add service principal` | Enterprise app (service principal) created |
| `Delete service principal` | Enterprise app deleted |
| `Update service principal` | SP properties updated |
| `Add owner to application` | Owner added to app registration |
| `Remove owner from application` | Owner removed |
| `Add app role assignment to service principal` | Service principal granted app role |
| `Add delegated permission grant` | OAuth2 permission grant added |
| `Remove delegated permission grant` | OAuth2 grant removed |
| `Add app role assignment grant to user` | User granted app role |
| `Consent to application` | User or admin consented to an application |

### Conditional Access
| ActivityDisplayName | Description |
|--------------------|-------------|
| `Add conditional access policy` | New CA policy created |
| `Update conditional access policy` | CA policy modified |
| `Delete conditional access policy` | CA policy deleted |

### MFA / Authentication
| ActivityDisplayName | Description |
|--------------------|-------------|
| `Update per-user MFA method` | MFA method changed |
| `Register security info` | User registered MFA method |
| `Delete security info` | MFA method removed |
| `Admin registered security info for user` | Admin-registered MFA |

---

## `LoggedByService` Values

| Value | Logs from |
|-------|-----------|
| `Core Directory` | Most directory operations |
| `PIM` | Privileged Identity Management |
| `Access Reviews` | Azure AD Access Reviews |
| `B2C` | Azure AD B2C tenant |
| `Invited User Experience` | Guest user invitations |
| `Terms Of Use` | ToU acceptance/rejection |
| `Entitlement Management` | Access packages |
| `Microsoft Managed Desktop` | MMD device management |
| `Authentication Methods` | MFA / SSPR operations |


```kql
AuditLogs
| where TimeGenerated > ago(7d)
| where ActivityDisplayName == "Add member to role"
| extend ActorUPN  = tostring(InitiatedBy.user.userPrincipalName)
| extend TargetUPN = tostring(TargetResources[0].userPrincipalName)
| extend TargetId  = tostring(TargetResources[0].id)
| mv-expand TargetResources
| mv-apply ModProp = TargetResources.modifiedProperties on (
    where tostring(ModProp.displayName) == "Role.DisplayName"
  )
| extend RoleName = replace_regex(tostring(ModProp.newValue), @'"', "")
| where RoleName in ("Global Administrator", "Privileged Role Administrator",
                     "Security Administrator", "Application Administrator",
                     "Cloud Application Administrator", "Exchange Administrator",
                     "SharePoint Administrator", "Helpdesk Administrator")
| project TimeGenerated, ActorUPN, TargetUPN, RoleName, Result, LoggedByService
| sort by TimeGenerated desc
```

### Malicious OAuth Consent Grant Detection

```kql
AuditLogs
| where TimeGenerated > ago(7d)
| where ActivityDisplayName in ("Consent to application", "Add delegated permission grant")
| extend ActorUPN   = tostring(InitiatedBy.user.userPrincipalName)
| extend AppName    = tostring(TargetResources[0].displayName)
| extend AppId      = tostring(TargetResources[0].id)
| mv-expand AdditionalDetails
| extend KeyName    = tostring(AdditionalDetails.key)
| extend KeyValue   = tostring(AdditionalDetails.value)
| where KeyName == "Permissions" and (
    KeyValue has_any ("Mail.Read", "Mail.ReadWrite", "Contacts.Read",
                      "Files.Read.All", "Files.ReadWrite.All",
                      "Directory.Read.All", "offline_access")
  )
| project TimeGenerated, ActorUPN, AppName, AppId, KeyValue, Result
```

### New Application Owner Added

```kql
AuditLogs
| where TimeGenerated > ago(7d)
| where ActivityDisplayName in ("Add owner to application", "Add owner to service principal")
| extend ActorUPN    = tostring(InitiatedBy.user.userPrincipalName)
| extend AppName     = tostring(TargetResources[0].displayName)
| extend NewOwnerUPN = tostring(TargetResources[1].userPrincipalName)
| project TimeGenerated, ActorUPN, AppName, NewOwnerUPN, Result, LoggedByService
```

### User Created Outside Business Hours

```kql
AuditLogs
| where TimeGenerated > ago(7d)
| where ActivityDisplayName == "Add user"
| extend ActorUPN    = tostring(InitiatedBy.user.userPrincipalName)
| extend TargetUPN   = tostring(TargetResources[0].userPrincipalName)
| extend HourOfDay   = hourofday(TimeGenerated)
| extend IsWeekend   = toint(dayofweek(TimeGenerated) / 1d) in (5, 6)
| where HourOfDay < 7 or HourOfDay >= 20 or IsWeekend
| project TimeGenerated, ActorUPN, TargetUPN, HourOfDay, IsWeekend, Result
```

### MFA Method Deleted (Potential Takeover Prep)

```kql
AuditLogs
| where TimeGenerated > ago(7d)
| where ActivityDisplayName in ("Delete security info", "Admin deleted security info for user")
| extend ActorUPN    = tostring(InitiatedBy.user.userPrincipalName)
| extend TargetUPN   = tostring(TargetResources[0].userPrincipalName)
| extend MFAMethod   = tostring(TargetResources[0].displayName)
// Flag if actor != target (admin deleted someone else's MFA)
| where ActorUPN != TargetUPN
| project TimeGenerated, ActorUPN, TargetUPN, MFAMethod, Result, LoggedByService
```

### PIM Role Activation (Eligible Role Used)

```kql
AuditLogs
| where TimeGenerated > ago(1d)
| where LoggedByService == "PIM"
| where ActivityDisplayName has_any ("activated", "Activate")
| extend ActorUPN     = tostring(InitiatedBy.user.userPrincipalName)
| extend TargetRoleId = tostring(TargetResources[0].id)
| mv-expand TargetResources
| mv-apply ModProp = TargetResources.modifiedProperties on (
    where tostring(ModProp.displayName) == "Role.DisplayName"
  )
| extend RoleName = replace_regex(tostring(ModProp.newValue), @'"', "")
| project TimeGenerated, ActorUPN, RoleName, Result
```

### Mass Password Reset (Potential Credential Takeover Campaign)

```kql
AuditLogs
| where TimeGenerated > ago(1h)
| where ActivityDisplayName == "Reset user password"
| extend ActorUPN = tostring(InitiatedBy.user.userPrincipalName)
| summarize
    ResetCount    = count(),
    AffectedUsers = make_set(tostring(TargetResources[0].userPrincipalName), 50),
    FirstReset    = min(TimeGenerated),
    LastReset     = max(TimeGenerated)
  by ActorUPN
| where ResetCount >= 5
| sort by ResetCount desc
```
