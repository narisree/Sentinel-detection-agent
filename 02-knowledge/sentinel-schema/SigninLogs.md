# SigninLogs — Microsoft Sentinel Schema Reference

**Table description:** Azure Active Directory (now Microsoft Entra ID) interactive and non-interactive sign-in logs. Includes all user sign-in events to Azure AD-integrated applications, including Microsoft 365, Azure portal, and third-party SaaS. Populated by the Azure Active Directory Diagnostic Settings data connector.

**Data connector:** Azure Active Directory (Entra ID) — Sign-in Logs
**Primary time field:** `TimeGenerated` (datetime)
**Related tables:** `AADNonInteractiveUserSignInLogs`, `AADServicePrincipalSignInLogs`, `AADManagedIdentitySignInLogs`
**Workspace table type:** Log Analytics workspace table

---

## Column Schema

| Column | Type | Description | Example Value |
|--------|------|-------------|---------------|
| `TimeGenerated` | datetime | Time event was ingested into Log Analytics | `2024-06-01T14:23:11Z` |
| `CreatedDateTime` | datetime | Original sign-in timestamp from Azure AD | `2024-06-01T14:23:10Z` |
| `UserDisplayName` | string | Full display name of the user | `Jane Doe` |
| `UserPrincipalName` | string | UPN of the user (email-format) | `jdoe@contoso.com` |
| `UserId` | string | Azure AD Object ID of the user (GUID) | `a1b2c3d4-...` |
| `AppDisplayName` | string | Name of the application being accessed | `Microsoft Teams` |
| `AppId` | string | Application (client) ID GUID | `1fec8e78-...` |
| `ResourceDisplayName` | string | Name of the resource being accessed | `Microsoft Graph` |
| `ResourceId` | string | Resource ID GUID | `00000003-...` |
| `ClientAppUsed` | string | Client application type | `Browser` |
| `UserAgent` | string | HTTP User-Agent string of the client | `Mozilla/5.0 ...` |
| `IPAddress` | string | Client IP address | `203.0.113.45` |
| `IsInteractive` | bool | Whether it is an interactive sign-in | `true` |
| `CorrelationId` | string | Correlation ID linking related sign-in events | `aaaa-bbbb-cccc-dddd` |
| `OriginalRequestId` | string | Original request ID | `eeee-ffff-...` |
| `TransactionId` | string | Transaction ID | `gggg-hhhh-...` |
| `UniqueTokenIdentifier` | string | Unique token identifier for this session | `iiii-jjjj-...` |
| `OperationName` | string | Always `Sign-in activity` | `Sign-in activity` |
| `Category` | string | Log category | `SignInLogs` |
| `Identity` | string | User identity claimed | `jdoe@contoso.com` |
| `Level` | int | Severity level | `4` |
| `ResultType` | string | Sign-in result code (string of int) | `"0"` (success) or `"50126"` |
| `ResultDescription` | string | Description of the sign-in result | `Invalid username or password or Invalid on-premises username or password.` |
| `ResultSignature` | string | ADAL result signature | `None` |
| `AuthenticationRequirement` | string | Primary or MFA requirement | `singleFactorAuthentication` |
| `ConditionalAccessStatus` | string | Result of Conditional Access evaluation | `success`, `failure`, `notApplied`, `notEnabled` |
| `RiskDetail` | string | Reason behind risk state | `none`, `adminGeneratedTemporaryPassword`, `userPerformedSecuredPasswordChange`, `aiConfirmedSigninSafe`, `userPassedMFADrivenByRiskBasedPolicy` |
| `RiskEventTypes` | dynamic | List of risk event types detected | `["unfamiliarFeatures","anonymizedIPAddress"]` |
| `RiskEventTypes_V2` | string | Comma-separated risk event types (v2) | `"unfamiliarFeatures,anonymizedIPAddress"` |
| `RiskLevelAggregated` | string | Aggregated risk level | `none`, `low`, `medium`, `high`, `hidden`, `unknownFutureValue` |
| `RiskLevelDuringSignIn` | string | Risk level at time of sign-in | `none`, `low`, `medium`, `high` |
| `RiskState` | string | Risk state of the user | `none`, `confirmedSafe`, `remediated`, `dismissed`, `atRisk`, `confirmedCompromised` |
| `MfaDetail` | dynamic | MFA method and result details | `{"authMethod":"PhoneAppNotification","authDetail":"MFA completed in Azure AD"}` |
| `Status` | dynamic | Status object with error and failure details | `{"errorCode":0,"failureReason":"Other","additionalDetails":"MFA requirement satisfied by claim..."}` |
| `DeviceDetail` | dynamic | Device information | `{"deviceId":"...","displayName":"...","operatingSystem":"Windows","browser":"Edge 121.0","isCompliant":true,"isManaged":true,"trustType":"AzureAD"}` |
| `Location` | dynamic | Geographic location of the sign-in | `{"city":"London","state":"England","countryOrRegion":"GB","geoCoordinates":{"latitude":51.5074,"longitude":-0.1278}}` |
| `NetworkLocationDetails` | dynamic | Network location details | `[{"networkType":"namedNetwork","networkNames":["Corpnet"]}]` |
| `AuthenticationDetails` | dynamic | Array of authentication steps taken | `[{"authenticationStepDateTime":"...","authenticationMethod":"Password","authenticationMethodDetail":"Password in the cloud","succeeded":true,"resultDetail":"MFA requirement satisfied","authenticationStepRequirement":"Primary authentication"}]` |
| `AuthenticationProcessingDetails` | dynamic | Processing details for each authentication step | |
| `ConditionalAccessPolicies` | dynamic | Array of CA policies evaluated | `[{"id":"...","displayName":"Require MFA for All Users","enforcedGrantControls":["Mfa"],"enforcedSessionControls":[],"result":"success"}]` |
| `AppliedConditionalAccessPolicies` | dynamic | Alias/older field for CA policies | |
| `TokenIssuerType` | string | Token issuer | `AzureAD`, `ADFS`, `UnknownFutureValue` |
| `TokenIssuerName` | string | Name of the token issuer (ADFS federation) | `FS.contoso.com` |
| `ProcessingTimeInMilliseconds` | string | Sign-in processing time in ms | `"342"` |
| `IncomingTokenType` | string | Type of incoming token | `"none"` |
| `FlaggedForReview` | bool | Whether admin flagged this sign-in | `false` |
| `HomeTenantId` | string | Home tenant ID GUID | `aaaa-bbbb-...` |
| `CrossTenantAccessType` | string | Cross-tenant access type | `none`, `b2bCollaboration`, `b2bDirectConnect`, `microsoftSupport`, `serviceProvider` |
| `ServicePrincipalId` | string | Service principal ID if applicable | |
| `ServicePrincipalName` | string | Service principal name if applicable | |
| `SignInEventTypes` | dynamic | Type(s) of sign-in event | `["interactiveUser"]` |
| `Type` | string | Table name | `SignInLogs` |

---

## ResultType Values

`ResultType` is stored as a **string** representation of an integer.

| ResultType | Meaning | Action |
|-----------|---------|--------|
| `"0"` | Success | Normal |
| `"50126"` | Invalid credentials — invalid username or password | Failed logon |
| `"50053"` | Account locked out (smart lockout) | Brute force trigger |
| `"50055"` | Password expired | Normal expiry |
| `"50057"` | Account disabled | Investigate |
| `"50058"` | Silent sign-in interrupt — user needs to sign in interactively | |
| `"50072"` | User needs to enroll in MFA | |
| `"50074"` | Strong auth required (MFA required) | CA policy enforced |
| `"50076"` | MFA required (new requirement) | |
| `"50079"` | User requires MFA registration | |
| `"50097"` | Device authentication required | |
| `"50105"` | User not assigned to the application | |
| `"50125"` | Sign-in was interrupted due to a password reset | |
| `"50128"` | Invalid domain name — no tenant found | |
| `"50129"` | Device is not workplace joined | |
| `"50131"` | Conditional Access error | |
| `"50133"` | Session invalid due to password expiration or password change | |
| `"50135"` | Password change required due to account risk | |
| `"50140"` | Keep-me-signed-in interrupt | |
| `"51006"` | Session token missing | |
| `"53000"` | Conditional Access policy requires a compliant device | |
| `"53001"` | Conditional Access policy requires a domain-joined device | |
| `"53003"` | Blocked by Conditional Access policy | |
| `"53004"` | CA requires a compliant device for MFA | |
| `"65001"` | User has not consented to use the application | |
| `"70011"` | Invalid scope (OAuth) | |
| `"70016"` | OAuth flow device authorization code expired | |
| `"80012"` | Allowed working hours violation | |
| `"90014"` | Field missing in authentication request | |
| `"90093"` | Graph returned forbidden error for this request | |

**KQL filter for failures only:**
```kql
SigninLogs
| where ResultType != "0"
```

---

## ConditionalAccessStatus Values

| Value | Meaning |
|-------|---------|
| `success` | CA policy evaluated and all controls satisfied |
| `failure` | CA policy blocked the sign-in |
| `notApplied` | No CA policies matched this sign-in |
| `notEnabled` | CA not configured for tenant |

---

## RiskLevel Values

| Value | Description |
|-------|-------------|
| `none` | No risk detected |
| `low` | Low risk; unusual sign-in patterns |
| `medium` | Medium risk; suspicious activity |
| `high` | High risk; likely compromise |
| `hidden` | Risk hidden by policy |

---

## RiskState Values

| Value | Description |
|-------|-------------|
| `none` | No risk |
| `confirmedSafe` | Admin confirmed this sign-in was safe |
| `remediated` | Risk remediated (e.g., password change) |
| `dismissed` | Risk dismissed by admin |
| `atRisk` | User is at risk |
| `confirmedCompromised` | Admin confirmed account compromise |

---

## ClientAppUsed Values

| Value | Description |
|-------|-------------|
| `Browser` | Web browser |
| `Mobile Apps and Desktop clients` | MSAL-based modern auth apps |
| `Exchange ActiveSync` | EAS protocol (mobile email) |
| `SMTP` | SMTP relay authentication |
| `IMAP4` | IMAP email client |
| `POP3` | POP3 email client |
| `Other clients` | Other/legacy protocols |

---

## Accessing Dynamic Fields

```kql
// Location fields
SigninLogs
| extend City       = tostring(Location.city)
| extend State      = tostring(Location.state)
| extend Country    = tostring(Location.countryOrRegion)
| extend Latitude   = toreal(Location.geoCoordinates.latitude)
| extend Longitude  = toreal(Location.geoCoordinates.longitude)

// Status fields
| extend ErrorCode   = toint(Status.errorCode)
| extend FailReason  = tostring(Status.failureReason)
| extend AddDetails  = tostring(Status.additionalDetails)

// Device details
| extend DeviceOS       = tostring(DeviceDetail.operatingSystem)
| extend Browser        = tostring(DeviceDetail.browser)
| extend IsCompliant    = tobool(DeviceDetail.isCompliant)
| extend IsManaged      = tobool(DeviceDetail.isManaged)
| extend TrustType      = tostring(DeviceDetail.trustType)
| extend DeviceName     = tostring(DeviceDetail.displayName)

// MFA details
| extend MFAMethod  = tostring(MfaDetail.authMethod)
| extend MFAResult  = tostring(MfaDetail.authDetail)

// Initiating user in AuditLogs context (not SigninLogs but pattern)
// For SigninLogs: the signing-in user IS the subject
```


```kql
let timeDelta = 1h;
let distanceThreshold = 500; // km
SigninLogs
| where TimeGenerated > ago(1d)
| where ResultType == "0"
| extend Latitude  = toreal(Location.geoCoordinates.latitude)
| extend Longitude = toreal(Location.geoCoordinates.longitude)
| extend Country   = tostring(Location.countryOrRegion)
| where isnotnull(Latitude) and isnotnull(Longitude)
| sort by UserPrincipalName asc, TimeGenerated asc
| serialize
| extend PrevTime    = prev(TimeGenerated)
| extend PrevLat    = prev(Latitude)
| extend PrevLon    = prev(Longitude)
| extend PrevCountry = prev(Country)
| extend PrevUser   = prev(UserPrincipalName)
| where PrevUser == UserPrincipalName
| extend TimeDiffHours = datetime_diff("minute", TimeGenerated, PrevTime) / 60.0
| where TimeDiffHours > 0 and TimeDiffHours < 6
| extend DistanceKm = geo_distance_2points(Longitude, Latitude, PrevLon, PrevLat) / 1000.0
| where DistanceKm > distanceThreshold
| extend SpeedKmh = DistanceKm / TimeDiffHours
| where SpeedKmh > 900   // faster than commercial aircraft
| project TimeGenerated, UserPrincipalName, IPAddress, Country, PrevCountry, DistanceKm, SpeedKmh, AppDisplayName
```

### Password Spray Detection (Many Users, One IP)

```kql
SigninLogs
| where TimeGenerated > ago(1h)
| where ResultType == "50126"   // bad password
| summarize
    FailCount     = count(),
    TargetUsers   = dcount(UserPrincipalName),
    UserList      = make_set(UserPrincipalName, 20),
    FirstSeen     = min(TimeGenerated),
    LastSeen      = max(TimeGenerated)
  by IPAddress, bin(TimeGenerated, 10m)
| where TargetUsers >= 5
| sort by FailCount desc
```

### MFA Fatigue / Push Bombing Detection

```kql
SigninLogs
| where TimeGenerated > ago(1h)
| where ResultType in ("50074", "50076")        // MFA required but not satisfied
| extend MFAMethod = tostring(MfaDetail.authMethod)
| where MFAMethod has_any ("PhoneAppNotification", "Notification")
| summarize
    MFAPromptCount = count(),
    UniqueIPs      = dcount(IPAddress),
    FirstPrompt    = min(TimeGenerated),
    LastPrompt     = max(TimeGenerated)
  by UserPrincipalName, bin(TimeGenerated, 30m)
| where MFAPromptCount >= 5
| sort by MFAPromptCount desc
```

### Successful Sign-In from High-Risk Location

```kql
let HighRiskCountries = dynamic(["CN","RU","KP","IR","BY","CU"]);
SigninLogs
| where TimeGenerated > ago(1d)
| where ResultType == "0"
| extend Country = tostring(Location.countryOrRegion)
| where Country in (HighRiskCountries)
| where not(ipv4_is_in_range(IPAddress, "10.0.0.0/8"))
      and not(ipv4_is_in_range(IPAddress, "192.168.0.0/16"))
| project TimeGenerated, UserPrincipalName, IPAddress, Country, AppDisplayName, ClientAppUsed, RiskLevelDuringSignIn
```

### Suspicious Legacy Protocol Sign-In

```kql
SigninLogs
| where TimeGenerated > ago(1d)
| where ResultType == "0"
| where ClientAppUsed in ("Exchange ActiveSync", "SMTP", "IMAP4", "POP3", "Other clients")
| where AuthenticationRequirement == "singleFactorAuthentication"  // no MFA
| summarize
    Count    = count(),
    LastSeen = max(TimeGenerated)
  by UserPrincipalName, ClientAppUsed, IPAddress
| sort by Count desc
```

### Blocked by Conditional Access After Multiple Attempts

```kql
SigninLogs
| where TimeGenerated > ago(1h)
| where ResultType == "53003"   // blocked by CA
| summarize
    BlockCount = count(),
    IPList     = make_set(IPAddress, 10),
    AppList    = make_set(AppDisplayName, 10)
  by UserPrincipalName, bin(TimeGenerated, 15m)
| where BlockCount >= 3
| sort by BlockCount desc
```

### Sign-In Anomaly — First-Time Country

```kql
let lookbackPeriod = 30d;
let recentWindow   = 1d;
let HistoricalCountries = SigninLogs
    | where TimeGenerated between (ago(lookbackPeriod) .. ago(recentWindow))
    | where ResultType == "0"
    | extend Country = tostring(Location.countryOrRegion)
    | summarize HistoricalCountries = make_set(Country) by UserPrincipalName;
SigninLogs
| where TimeGenerated > ago(recentWindow)
| where ResultType == "0"
| extend Country = tostring(Location.countryOrRegion)
| join kind=leftouter (HistoricalCountries) on UserPrincipalName
| where not(set_has_element(HistoricalCountries, Country))
| project TimeGenerated, UserPrincipalName, IPAddress, Country, AppDisplayName
```
