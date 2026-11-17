# Role Documentation

Documentation for the `rhel_stig_with_rollback` Ansible role.

## Table of Contents

- [Overview](#overview)
- [Role Structure](#role-structure)
- [Phases](#phases)
- [Variables](#variables)
- [Using the Role](#using-the-role)

---

## Overview

The `rhel_stig_with_rollback` role automates DISA STIG hardening for RHEL 8/9/10 with:

- **Selective or Full Auditing** - Audit specific rules or all rules
- **Ansible-based Remediation** - Native Ansible tasks (not bash scripts)
- **Automatic Backup** - Pre-hardening snapshots
- **Intelligent Rollback** - Auto-rollback on operational failures
- **Multi-phase Workflow** - 6 phases from validation to summary

---

## Role Structure

```
roles/rhel_stig_with_rollback/
├── defaults/
│   └── main.yml                  # Default variables
├── handlers/
│   └── main.yml                  # Event handlers
├── tasks/
│   ├── main.yml                  # Main task orchestrator
│   ├── phase1_validation.yml     # Pre-flight checks
│   ├── phase2_backup.yml         # Backup creation
│   ├── phase3_baseline_audit.yml # Audit (selective or full)
│   ├── phase4_remediation.yml    # Apply fixes
│   ├── phase5_verification.yml   # Operational checks
│   ├── phase6_summary.yml        # Final report
│   ├── rollback.yml              # Rollback logic
│   └── verify_operational.yml    # System health checks
├── vars/
│   └── main.yml                  # Internal variables
└── README.md                     # Role README
```

---

## Phases

### Phase 1: Validation

**File:** `tasks/phase1_validation.yml`

**Purpose:** Pre-flight checks before any changes

**Tasks:**
- Verify RHEL version (8, 9, or 10)
- Check SCAP content exists
- Install missing packages (openscap-scanner, scap-security-guide)
- Validate required Ansible version

**Variables Used:**
- `rhel_stig_with_rollback_scap_ds_path`

**Exit Criteria:**
- RHEL version supported
- SCAP content available
- Required packages installed

---

### Phase 2: Backup

**File:** `tasks/phase2_backup.yml`

**Purpose:** Create pre-hardening backup for rollback capability

**Tasks:**
- Create backup directory
- Backup critical configuration files
- Save service states (enabled/running)
- Create compressed archive
- Copy to AAP controller (if enabled)
- Generate rollback instructions

**Variables Used:**
- `rhel_stig_with_rollback_enable_auto_backup`
- `rhel_stig_with_rollback_backup_root`
- `rhel_stig_with_rollback_backup_timestamp`
- `rhel_stig_with_rollback_fetch_to_controller`
- `rhel_stig_with_rollback_controller_backup_dir`

**Backed Up Files:**
- `/etc/passwd`, `/etc/shadow`, `/etc/group`
- `/etc/sudoers`
- `/etc/ssh/sshd_config`
- `/etc/pam.d/`
- `/etc/login.defs`
- `/etc/security/`
- `/etc/audit/`
- `/etc/sysctl.conf`, `/etc/sysctl.d/`
- `/etc/selinux/`
- `/etc/firewalld/`

**Output:**
- Backup archive: `${backup_root}/${backup_name}.tar.gz`
- Controller copy: `${controller_backup_dir}/${hostname}/${backup_name}.tar.gz`
- Instructions: `${backup_root}/ROLLBACK_INSTRUCTIONS.txt`

---

### Phase 3: Baseline Audit

**File:** `tasks/phase3_baseline_audit.yml`

**Purpose:** Run OSCAP audit (selective or full mode)

**Modes:**

**Full Mode** (default):
- Audits all STIG rules from profile
- `rhel_stig_with_rollback_stig_rules_to_apply: []`

**Selective Mode**:
- Audits only specified rules
- `rhel_stig_with_rollback_stig_rules_to_apply: ['rule1', 'rule2']`

**Tasks:**
- Determine audit mode (selective vs full)
- Run OSCAP evaluation
- Generate XML results and HTML report
- Parse compliance score
- (Selective mode) Filter results for selected rules
- Identify which rules failed
- Store failed rules for remediation

**Variables Used:**
- `rhel_stig_with_rollback_stig_rules_to_apply`
- `rhel_stig_with_rollback_stig_profile_id`
- `rhel_stig_with_rollback_stig_audit_dir`
- `rhel_stig_with_rollback_scap_ds_path`

**Variables Set:**
- `rhel_stig_with_rollback_selective_mode` (bool)
- `rhel_stig_with_rollback_baseline_score` (compliance %)
- `rhel_stig_with_rollback_rules_to_remediate` (list of failed rules)

**Output:**
- XML results: `/opt/stig_audit/baseline_*.xml`
- HTML report: `/opt/stig_audit/baseline_*.html`

**Selective Mode Output:**
```
SELECTIVE AUDIT RESULTS
Selected rules: 3
Rules found: 3
Pass: 2
Fail: 1

FAILED RULES (will be remediated):
  - audit_rules_login_events
```

---

### Phase 4: Remediation

**File:** `tasks/phase4_remediation.yml`

**Purpose:** Generate and apply STIG fixes using Ansible

**Modes:**

**Full Mode:**
- Remediates all failed rules
- Uses complete remediation playbook

**Selective Mode:**
- Remediates ONLY rules that failed in Phase 3 audit
- Filters remediation playbook to include only failed rules

**Tasks:**
- Generate Ansible remediation playbook (`--fix-type ansible`)
- (Selective mode) Filter playbook for failed rules only
- Execute remediation playbook
- Handle system reboots if needed
- Save execution log
- Verify system still reachable

**Variables Used:**
- `rhel_stig_with_rollback_apply_remediations`
- `rhel_stig_with_rollback_selective_mode`
- `rhel_stig_with_rollback_rules_to_remediate`
- `rhel_stig_with_rollback_stig_work_dir`

**Output:**
- Full remediation playbook: `/opt/stig_work/remediation_*.yml`
- Filtered playbook (selective): `/opt/stig_work/remediation_filtered_*.yml`
- Execution log: `/opt/stig_work/remediation_*.log`

**Important Notes:**
- Uses `--fix-type ansible` (not bash)
- Includes tasks only, no bash scripts
- Selective mode significantly reduces scope and risk

---

### Phase 5: Verification

**File:** `tasks/phase5_verification.yml`

**Purpose:** Verify system is operational after hardening

**Tasks:**
- Run operational checks (via `verify_operational.yml`)
- Test SSH connectivity
- Check critical services (sshd, NetworkManager)
- Assess production readiness
- Trigger auto-rollback if verification fails

**Variables Used:**
- `rhel_stig_with_rollback_auto_rollback_on_failure`
- `rhel_stig_with_rollback_rollback_on_critical_service_failure`
- `rhel_stig_with_rollback_critical_services`

**Variables Set:**
- `rhel_stig_with_rollback_system_is_operable` (bool)
- `rhel_stig_with_rollback_operational_failures` (list)

**Operational Checks:**
- ✅ SSH daemon running and reachable
- ✅ NetworkManager active
- ✅ Network connectivity
- ✅ DNS resolution
- ✅ Default gateway reachable

**Rollback Trigger:**
If `rhel_stig_with_rollback_system_is_operable: false` and auto-rollback enabled:
- Rollback initiated automatically
- System restored from Phase 2 backup

---

### Phase 6: Summary

**File:** `tasks/phase6_summary.yml`

**Purpose:** Display final results and rollback instructions

**Tasks:**
- Run post-hardening audit
- Calculate compliance improvement
- Display summary report
- Generate rollback instructions file

**Variables Used:**
- `rhel_stig_with_rollback_baseline_score`
- `rhel_stig_with_rollback_post_score`
- `rhel_stig_with_rollback_backup_archive`

**Output:**
```
========================================================================
            RHEL 8 DISA STIG HARDENING COMPLETE
========================================================================
Target Host            : hostname
RHEL Version           : 8.6
Baseline Compliance    : 54%
Post-Hardening Compliance : 95%
Compliance Improvement    : +41.0%
-------------------------------------------------------------------------
Backup Archive         : /opt/stig_backups/pre_stig_hostname_20261102.tar.gz
Baseline Report        : /opt/stig_audit/baseline_20261102.html
Post-Hardening Report  : /opt/stig_audit/post_hardening_20261102.html
========================================================================
```

---

## Variables

### Core Settings

| Variable | Default | Type | Description |
|----------|---------|------|-------------|
| `rhel_stig_with_rollback_apply_remediations` | `true` | bool | Apply remediations after audit |
| `rhel_stig_with_rollback_enable_auto_backup` | `true` | bool | Create pre-hardening backup |
| `rhel_stig_with_rollback_auto_rollback_on_failure` | `true` | bool | Auto-rollback on verification failure |
| `rhel_stig_with_rollback_rollback_on_critical_service_failure` | `true` | bool | Rollback if critical services fail |

### Selective STIG Settings

| Variable | Default | Type | Description |
|----------|---------|------|-------------|
| `rhel_stig_with_rollback_stig_rules_to_apply` | `[]` | list | STIG rule IDs to audit/remediate (empty = full) |

### Paths and Locations

| Variable | Default | Type | Description |
|----------|---------|------|-------------|
| `rhel_stig_with_rollback_backup_root` | `/opt/stig_backups` | string | Backup storage directory |
| `rhel_stig_with_rollback_stig_audit_dir` | `/opt/stig_audit` | string | Audit results directory |
| `rhel_stig_with_rollback_stig_work_dir` | `/opt/stig_work` | string | Working directory for scripts |
| `rhel_stig_with_rollback_controller_backup_dir` | `/var/lib/awx/projects/stig_backups` | string | AAP controller backup location |
| `rhel_stig_with_rollback_scap_ds_path` | `/usr/share/xml/scap/ssg/content/ssg-rhel{version}-ds.xml` | string | SCAP data stream path |

### SCAP Settings

| Variable | Default | Type | Description |
|----------|---------|------|-------------|
| `rhel_stig_with_rollback_stig_profile_id` | `xccdf_org.ssgproject.content_profile_stig` | string | SCAP profile identifier |

### Backup Settings

| Variable | Default | Type | Description |
|----------|---------|------|-------------|
| `rhel_stig_with_rollback_fetch_to_controller` | `true` | bool | Copy backup to AAP controller |
| `rhel_stig_with_rollback_backup_timestamp` | `{{ ansible_date_time.iso8601_basic_short }}` | string | Timestamp for backup naming |

### Critical Services

| Variable | Default | Type | Description |
|----------|---------|------|-------------|
| `rhel_stig_with_rollback_critical_services` | `['sshd', 'NetworkManager']` | list | Services that must stay running |

### Internal Variables (Set During Execution)

| Variable | Set By | Type | Description |
|----------|--------|------|-------------|
| `rhel_stig_with_rollback_selective_mode` | Phase 3 | bool | True if selective audit mode |
| `rhel_stig_with_rollback_baseline_score` | Phase 3 | string | Baseline compliance % |
| `rhel_stig_with_rollback_post_score` | Phase 6 | string | Post-hardening compliance % |
| `rhel_stig_with_rollback_rules_to_remediate` | Phase 3 | list | Failed rules to remediate |
| `rhel_stig_with_rollback_system_is_operable` | Phase 5 | bool | System operational status |
| `rhel_stig_with_rollback_backup_archive` | Phase 2 | string | Path to backup archive |

---

## Using the Role

### Basic Usage

```yaml
---
- hosts: rhel_servers
  roles:
    - rhel_stig_with_rollback
```

### Full Mode with Custom Settings

```yaml
---
- hosts: rhel_servers
  roles:
    - role: rhel_stig_with_rollback
      rhel_stig_with_rollback_apply_remediations: true
      rhel_stig_with_rollback_auto_rollback_on_failure: true
      rhel_stig_with_rollback_backup_root: /mnt/backups
```

### Selective Mode

```yaml
---
- hosts: rhel_servers
  roles:
    - role: rhel_stig_with_rollback
      rhel_stig_with_rollback_stig_rules_to_apply:
        - sysctl_crypto_fips_enabled
        - audit_rules_login_events
        - sshd_set_idle_timeout
      rhel_stig_with_rollback_apply_remediations: true
```

### Audit Only Mode

```yaml
---
- hosts: rhel_servers
  roles:
    - role: rhel_stig_with_rollback
      rhel_stig_with_rollback_apply_remediations: false
```

### Disable Auto-Rollback

```yaml
---
- hosts: rhel_servers
  roles:
    - role: rhel_stig_with_rollback
      rhel_stig_with_rollback_auto_rollback_on_failure: false
```

---

## Tags

The role supports tags for selective execution:

| Tag | Phases Included |
|-----|----------------|
| `validation` | Phase 1 only |
| `backup` | Phase 2 only |
| `audit`, `baseline` | Phase 3 only |
| `remediation` | Phase 4 only |
| `verification`, `operational-check` | Phase 5 only |
| `summary`, `report` | Phase 6 only |

**Examples:**

```bash
# Run only audit
ansible-playbook playbook.yml --tags audit

# Run audit and remediation only
ansible-playbook playbook.yml --tags audit,remediation

# Skip backup
ansible-playbook playbook.yml --skip-tags backup
```

---

## Dependencies

### Ansible Collections

- `ansible.posix`
- `community.general`

### System Packages (Auto-installed)

- `openscap-scanner`
- `scap-security-guide`

### Python Requirements

- Python 3.6+
- Standard library only (no additional packages)

---

## Platform Support

| Platform | Supported | Notes |
|----------|-----------|-------|
| RHEL 8.x | ✅ Yes | Fully tested |
| RHEL 9.x | ✅ Yes | Fully tested |
| RHEL 10.x | ✅ Yes | Supported |
| CentOS Stream | ⚠️  Partial | May work but untested |
| Rocky Linux | ⚠️  Partial | May work but untested |
| AlmaLinux | ⚠️  Partial | May work but untested |

---

## Role Development

### Adding New Phases

1. Create new task file in `tasks/`
2. Add include in `tasks/main.yml`
3. Update this documentation
4. Add appropriate tags

### Modifying Variables

1. Update `defaults/main.yml` for defaults
2. Document in this file
3. Update survey configuration if AAP-facing
4. Test both full and selective modes

### Testing

```bash
# Molecule testing
molecule test

# Manual testing
ansible-playbook tests/test_role.yml
```

---

## See Also

- [Playbook Reference](PLAYBOOK_REFERENCE.md) - All available playbooks
- [Survey Configuration](SURVEY_CONFIGURATION.md) - AAP survey and selective STIG
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues and solutions
- [AAP Complete Guide](AAP_COMPLETE_GUIDE.md) - AAP 2.7 deployment
