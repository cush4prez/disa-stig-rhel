# Ansible Automation Platform (AAP) 2.7 Complete Guide

Complete guide for deploying RHEL DISA STIG hardening with AAP 2.7.

## Table of Contents

- [Overview](#overview)
- [Initial Setup](#initial-setup)
- [Creating Projects](#creating-projects)
- [Setting Up Job Templates](#setting-up-job-templates)
- [Using Surveys](#using-surveys)
- [Running Jobs](#running-jobs)
- [Monitoring and Results](#monitoring-and-results)
- [Workflows](#workflows)
- [Best Practices](#best-practices)

---

## Overview

This project is fully compatible with AAP 2.7 and provides:

- **Survey-based configuration** for easy GUI-driven deployment
- **Selective STIG auditing** - choose specific rules or all rules
- **Automatic backups** stored on AAP controller for disaster recovery
- **Intelligent rollback** on operational failures
- **Multi-RHEL support** - RHEL 8, 9, and 10

---

## Initial Setup

### Prerequisites

- AAP 2.7 installed and configured
- Git repository containing this project
- Execution environment with required collections:
  - `ansible.posix`
  - `community.general`

### Verify Execution Environment

```bash
# Check your execution environment includes required collections
ansible-galaxy collection list
```

If missing, add to your execution environment:

```yaml
# execution-environment.yml
dependencies:
  galaxy: requirements.yml
```

```yaml
# requirements.yml
collections:
  - name: ansible.posix
  - name: community.general
```

---

## Creating Projects

### Step 1: Create SCM Credential (if needed)

If your repository requires authentication:

1. **Resources → Credentials → Add**
2. **Credential Type**: Source Control
3. **Username**: Your Git username
4. **Password/Token**: Your Git password or token
5. **Save**

### Step 2: Create Project

1. **Resources → Projects → Add**
2. **Name**: `RHEL DISA STIG`
3. **Organization**: Your organization
4. **Execution Environment**: Select environment with required collections
5. **Source Control Type**: Git
6. **Source Control URL**: `https://github.com/yourorg/rhel8-disa-stig.git`
7. **Source Control Credential**: (if needed)
8. **Update Options**:
   - ✅ Clean
   - ✅ Delete on Update
   - ✅ Update Revision on Launch
9. **Save**
10. **Sync** the project

---

## Setting Up Job Templates

### Job Template 1: STIG Hardening with Survey (Recommended)

This is the primary job template for production use.

#### Create Template

1. **Resources → Templates → Add → Job Template**
2. **Name**: `DISA STIG - Hardening`
3. **Job Type**: Run
4. **Inventory**: Select your RHEL inventory
5. **Project**: `RHEL DISA STIG`
6. **Playbook**: `playbooks/rhel_stig_with_rollback.yml`
7. **Credentials**: Machine credential with sudo access
8. **Variables**:
   ```yaml
   # Optional: Set defaults (survey will override)
   rhel_stig_with_rollback_controller_backup_dir: /var/lib/awx/projects/stig_backups
   rhel_stig_with_rollback_fetch_to_controller: true
   ```
9. **Options**:
   - ✅ Privilege Escalation
   - ✅ Enable Fact Storage (optional)
10. **Save**

#### Add Survey

1. **Click Survey tab**
2. **Add** or **Import**
3. **Import** from `docs/aap_survey_configuration.json`

Or manually add questions:

**Question 1: STIG Audit Mode**
- Variable: `stig_audit_mode`
- Question: "STIG Audit Mode"
- Answer Type: Multiple Choice
- Choices: `full`, `selective`
- Default: `full`
- Required: Yes

**Question 2: STIG Rules**
- Variable: `stig_rules_input`
- Question: "STIG Rules to Audit (comma-separated)"
- Answer Type: Textarea
- Default: (blank)
- Required: No

**Question 3: Apply Remediations**
- Variable: `rhel_stig_with_rollback_apply_remediations`
- Question: "Apply Remediations?"
- Answer Type: Multiple Choice
- Choices: `true`, `false`
- Default: `true`
- Required: Yes

**Question 4: Auto Rollback**
- Variable: `rhel_stig_with_rollback_auto_rollback_on_failure`
- Question: "Auto Rollback on Failure?"
- Answer Type: Multiple Choice
- Choices: `true`, `false`
- Default: `true`
- Required: Yes

4. **Enable Survey**
5. **Save**

### Job Template 2: Audit Only

Quick compliance check without remediation.

1. **Resources → Templates → Add → Job Template**
2. **Name**: `DISA STIG - Audit Only`
3. **Project**: `RHEL DISA STIG`
4. **Playbook**: `playbooks/rhel_stig_audit_only.yml`
5. **Credentials**: Machine credential
6. **Options**: ✅ Privilege Escalation
7. **Save**

### Job Template 3: Rollback

Restore from backup after failed hardening.

1. **Resources → Templates → Add → Job Template**
2. **Name**: `DISA STIG - Rollback`
3. **Project**: `RHEL DISA STIG`
4. **Playbook**: `playbooks/perform_rollback.yml`
5. **Credentials**: Machine credential
6. **Variables**:
   ```yaml
   # Leave blank - will prompt
   ```
7. **Options**:
   - ✅ Privilege Escalation
   - ✅ Prompt on Launch → Extra Variables
8. **Save**

### Job Template 4: Final Audit Report

Detailed compliance report with CAT I/II/III breakdown.

1. **Resources → Templates → Add → Job Template**
2. **Name**: `DISA STIG - Final Audit Report`
3. **Project**: `RHEL DISA STIG`
4. **Playbook**: `playbooks/final_audit_report.yml`
5. **Credentials**: Machine credential
6. **Options**: ✅ Privilege Escalation
7. **Save**

---

## Using Surveys

### Launching a Survey-Based Job

1. **Resources → Templates**
2. **Select** `DISA STIG - Hardening`
3. **Launch**
4. **Fill out survey**:

**Example - Full Audit:**
```
STIG Audit Mode: full
STIG Rules to Audit: (leave blank)
Apply Remediations: true
Auto Rollback on Failure: true
```

**Example - Selective Audit:**
```
STIG Audit Mode: selective
STIG Rules to Audit: sysctl_crypto_fips_enabled,audit_rules_login_events,sshd_set_idle_timeout
Apply Remediations: true
Auto Rollback on Failure: true
```

5. **Next**
6. **Launch**

### Finding STIG Rule IDs

To find valid rule IDs for selective mode:

1. Run audit-only job first
2. Check audit report: `/opt/stig_audit/baseline_*.html`
3. Or run final audit report playbook
4. Use short IDs (without `xccdf_org.ssgproject.content_rule_` prefix)

**Common Rule IDs:**

CAT I (High):
- `sysctl_crypto_fips_enabled`
- `no_empty_passwords`
- `sshd_disable_empty_passwords`

CAT II (Medium):
- `audit_rules_login_events`
- `sshd_set_idle_timeout`
- `accounts_password_minlen_login_defs`
- `file_permissions_var_log_audit`

CAT III (Low):
- `banner_etc_issue`
- `sshd_print_last_log`

---

## Running Jobs

### Standard Workflow

1. **Audit First** (optional but recommended):
   - Run `DISA STIG - Audit Only`
   - Review baseline compliance
   - Identify which rules are failing

2. **Harden**:
   - Run `DISA STIG - Hardening`
   - Fill out survey
   - Monitor job output

3. **Verify**:
   - Job automatically runs operational checks
   - Auto-rollback triggers if verification fails

4. **Review Results**:
   - Run `DISA STIG - Final Audit Report`
   - Check compliance improvement

### Emergency Recovery

If a host becomes unreachable after hardening:

1. Access via console (not SSH)
2. Run rollback manually:
   ```bash
   ansible-playbook -i inventory playbooks/perform_rollback.yml \
     -e rhel_stig_with_rollback_backup_name=pre_stig_hostname_20261102T120000
   ```

Or restore from controller backup:

```bash
ansible-playbook -i inventory playbooks/emergency_restore_from_controller.yml \
  -e target_host=hostname \
  -e backup_name=pre_stig_hostname_20261102T120000
```

---

## Monitoring and Results

### Job Output

Monitor these phases during execution:

1. **Phase 1: Validation** - RHEL version check, SCAP content verification
2. **Phase 2: Backup** - Pre-hardening snapshot creation
3. **Phase 3: Baseline Audit** - Compliance scan (selective or full)
4. **Phase 4: Remediation** - Apply fixes (only failed rules if selective)
5. **Phase 5: Verification** - Operational checks, SSH connectivity
6. **Phase 6: Summary** - Final compliance score, rollback instructions

### Artifacts

After job completion, check:

**On Target Host:**
- Audit results: `/opt/stig_audit/`
- Remediation logs: `/opt/stig_work/`
- Backups: `/opt/stig_backups/`

**On AAP Controller:**
- Backup copies: `/var/lib/awx/projects/stig_backups/{hostname}/`

### Reviewing Audit Reports

HTML reports are generated:

```bash
# Baseline audit
/opt/stig_audit/baseline_*.html

# Post-hardening audit
/opt/stig_audit/post_hardening_*.html
```

Download from host or access via console.

---

## Workflows

### Workflow 1: Complete STIG Hardening

Create a workflow template to chain multiple jobs:

1. **Resources → Templates → Add → Workflow Template**
2. **Name**: `DISA STIG - Complete Workflow`
3. **Visualizer**:
   ```
   [Audit Only] → [Hardening] → [Final Report]
                       ↓ (on failure)
                   [Rollback]
   ```

**Step 1: Audit Only**
- Job Template: `DISA STIG - Audit Only`
- Convergence: Any

**Step 2: Hardening** (on success)
- Job Template: `DISA STIG - Hardening`
- Convergence: Any

**Step 3: Final Report** (on success of hardening)
- Job Template: `DISA STIG - Final Audit Report`

**Step 4: Rollback** (on failure of hardening)
- Job Template: `DISA STIG - Rollback`
- Prompt for variables: Yes

4. **Save**

### Workflow 2: Selective Remediation

For targeted fixes:

1. Run audit to identify failures
2. Review failures by category
3. Run selective hardening for specific rules
4. Re-audit to confirm fixes

---

## Best Practices

### Pre-Hardening

- ✅ Test on non-production systems first
- ✅ Run audit-only to establish baseline
- ✅ Review which rules will fail before hardening
- ✅ Schedule hardening during maintenance windows
- ✅ Ensure console access is available

### During Hardening

- ✅ Monitor job output in real-time
- ✅ Keep console access open (in case SSH breaks)
- ✅ Have rollback procedure ready
- ✅ Use selective mode for high-risk environments

### Post-Hardening

- ✅ Verify SSH access immediately
- ✅ Test critical services
- ✅ Review compliance improvement
- ✅ Document exceptions/tailoring needed
- ✅ Keep backups for at least 30 days

### Backup Management

**On AAP Controller:**

```bash
# Check backup storage
du -sh /var/lib/awx/projects/stig_backups/

# Clean old backups (>30 days)
find /var/lib/awx/projects/stig_backups/ -name "*.tar.gz" -mtime +30 -delete
```

**On Target Hosts:**

```bash
# Clean old backups
find /opt/stig_backups/ -name "*.tar.gz" -mtime +30 -delete
```

### Selective vs Full Mode

**Use Selective Mode when:**
- Testing specific fixes
- Fixing known failures only
- High-risk production systems
- Gradual remediation approach

**Use Full Mode when:**
- Initial hardening
- Non-production environments
- Comprehensive compliance required
- Low-risk systems

---

## Troubleshooting

### Survey Not Appearing

1. Verify survey is **enabled** on job template
2. Check survey questions are saved
3. Ensure variable names match exactly (case-sensitive)

### Rules Not Found in Audit

```
⚠️  WARNING: Some requested rules were not found:
  - rule_name_xyz
```

**Solutions:**
- Check spelling (case-sensitive)
- Use short ID without `xccdf_org.ssgproject.content_rule_` prefix
- Verify rule exists in your SCAP content version

### Job Fails on Phase 4

Check remediation log:

```bash
cat /opt/stig_work/remediation_*.log
```

Common causes:
- Conflicting STIG rules
- System-specific constraints
- Service dependencies

### Host Unreachable After Hardening

**Automatic Recovery:**
- Wait for auto-rollback to trigger (if enabled)

**Manual Recovery:**
1. Access via console
2. Check `/opt/stig_backups/ROLLBACK_INSTRUCTIONS.txt`
3. Run rollback playbook from AAP or another host

### No Compliance Improvement

Possible causes:
- Remediation didn't apply (check logs)
- Rules require manual intervention
- SCAP content version mismatch

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more solutions.

---

## Advanced Configuration

### Custom Execution Environment

Create custom EE with additional tools:

```dockerfile
# execution-environment.yml
version: 1
dependencies:
  galaxy: requirements.yml
  python: requirements.txt
additional_build_steps:
  prepend: |
    RUN pip3 install --upgrade pip
    RUN dnf install -y openscap-scanner
```

### Credential Types

Create custom credential type for STIG settings:

```yaml
# Input Configuration
fields:
  - id: backup_retention_days
    type: integer
    label: Backup Retention (days)
  - id: compliance_threshold
    type: integer
    label: Min Compliance Score

# Injector Configuration
extra_vars:
  stig_backup_retention: "{{ backup_retention_days }}"
  stig_compliance_threshold: "{{ compliance_threshold }}"
```

### Notifications

Set up notifications for job results:

1. **Administration → Notifiers → Add**
2. **Type**: Email / Slack / Webhook
3. **Configure** connection details
4. **On Job Template**:
   - Success: Send final report
   - Failure: Alert on-call team
   - Rollback: Critical alert

---

## Support

For issues:
1. Check job output logs in AAP
2. Review target host logs in `/opt/stig_work/` and `/opt/stig_audit/`
3. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
4. Check AAP controller logs: `/var/log/tower/`
