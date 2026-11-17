# Playbook Reference Guide

Complete reference for all available playbooks.

## Table of Contents

- [Production Playbooks](#production-playbooks)
- [Diagnostic Playbooks](#diagnostic-playbooks)
- [Utility Playbooks](#utility-playbooks)
- [Test Playbooks](#test-playbooks)

---

## Production Playbooks

### rhel_stig_with_rollback.yml

**Purpose:** Main STIG hardening workflow with full/selective audit and rollback protection.

**Use Case:** Production deployments via AAP or CLI

**Features:**
- Survey-compatible (AAP)
- Selective or full STIG audit
- Ansible-based remediation
- Automatic backup
- Operational verification
- Auto-rollback on failure

**Usage:**

```bash
# CLI - full mode
ansible-playbook -i inventory playbooks/rhel_stig_with_rollback.yml

# CLI - selective mode
ansible-playbook -i inventory playbooks/rhel_stig_with_rollback.yml \
  -e rhel_stig_with_rollback_stig_rules_to_apply='["sysctl_crypto_fips_enabled","audit_rules_login_events"]'

# CLI - with organization tailoring
ansible-playbook -i inventory playbooks/rhel_stig_with_rollback.yml \
  -e rhel_stig_with_rollback_tailoring_profile=myorg

# CLI - tailoring + selective mode
ansible-playbook -i inventory playbooks/rhel_stig_with_rollback.yml \
  -e rhel_stig_with_rollback_tailoring_profile=myorg \
  -e rhel_stig_with_rollback_stig_rules_to_apply='["sysctl_crypto_fips_enabled"]'

# AAP - use survey
```

**Variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `rhel_stig_with_rollback_stig_rules_to_apply` | `[]` | List of rule IDs (empty = full) |
| `rhel_stig_with_rollback_tailoring_profile` | `""` | Organization tailoring profile (empty = defaults) |
| `rhel_stig_with_rollback_use_native_parsing` | `true` | Use native Ansible XML parsing (recommended) |
| `rhel_stig_with_rollback_apply_remediations` | `true` | Apply fixes |
| `rhel_stig_with_rollback_auto_rollback_on_failure` | `true` | Auto-rollback |
| `rhel_stig_with_rollback_enable_auto_backup` | `true` | Create backup |

**Phases:**
1. Load organization tailoring variables (if specified)
2. Pre-hardening validation
3. Backup creation
4. Baseline audit (selective or full)
5. Remediation (Ansible playbook with tailored variables)
6. Operational verification
7. Summary and rollback instructions

**Output:**
- Audit reports: `/opt/stig_audit/`
- Remediation logs: `/opt/stig_work/`
- Backups: `/opt/stig_backups/`

---

### rhel_stig_with_rollback_interactive.yml

**Purpose:** Interactive CLI version with prompts for configuration.

**Use Case:** Manual deployments with user-friendly prompts

**Features:**
- Interactive prompts for all settings
- Nice formatted questions
- Configuration summary before execution
- Same workflow as main playbook

**Usage:**

```bash
ansible-playbook -i inventory playbooks/rhel_stig_with_rollback_interactive.yml
```

**Prompts:**
1. Audit mode (full or selective)
2. STIG rules to audit (if selective)
3. Apply remediations (yes/no)
4. Auto rollback on failure (yes/no)

**Notes:**
- Not recommended for AAP (prompts won't work)
- Use survey-based version for AAP

---

### rhel_stig_audit_only.yml

**Purpose:** Run OSCAP audit without applying any remediations.

**Use Case:** Compliance reporting, baseline establishment

**Features:**
- No system changes
- Fast execution
- Generates HTML reports
- Returns compliance score

**Usage:**

```bash
ansible-playbook -i inventory playbooks/rhel_stig_audit_only.yml
```

**Variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `rhel_stig_with_rollback_stig_audit_dir` | `/opt/stig_audit` | Audit output directory |

**Output:**
- XML results: `/opt/stig_audit/baseline_*.xml`
- HTML report: `/opt/stig_audit/baseline_*.html`
- Compliance score printed to console

**Example Output:**
```
Current STIG compliance: 54.3%
Baseline Report: /opt/stig_audit/baseline_20261102T120000.html
```

---

### final_audit_report.yml

**Purpose:** Generate detailed compliance report with failures categorized by CAT I/II/III.

**Use Case:** Post-hardening validation, executive reporting

**Features:**
- Categorizes failures by severity
- Operational status check
- Production readiness assessment
- Actionable recommendations

**Usage:**

```bash
ansible-playbook -i inventory playbooks/final_audit_report.yml
```

**Output Format:**
```
========================================================================
FINAL COMPLIANCE AUDIT REPORT
========================================================================
Compliance Score: 95.2%
Total Checks: 250
Passed: 238
Failed: 12

FAILURES BY CATEGORY:
CAT I (High Severity): 1
  1. [audit_rules_login_events] Ensure auditd Collects Login Events

CAT II (Medium Severity): 8
  1. [sshd_set_idle_timeout] Set SSH Idle Timeout
  ...

CAT III (Low Severity): 3
  1. [banner_etc_issue] Set Login Banner
  ...

OPERATIONAL STATUS: ✅ PRODUCTION READY
========================================================================
```

**Notes:**
- Run after hardening to see improvement
- Can run standalone for current state
- Useful for compliance documentation

---

### perform_rollback.yml

**Purpose:** Restore system from pre-hardening backup.

**Use Case:** Emergency recovery, undo STIG hardening

**Features:**
- Restores configuration files
- Restores service states
- Restores firewall rules
- Restores kernel parameters

**Usage:**

```bash
# Find backup name
ls /opt/stig_backups/

# Perform rollback
ansible-playbook -i inventory playbooks/perform_rollback.yml \
  -e rhel_stig_with_rollback_backup_name=pre_stig_hostname_20261102T120000
```

**Variables:**

| Variable | Required | Description |
|----------|----------|-------------|
| `rhel_stig_with_rollback_backup_name` | Yes | Backup archive name (without .tar.gz) |
| `rhel_stig_with_rollback_backup_root` | No | Backup directory (default: /opt/stig_backups) |

**What Gets Restored:**
- `/etc/passwd`, `/etc/shadow`, `/etc/group`
- `/etc/ssh/sshd_config`
- `/etc/pam.d/`
- `/etc/sudoers`
- `/etc/audit/`
- `/etc/sysctl.conf`, `/etc/sysctl.d/`
- `/etc/selinux/`
- `/etc/firewalld/`
- Service enabled/running states

**Notes:**
- Requires backup was created during hardening
- Does not restore user data or application files
- System will reboot if needed

---

### test_tailoring.yml

**Purpose:** Test and validate organization tailoring profile loading.

**Use Case:** Verify tailoring files are correctly formatted and load properly

**Features:**
- Validates tailoring directory exists
- Loads common and version-specific variables
- Displays loaded variables
- Verifies expected values match

**Usage:**

```bash
# Test specific tailoring profile
ansible-playbook playbooks/test_tailoring.yml \
  -e rhel_stig_with_rollback_tailoring_profile=myorg

# Test with custom tailoring location
ansible-playbook playbooks/test_tailoring.yml \
  -e rhel_stig_with_rollback_tailoring_profile=production
```

**Output:**
```
========================================================================
TAILORING VARIABLES LOADED SUCCESSFULLY
========================================================================
Profile: myorg

Sample Variables:
  var_password_pam_minlen: 20
  var_accounts_tmout: 900
  var_accounts_passwords_pam_faillock_deny: 5
  sshd_idle_timeout_value: 600
========================================================================
✅ All tailoring variables loaded correctly!
```

**Notes:**
- No system changes made
- Validates YAML syntax
- Checks for common tailoring errors
- See [docs/TAILORING_GUIDE.md](TAILORING_GUIDE.md) for creating tailoring files

---

## Diagnostic Playbooks

### diagnose_stig_remediation.yml

**Purpose:** Diagnose why STIG remediation isn't working or improving compliance.

**Use Case:** Troubleshooting failed/incomplete remediation

**Features:**
- Checks OSCAP installation
- Validates SCAP content
- Reviews remediation logs
- Identifies common issues

**Usage:**

```bash
ansible-playbook -i inventory playbooks/diagnose_stig_remediation.yml
```

**Checks:**
- OSCAP packages installed
- SCAP content exists and is valid
- Remediation script was generated
- Remediation execution results
- Service status
- Audit results comparison

**Output:**
```
STIG REMEDIATION DIAGNOSTIC
========================================================================
✅ OSCAP Scanner: Installed (version 1.3.6)
✅ SCAP Content: Found at /usr/share/xml/scap/ssg/content/
⚠️  Remediation Script: Generated but has errors
❌ Compliance Improvement: 0% (54% → 54%)

ISSUES FOUND:
1. Service 'auditd' failed to restart after remediation
2. SELinux contexts not restored after file modifications

RECOMMENDATIONS:
- Check /opt/stig_work/remediation_*.log for service failures
- Run: ausearch -m avc -ts recent
========================================================================
```

---

### full_diagnostic.yml

**Purpose:** Comprehensive system diagnostic for STIG hardening environment.

**Use Case:** Complete health check, pre-deployment validation

**Features:**
- System information
- OSCAP environment check
- Backup status
- Disk space verification
- Network connectivity
- Service status

**Usage:**

```bash
ansible-playbook -i inventory playbooks/full_diagnostic.yml
```

**Checks:**
- RHEL version compatibility
- Required packages installed
- SCAP content availability
- Backup directory writable
- Sufficient disk space
- Critical services running
- Python version
- Ansible version

---

### verify_system_operational.yml

**Purpose:** Verify system is operational after hardening.

**Use Case:** Post-hardening validation, health check

**Features:**
- SSH connectivity test
- Critical services check
- Network connectivity test
- Firewall status

**Usage:**

```bash
ansible-playbook -i inventory playbooks/verify_system_operational.yml
```

**Tests:**
- SSH daemon running and reachable
- NetworkManager active
- Firewall operational
- DNS resolution
- Default gateway reachable

**Output:**
```
✅ SSH connectivity: OK
✅ NetworkManager: Running
✅ Firewall: Active
✅ Network connectivity: OK

VERDICT: SYSTEM IS OPERATIONAL
```

---

## Utility Playbooks

### rhel_stig_backup_state.yml

**Purpose:** Create backup without running audit or remediation.

**Use Case:** Pre-change snapshot, scheduled backups

**Usage:**

```bash
ansible-playbook -i inventory playbooks/rhel_stig_backup_state.yml
```

**Features:**
- Creates compressed backup
- Saves service states
- Copies to AAP controller (if configured)
- Generates rollback instructions

---

### emergency_restore_from_controller.yml

**Purpose:** Restore system from backup stored on AAP controller.

**Use Case:** Host inaccessible, backup on target lost

**Usage:**

```bash
ansible-playbook -i inventory playbooks/emergency_restore_from_controller.yml \
  -e target_host=hostname \
  -e backup_name=pre_stig_hostname_20261102T120000
```

**Variables:**

| Variable | Required | Description |
|----------|----------|-------------|
| `target_host` | Yes | Hostname to restore |
| `backup_name` | Yes | Backup archive name |
| `rhel_stig_with_rollback_controller_backup_dir` | No | Controller backup path |

**Notes:**
- Requires backup was fetched to controller
- Copies backup from controller to target
- Extracts and restores

---

### rhel_stig_query.yml

**Purpose:** Query current STIG status without making changes.

**Use Case:** Quick status check, monitoring

**Usage:**

```bash
ansible-playbook -i inventory playbooks/rhel_stig_query.yml
```

**Shows:**
- Current compliance score
- Last audit date
- Available backups
- Remediation history

---

### rhel_stig_verification.yml

**Purpose:** Verify STIG hardening was successful.

**Use Case:** Post-deployment validation

**Usage:**

```bash
ansible-playbook -i inventory playbooks/rhel_stig_verification.yml
```

**Checks:**
- Compliance score improved
- System operational
- Backups exist
- No critical failures

---

## Test Playbooks

### check_score_calculation.yml

**Purpose:** Debug compliance score calculation issues.

**Use Case:** Troubleshooting score discrepancies

**Usage:**

```bash
ansible-playbook -i inventory playbooks/check_score_calculation.yml
```

---

### debug_oscap_score.yml

**Purpose:** Detailed OSCAP score debugging.

**Use Case:** Understanding how scores are calculated

**Usage:**

```bash
ansible-playbook -i inventory playbooks/debug_oscap_score.yml
```

---

### diagnose_score_issue.yml

**Purpose:** Investigate why compliance scores don't match expectations.

**Use Case:** Troubleshooting score calculation

**Usage:**

```bash
ansible-playbook -i inventory playbooks/diagnose_score_issue.yml
```

---

### test_actual_remediation.yml

**Purpose:** Test remediation generation and application.

**Use Case:** Development, testing

**Usage:**

```bash
ansible-playbook -i inventory playbooks/test_actual_remediation.yml
```

**Notes:**
- For testing only
- May make system changes
- Use in development environment

---

## Playbook Comparison

### Which Playbook Should I Use?

| Scenario | Recommended Playbook |
|----------|---------------------|
| Initial STIG hardening | `rhel_stig_with_rollback.yml` or `rhel_stig_with_rollback_interactive.yml` |
| AAP deployment | `rhel_stig_with_rollback.yml` (with survey) |
| Organization-specific hardening | `rhel_stig_with_rollback.yml` (with tailoring profile) |
| Just check compliance | `rhel_stig_audit_only.yml` |
| Fix specific STIG rules only | `rhel_stig_with_rollback.yml` (selective mode) |
| Detailed compliance report | `final_audit_report.yml` |
| Undo hardening | `perform_rollback.yml` |
| System won't boot/login | `emergency_restore_from_controller.yml` |
| Troubleshoot remediation | `diagnose_stig_remediation.yml` |
| Pre-change backup | `rhel_stig_backup_state.yml` |
| Health check | `verify_system_operational.yml` |
| Test tailoring profile | `test_tailoring.yml` |

---

## Common Playbook Combinations

### Full Hardening Workflow

```bash
# 1. Baseline audit
ansible-playbook -i inventory playbooks/rhel_stig_audit_only.yml

# 2. Review results, then harden
ansible-playbook -i inventory playbooks/rhel_stig_with_rollback.yml

# 3. Detailed report
ansible-playbook -i inventory playbooks/final_audit_report.yml
```

### Selective Remediation Workflow

```bash
# 1. Audit to find failures
ansible-playbook -i inventory playbooks/final_audit_report.yml

# 2. Fix only specific failures
ansible-playbook -i inventory playbooks/rhel_stig_with_rollback.yml \
  -e rhel_stig_with_rollback_stig_rules_to_apply='["rule1","rule2"]'

# 3. Re-audit to confirm
ansible-playbook -i inventory playbooks/final_audit_report.yml
```

### Emergency Recovery Workflow

```bash
# 1. Diagnose issue
ansible-playbook -i inventory playbooks/diagnose_stig_remediation.yml

# 2. If recovery needed
ansible-playbook -i inventory playbooks/perform_rollback.yml \
  -e rhel_stig_with_rollback_backup_name=BACKUP_NAME

# 3. Verify system operational
ansible-playbook -i inventory playbooks/verify_system_operational.yml
```

### Organization-Specific Hardening Workflow

```bash
# 1. Create tailoring profile
mkdir -p tailoring/myorg
cp tailoring/example_tailoring.yml tailoring/myorg/common.yml
vim tailoring/myorg/common.yml  # Edit with your values

# 2. Test tailoring loads correctly
ansible-playbook playbooks/test_tailoring.yml \
  -e rhel_stig_with_rollback_tailoring_profile=myorg

# 3. Audit with tailoring (no changes)
ansible-playbook -i inventory playbooks/rhel_stig_audit_only.yml \
  -e rhel_stig_with_rollback_tailoring_profile=myorg

# 4. Apply hardening with tailoring
ansible-playbook -i inventory playbooks/rhel_stig_with_rollback.yml \
  -e rhel_stig_with_rollback_tailoring_profile=myorg

# 5. Verify compliance
ansible-playbook -i inventory playbooks/final_audit_report.yml
```

### Multi-Environment Tailoring Workflow

```bash
# Development environment
ansible-playbook -i dev_inventory playbooks/rhel_stig_with_rollback.yml \
  -e rhel_stig_with_rollback_tailoring_profile=development

# Staging environment (production-like settings)
ansible-playbook -i staging_inventory playbooks/rhel_stig_with_rollback.yml \
  -e rhel_stig_with_rollback_tailoring_profile=staging

# Production environment (strictest settings)
ansible-playbook -i prod_inventory playbooks/rhel_stig_with_rollback.yml \
  -e rhel_stig_with_rollback_tailoring_profile=production
```

---

## All Available Playbooks

| Playbook | Category | Changes System | Requires Backup |
|----------|----------|----------------|-----------------|
| `rhel_stig_with_rollback.yml` | Production | Yes | No (creates one) |
| `rhel_stig_with_rollback_interactive.yml` | Production | Yes | No (creates one) |
| `rhel_stig_audit_only.yml` | Production | No | No |
| `final_audit_report.yml` | Production | No | No |
| `perform_rollback.yml` | Production | Yes | Yes |
| `diagnose_stig_remediation.yml` | Diagnostic | No | No |
| `full_diagnostic.yml` | Diagnostic | No | No |
| `verify_system_operational.yml` | Diagnostic | No | No |
| `rhel_stig_backup_state.yml` | Utility | No | No |
| `emergency_restore_from_controller.yml` | Utility | Yes | Yes (from controller) |
| `rhel_stig_query.yml` | Utility | No | No |
| `rhel_stig_verification.yml` | Utility | No | No |
| `check_score_calculation.yml` | Test | No | No |
| `debug_oscap_score.yml` | Test | No | No |
| `diagnose_score_issue.yml` | Test | No | No |
| `test_actual_remediation.yml` | Test | Yes | No |
| `test_tailoring.yml` | Test | No | No |
| `site.yml` | Main | Yes | No (uses role) |

---

## Organization Tailoring

All production playbooks support organization-specific STIG variable customization through tailoring profiles.

### What is Tailoring?

Tailoring allows you to customize STIG security control variables to meet your organization's specific requirements:

- **Password policies** - Length, complexity, history
- **Account lockout** - Failed attempts, lockout duration
- **Session timeouts** - Shell and SSH idle timeouts
- **Audit configuration** - Log size, retention, actions
- **Cryptography** - Crypto policies, algorithms
- **Network security** - Firewall defaults, SSH hardening

### Quick Start

```bash
# 1. Create profile
mkdir -p tailoring/myorg
cp tailoring/example_tailoring.yml tailoring/myorg/common.yml

# 2. Edit variables
vim tailoring/myorg/common.yml

# 3. Use with any playbook
ansible-playbook -i inventory playbooks/rhel_stig_with_rollback.yml \
  -e rhel_stig_with_rollback_tailoring_profile=myorg
```

### Tailoring Files

```
tailoring/
├── myorg/
│   ├── common.yml          # All RHEL versions
│   ├── rhel8.yml          # RHEL 8 overrides (optional)
│   ├── rhel9.yml          # RHEL 9 overrides (optional)
│   └── rhel10.yml         # RHEL 10 overrides (optional)
```

### Variable Precedence

Variables are loaded in order (later overrides earlier):

1. Role defaults
2. Tailoring `common.yml`
3. Tailoring version-specific file
4. Group variables
5. Host variables
6. Playbook variables
7. Extra variables (`-e`)

### Common Use Cases

**Financial Services (PCI-DSS):**
```yaml
# tailoring/financial/common.yml
var_password_pam_minlen: 20
var_accounts_passwords_pam_faillock_deny: 3
var_accounts_tmout: 600
var_system_crypto_policy: "FIPS:OSPP"
```

**Healthcare (HIPAA):**
```yaml
# tailoring/healthcare/common.yml
var_password_pam_minlen: 16
var_accounts_tmout: 900
var_auditd_num_logs: 15  # 60 day retention
```

**Development Environment:**
```yaml
# tailoring/development/common.yml
var_password_pam_minlen: 12
var_accounts_passwords_pam_faillock_deny: 5
var_accounts_tmout: 1800  # Longer for debugging
```

### Playbooks with Tailoring Support

All these playbooks support the `rhel_stig_with_rollback_tailoring_profile` variable:

- `rhel_stig_with_rollback.yml` - Main hardening with tailoring
- `rhel_stig_with_rollback_interactive.yml` - Interactive with tailoring
- `rhel_stig_audit_only.yml` - Audit with tailored variables
- `final_audit_report.yml` - Report using tailored settings
- `test_tailoring.yml` - Test profile loading

### Documentation

- **[TAILORING_GUIDE.md](TAILORING_GUIDE.md)** - Complete tailoring documentation
- **[TAILORING_EXAMPLES.md](TAILORING_EXAMPLES.md)** - Real-world examples (PCI-DSS, HIPAA, DoD, etc.)
- **[tailoring/README.md](../tailoring/README.md)** - Quick reference
- **[tailoring/QUICKSTART.md](../tailoring/QUICKSTART.md)** - 5-minute getting started guide

### Testing Tailoring

```bash
# Validate profile loads correctly
ansible-playbook playbooks/test_tailoring.yml \
  -e rhel_stig_with_rollback_tailoring_profile=myorg

# Test in audit-only mode first
ansible-playbook -i inventory playbooks/rhel_stig_audit_only.yml \
  -e rhel_stig_with_rollback_tailoring_profile=myorg
```

### AAP Integration

Add tailoring profile selection to AAP survey:

```json
{
  "question_name": "Organization Tailoring Profile",
  "variable": "rhel_stig_with_rollback_tailoring_profile",
  "type": "text",
  "default": ""
}
```

See `docs/aap_survey_configuration.json` for complete example.
