# Syslog — Microsoft Sentinel Schema Reference

**Table description:** Linux syslog messages collected via the Microsoft Monitoring Agent (MMA/OMS), Azure Monitor Agent (AMA), or rsyslog/syslog-ng forwarded to the Log Analytics workspace. Covers standard POSIX syslog messages from Linux servers, network devices, and other Unix-like systems.

**Data connector:** Syslog via AMA / Syslog via Legacy Agent (MMA)
**Primary time field:** `TimeGenerated` (datetime)
**Related tables:** `CommonSecurityLog` (for CEF-formatted syslog from firewalls/IDS)
**Workspace table type:** Log Analytics workspace table

---

## Column Schema

| Column | Type | Description | Example Value |
|--------|------|-------------|---------------|
| `TimeGenerated` | datetime | Time event was ingested into Log Analytics | `2024-06-01T14:23:11Z` |
| `EventTime` | datetime | Timestamp from the syslog message header | `2024-06-01T14:23:10Z` |
| `Computer` | string | FQDN or hostname of the source system | `webserver01.contoso.com` |
| `HostName` | string | Hostname as reported in the syslog message | `webserver01` |
| `HostIP` | string | IP address of the source system | `10.0.1.50` |
| `Facility` | string | Syslog facility name (lowercase) | `auth` |
| `SeverityLevel` | string | Syslog severity level name | `err` |
| `ProcessName` | string | Name of the process that generated the log | `sshd` |
| `ProcessID` | int | PID of the process | `12345` |
| `SyslogMessage` | string | Full message content from the syslog entry | `Failed password for root from 203.0.113.1 port 22 ssh2` |
| `SourceSystem` | string | Collection agent | `OpsManager` |
| `Type` | string | Table name identifier | `Syslog` |
| `MG` | string | Management group name | `AOI-workspace-id` |

---

## Syslog Facility Values

| Facility Name | Numeric Code | Description |
|--------------|-------------|-------------|
| `kern` | 0 | Kernel messages |
| `user` | 1 | User-level messages |
| `mail` | 2 | Mail system |
| `daemon` | 3 | System daemons |
| `auth` | 4 | Security/authorization messages (login, su) |
| `syslog` | 5 | Messages generated internally by syslogd |
| `lpr` | 6 | Line printer subsystem |
| `news` | 7 | Network news subsystem |
| `uucp` | 8 | UUCP subsystem |
| `cron` | 9 | Clock/cron daemon |
| `security` | 10 | Security/authorization (synonym for auth on some systems) |
| `ftp` | 11 | FTP daemon |
| `ntp` | 12 | NTP subsystem |
| `logaudit` | 13 | Log audit |
| `logalert` | 14 | Log alert |
| `clock` | 15 | Clock daemon |
| `local0` | 16 | Local use 0 |
| `local1` | 17 | Local use 1 |
| `local2` | 18 | Local use 2 |
| `local3` | 19 | Local use 3 |
| `local4` | 20 | Local use 4 |
| `local5` | 21 | Local use 5 |
| `local6` | 22 | Local use 6 |
| `local7` | 23 | Local use 7 |

**Common usage:** `auth` and `authpriv` (facility 10 on some distros) contain SSH, sudo, PAM logs. `cron` contains scheduled task logs. `daemon` contains service logs.

---

## SeverityLevel Values

| Severity Name | Numeric Code | Description | Action |
|--------------|-------------|-------------|--------|
| `emerg` | 0 | System is unusable | Immediate response |
| `alert` | 1 | Action must be taken immediately | Immediate response |
| `crit` | 2 | Critical conditions | High priority |
| `err` | 3 | Error conditions | Investigate |
| `warning` | 4 | Warning conditions | Review |
| `notice` | 5 | Normal but significant condition | Review |
| `info` | 6 | Informational messages | Baseline |
| `debug` | 7 | Debug-level messages | Ignore in production |

**KQL filter for actionable severities:**
```kql
Syslog
| where SeverityLevel in ("emerg", "alert", "crit", "err", "warning")
```

---

## Common Log Patterns by Process

### SSH Authentication (`ProcessName == "sshd"`)

```
# Successful login
Accepted password for jdoe from 10.0.1.5 port 54321 ssh2
Accepted publickey for jdoe from 10.0.1.5 port 54321 ssh2: RSA SHA256:...

# Failed login
Failed password for jdoe from 203.0.113.1 port 12345 ssh2
Failed password for invalid user admin from 203.0.113.1 port 12345 ssh2
Invalid user webadmin from 203.0.113.1 port 54321

# Root login
ROOT LOGIN  on 'pts/0' from 10.0.1.5
Disconnecting invalid user guest 203.0.113.1 port 54321: Too many authentication failures

# Connection info
Connection from 203.0.113.1 port 12345 on 10.0.1.100 port 22 rdomain ""
session opened for user jdoe by (uid=0)
session closed for user jdoe

# Repeated failures trigger PAM
pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=203.0.113.1  user=jdoe
```

### Sudo (`ProcessName == "sudo"`)

```
# Successful sudo
jdoe : TTY=pts/1 ; PWD=/home/jdoe ; USER=root ; COMMAND=/bin/bash
jdoe : TTY=pts/1 ; PWD=/home/jdoe ; USER=root ; COMMAND=/usr/bin/cat /etc/shadow

# Authentication failure
jdoe : 3 incorrect password attempts ; TTY=pts/1 ; PWD=/home/jdoe ; USER=root ; COMMAND=/bin/su
jdoe : auth could not identify password for [jdoe]

# sudo to new shell (suspicious)
jdoe : TTY=pts/1 ; PWD=/home/jdoe ; USER=root ; COMMAND=/bin/bash --noprofile --norc
```

### PAM (`ProcessName` starts with `pam` or contains in message)

```
pam_unix(sudo:auth): authentication failure; logname=jdoe uid=1001 euid=0 tty=/dev/pts/1 ruser=jdoe rhost=  user=jdoe
pam_unix(su:session): session opened for user root by jdoe(uid=1001)
pam_unix(sshd:session): session closed for user jdoe
```

### Cron (`Facility == "cron"` or `ProcessName == "cron"/"CROND"`)

```
# Job execution
(root) CMD (/usr/sbin/run-parts /etc/cron.daily)
(jdoe) CMD (/home/jdoe/.hidden/beacon.sh)

# Crontab edit
(jdoe) BEGIN EDIT (jdoe)
(jdoe) END EDIT (jdoe)
```

### su Command

```
Successful su for root by jdoe
FAILED su for root by jdoe
+ pts/1 jdoe:root
```

### systemd/Service Events

```
systemd[1]: Started OpenSSH server daemon.
systemd[1]: Stopping OpenSSH server daemon.
systemd[1]: sshd.service: Deactivated successfully.
```

---

## Parsing SyslogMessage with the `parse` Operator

```kql
// Parse SSH failed password
Syslog
| where ProcessName == "sshd"
| where SyslogMessage has "Failed password"
| parse SyslogMessage with
    "Failed password for " ParsedUser
    " from " SrcIP
    " port " SrcPort
    " " Protocol

// Parse sudo
Syslog
| where ProcessName == "sudo"
| where SyslogMessage has "COMMAND"
| parse SyslogMessage with
    CallerUser " : TTY=" TTY
    " ; PWD=" WorkDir
    " ; USER=" RunAsUser
    " ; COMMAND=" SudoCommand

// Parse PAM authentication failure
Syslog
| where SyslogMessage has "authentication failure"
| parse kind=relaxed SyslogMessage with
    "pam_unix(" PamModule "): authentication failure; logname=" LogName
    " uid=" UID " euid=" EUID
    " tty=" TTY " ruser=" RUser
    " rhost=" RHost " user=" FailedUser
```


```kql
Syslog
| where TimeGenerated > ago(1h)
| where ProcessName == "sshd"
| where SyslogMessage has_any ("Failed password", "Invalid user", "authentication failure")
| parse kind=relaxed SyslogMessage with
    * "from " SrcIP " port " SrcPort " " *
| where isnotempty(SrcIP)
| summarize
    FailCount     = count(),
    TargetUsers   = dcount(Computer),
    FirstAttempt  = min(TimeGenerated),
    LastAttempt   = max(TimeGenerated)
  by SrcIP, bin(TimeGenerated, 10m)
| where FailCount >= 10
| sort by FailCount desc
```

### Successful SSH Login After Many Failures (Successful Brute Force)

```kql
let LookbackWindow = 1h;
let FailThreshold  = 5;
let Failures = Syslog
    | where TimeGenerated > ago(LookbackWindow)
    | where ProcessName == "sshd"
    | where SyslogMessage has "Failed password"
    | parse kind=relaxed SyslogMessage with * "from " SrcIP " port " * " " *
    | summarize FailCount=count() by SrcIP, Computer
    | where FailCount >= FailThreshold;
let Successes = Syslog
    | where TimeGenerated > ago(LookbackWindow)
    | where ProcessName == "sshd"
    | where SyslogMessage has "Accepted"
    | parse kind=relaxed SyslogMessage with
        "Accepted " AuthMethod " for " SuccessUser " from " SrcIP " port " * " " *
    | project SuccessTime=TimeGenerated, SuccessUser, SrcIP, Computer, AuthMethod;
Successes
| join kind=inner (Failures) on SrcIP, Computer
| project SuccessTime, SuccessUser, SrcIP, Computer, AuthMethod, FailCount
```

### Sudo to Root Escalation

```kql
Syslog
| where TimeGenerated > ago(1d)
| where ProcessName == "sudo"
| where SyslogMessage has "COMMAND" and SyslogMessage has "USER=root"
| parse SyslogMessage with
    CallerUser " : TTY=" TTY
    " ; PWD=" WorkDir
    " ; USER=" RunAsUser
    " ; COMMAND=" SudoCommand
| where RunAsUser == "root"
| where SudoCommand has_any ("/bin/bash", "/bin/sh", "/usr/bin/python", "/usr/bin/perl",
                              "/bin/su", "chmod 4755", "chown root")
| project TimeGenerated, Computer, CallerUser, SudoCommand, WorkDir
```

### Cron Job Created by Non-Root User

```kql
Syslog
| where TimeGenerated > ago(7d)
| where Facility == "cron"
| where SyslogMessage has "BEGIN EDIT" or SyslogMessage has "END EDIT"
| parse SyslogMessage with "(" CronUser ") " EventType " (" _TargetUser ")"
| where CronUser !in ("root", "daemon", "cron")
| project TimeGenerated, Computer, CronUser, EventType
```

### Suspicious Cron Job Execution (Hidden Paths)

```kql
Syslog
| where TimeGenerated > ago(1d)
| where Facility == "cron"
| where SyslogMessage has "CMD"
| parse SyslogMessage with "(" CronUser ") CMD (" CronCommand ")"
| where CronCommand has_any ("/tmp/", "/var/tmp/", "/.hidden", "/dev/shm/",
                              "bash -i", "nc -", "ncat ", "curl ", "wget ",
                              "python -c", "perl -e", "ruby -e")
| project TimeGenerated, Computer, CronUser, CronCommand
```

### Failed su Attempts

```kql
Syslog
| where TimeGenerated > ago(1d)
| where SyslogMessage has "FAILED su"
| parse kind=relaxed SyslogMessage with "FAILED su for " TargetUser " by " CallerUser
| summarize
    FailCount = count(),
    Computers = make_set(Computer)
  by CallerUser, TargetUser, bin(TimeGenerated, 1h)
| where FailCount >= 3
```

### Root Login via SSH (High Severity)

```kql
Syslog
| where TimeGenerated > ago(1d)
| where ProcessName == "sshd"
| where SyslogMessage has "Accepted" and SyslogMessage has " root "
| parse kind=relaxed SyslogMessage with
    "Accepted " AuthMethod " for root from " SrcIP " port " SrcPort " " *
| project TimeGenerated, Computer, SrcIP, SrcPort, AuthMethod
```
