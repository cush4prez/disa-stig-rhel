# STIG Playbook Survey Configuration Guide

This guide explains how to configure and use the interactive survey feature for selective STIG auditing and remediation.

## Table of Contents
- [Overview](#overview)
- [Ansible Automation Platform Configuration](#ansible-automation-platform-configuration)
- [CLI Interactive Mode](#cli-interactive-mode)
- [Survey Variables](#survey-variables)
- [Usage Examples](#usage-examples)

---

## Overview

The STIG workflow now supports **selective auditing and remediation** where users can:

1. Choose between **full** or **selective** STIG audit mode
2. Specify which STIG rules to audit (in selective mode)
3. See which selected rules pass/fail
4. Remediate ONLY the failed rules (not all rules)
5. Control remediation and rollback behavior

This is exposed through:
- **Ansible Automation Platform (AAP) Survey**: GUI-based survey before job launch
- **CLI Interactive Mode**: Terminal prompts when running playbook manually

---

## Ansible Automation Platform Configuration

**IMPORTANT**: AAP 2.7 does NOT support importing JSON survey files. You must create the survey manually through the GUI.

The file `docs/aap_survey_configuration.json` is provided as a **reference only** showing the survey structure.

### Step 1: Create Survey Manually

1. In AAP, navigate to your Job Template
2. Click **Survey** tab
3. Click **Add**
4. Create each survey question as shown below:

**Survey Questions to Create:**

#### Question 1: STIG Audit Mode
- **Variable Name**: `stig_audit_mode`
- **Question**: STIG Audit Mode
- **Description**: Select whether to audit ALL STIG rules or only specific rules
- **Answer Type**: Multiple Choice (single select)
- **Choices**:
  ```
  full
  selective
  ```
- **Default**: `full`
- **Required**: Yes

#### Question 2: STIG Rules to Audit
- **Variable Name**: `stig_rules_input`
- **Question**: STIG Rules to Audit
- **Description**: Enter comma-separated list of STIG rule IDs (e.g., sysctl_crypto_fips_enabled,audit_rules_login_events). Only used if 'selective' mode is chosen. Leave blank for full audit.
- **Answer Type**: Textarea
- **Default**: (blank)
- **Required**: No

#### Question 3: Apply Remediations
- **Variable Name**: `rhel_stig_with_rollback_apply_remediations`
- **Question**: Apply Remediations
- **Description**: Should remediations be applied automatically?
- **Answer Type**: Multiple Choice (single select)
- **Choices**:
  ```
  true
  false
  ```
- **Default**: `true`
- **Required**: Yes

#### Question 4: Auto Rollback on Failure
- **Variable Name**: `rhel_stig_with_rollback_auto_rollback_on_failure`
- **Question**: Auto Rollback on Failure
- **Description**: Automatically rollback changes if operational verification fails?
- **Answer Type**: Multiple Choice (single select)
- **Choices**:
  ```
  true
  false
  ```
- **Default**: `true`
- **Required**: Yes

### Step 2: Configure the Job Template

- **Playbook**: `playbooks/rhel_stig_with_rollback.yml`
- **Survey Enabled**: ✅ Yes
- **Prompt on Launch**: 
  - Extra Variables: ✅ Yes (optional, allows overrides)

### Step 3: Launch the Job

When you launch the job, you'll see the survey form. Fill it out:

**Example - Selective Mode:**
```
STIG Audit Mode: selective
STIG Rules to Audit: sysctl_crypto_fips_enabled,audit_rules_login_events,sshd_set_idle_timeout
Apply Remediations: true
Auto Rollback on Failure: true
```

**Example - Full Mode:**
```
STIG Audit Mode: full
STIG Rules to Audit: (leave blank)
Apply Remediations: true
Auto Rollback on Failure: true
```

---

## CLI Interactive Mode

For direct command-line execution (not AAP), use the interactive playbook:

### Run Interactive Playbook

```bash
ansible-playbook -i inventory playbooks/rhel_stig_with_rollback_interactive.yml
```

You'll be prompted with a series of questions:

```
╔════════════════════════════════════════════════════════════════════════╗
║                      STIG AUDIT MODE SELECTION                         ║
╚════════════════════════════════════════════════════════════════════════╝

Select STIG audit mode:

  [1] full      - Audit ALL STIG rules from the profile (default)
  [2] selective - Audit only specific STIG rules you specify

Enter your choice (1 or 2):
```

After answering all questions, you'll see a configuration summary:

```
╔════════════════════════════════════════════════════════════════════════╗
║                    CONFIGURATION SUMMARY                               ║
╚════════════════════════════════════════════════════════════════════════╝

Audit Mode          : SELECTIVE
Selected Rules      : 3 rules
Apply Remediations  : True
Auto Rollback       : True

Rules to audit:
  - sysctl_crypto_fips_enabled
  - audit_rules_login_events
  - sshd_set_idle_timeout

╚════════════════════════════════════════════════════════════════════════╝

Press ENTER to continue with this configuration, or Ctrl+C then 'A' to abort:
```

---

## Survey Variables

### Role Variables (Set by Survey)

| Variable | Default | Description |
|----------|---------|-------------|
| `rhel_stig_with_rollback_stig_rules_to_apply` | `[]` | List of STIG rule IDs to audit/remediate. Empty list = full mode. |
| `rhel_stig_with_rollback_apply_remediations` | `true` | Whether to apply remediations after audit. |
| `rhel_stig_with_rollback_auto_rollback_on_failure` | `true` | Auto-rollback if operational verification fails. |

### Survey Input Variables (AAP)

| Variable | Type | Description |
|----------|------|-------------|
| `stig_audit_mode` | Choice | `full` or `selective` |
| `stig_rules_input` | Textarea | Comma-separated STIG rule IDs (only for selective mode) |

### Variable Processing Logic

The playbook converts survey inputs to role variables:

```yaml
# If user selected "selective" mode:
rhel_stig_with_rollback_stig_rules_to_apply: 
  - sysctl_crypto_fips_enabled
  - audit_rules_login_events
  - sshd_set_idle_timeout

# If user selected "full" mode or left rules blank:
rhel_stig_with_rollback_stig_rules_to_apply: []
```

---

## Usage Examples

### Example 1: Audit Only (No Remediation)

**Survey Input:**
```
STIG Audit Mode: full
STIG Rules to Audit: (blank)
Apply Remediations: false
Auto Rollback on Failure: true
```

**Result:** Runs full STIG audit, reports compliance score, does NOT apply remediations.

---

### Example 2: Selective Audit and Remediation

**Survey Input:**
```
STIG Audit Mode: selective
STIG Rules to Audit: sysctl_crypto_fips_enabled,audit_rules_login_events
Apply Remediations: true
Auto Rollback on Failure: true
```

**Workflow:**
1. Audits only the 2 specified rules
2. Reports which of those 2 rules pass/fail
3. If any fail, generates Ansible remediation for ONLY the failed rules
4. Applies the remediation
5. Runs operational verification
6. Auto-rolls back if verification fails

**Sample Output:**
```
=========================================================================
SELECTIVE AUDIT RESULTS
=========================================================================
Selected rules: 2
Rules found in audit: 2
Rules not found: 0

RESULTS BREAKDOWN:
  Pass: 1
  Fail: 1
  Not Applicable: 0
  Not Checked: 0

FAILED RULES (will be remediated):
  - audit_rules_login_events

=========================================================================
```

---

### Example 3: Full Audit with Manual Remediation Control

**Survey Input:**
```
STIG Audit Mode: full
STIG Rules to Audit: (blank)
Apply Remediations: true
Auto Rollback on Failure: false
```

**Result:** 
- Full STIG audit
- Remediates all failed rules
- Does NOT auto-rollback (manual rollback required if needed)

---

### Example 4: Finding Available Rule IDs

To find valid STIG rule IDs for selective mode:

#### Method 1: Run a full audit first
```bash
ansible-playbook -i inventory playbooks/rhel_stig_with_rollback.yml \
  -e rhel_stig_with_rollback_apply_remediations=false
```

Then check the audit report:
```bash
# View the HTML report
cat /opt/stig_audit/baseline_*.html

# Or query the XML
oscap info /usr/share/xml/scap/ssg/content/ssg-rhel8-ds.xml
```

#### Method 2: Query SCAP content directly
```bash
oscap info /usr/share/xml/scap/ssg/content/ssg-rhel8-ds.xml | grep -i "rule.*crypto"
```

#### Method 3: Use the final audit report playbook
```bash
ansible-playbook -i inventory playbooks/final_audit_report.yml
```

This shows failures categorized by CAT I/II/III with shortened rule IDs.

---

## Common STIG Rule IDs

Here are some commonly audited STIG rules:

### CAT I (High Severity)
- `sysctl_crypto_fips_enabled` - FIPS 140-2 mode
- `no_empty_passwords` - No empty passwords
- `sshd_disable_empty_passwords` - SSH deny empty passwords

### CAT II (Medium Severity)
- `audit_rules_login_events` - Audit login events
- `sshd_set_idle_timeout` - SSH idle timeout
- `accounts_password_minlen_login_defs` - Password minimum length
- `accounts_minimum_age_login_defs` - Password minimum age
- `file_permissions_var_log_audit` - Audit log permissions

### CAT III (Low Severity)
- `banner_etc_issue` - Login banner configuration
- `sshd_print_last_log` - SSH print last login

---

## Troubleshooting

### Survey Not Appearing in Ansible Automation Platform

1. Verify survey is enabled on the Job Template
2. Check that survey questions are properly saved
3. Ensure variable names match exactly (case-sensitive)

### Rules Not Found in Audit

Error message:
```
⚠️  WARNING: Some requested rules were not found:
  - rule_name_xyz
```

**Solutions:**
1. Check spelling of rule IDs (case-sensitive)
2. Verify rule exists in your SCAP content version
3. Rule ID should NOT include the `xccdf_org.ssgproject.content_rule_` prefix
   - ✅ Correct: `sysctl_crypto_fips_enabled`
   - ❌ Wrong: `xccdf_org.ssgproject.content_rule_sysctl_crypto_fips_enabled`

### No Remediations Applied (Selective Mode)

If all selected rules passed:
```
✅ No remediation needed - all selected rules passed!
```

This is normal! Remediation only applies to **failed** rules.

### Remediation Format

The workflow uses `--fix-type ansible` (NOT bash) for remediation. This generates an Ansible playbook that is filtered and executed as native Ansible tasks.

---

## Advanced Configuration

### Override Variables at Runtime

You can override survey selections with extra vars:

```bash
# Ansible Automation Platform: Add to Extra Variables field
rhel_stig_with_rollback_stig_rules_to_apply:
  - custom_rule_1
  - custom_rule_2
```

### Pre-populate Survey Defaults

Modify `roles/rhel_stig_with_rollback/defaults/main.yml`:

```yaml
# Set default selective rules (empty = full mode)
rhel_stig_with_rollback_stig_rules_to_apply:
  - sysctl_crypto_fips_enabled
  - audit_rules_login_events
```

### Use with Tailoring Files

The survey works with XCCDF tailoring files:

```yaml
# In survey extra vars or role vars:
rhel_stig_with_rollback_scap_tailoring_file: /path/to/tailoring.xml
```

---

## Files Reference

| File | Purpose |
|------|---------|
| `docs/aap_survey_configuration.json` | AAP 2.7 survey JSON import |
| `playbooks/rhel_stig_with_rollback.yml` | Main playbook (AAP compatible) |
| `playbooks/rhel_stig_with_rollback_interactive.yml` | CLI interactive version |
| `roles/rhel_stig_with_rollback/defaults/main.yml` | Default variables |
| `roles/rhel_stig_with_rollback/tasks/phase3_baseline_audit.yml` | Selective audit logic |
| `roles/rhel_stig_with_rollback/tasks/phase4_remediation.yml` | Selective remediation logic |
| `files/filter_audit_results.py` | Filters audit XML for selected rules |
| `files/filter_remediation_playbook.py` | Filters remediation playbook for selected rules |

---

## Support

For issues or questions:
1. Check the audit logs: `/opt/stig_audit/baseline_*.xml`
2. Check remediation logs: `/opt/stig_work/remediation_*.log`
3. Review playbook output for error messages
