# STIG Tailoring Guide

This guide explains how to customize DISA STIG security control variables for your organization using tailoring files.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [How Tailoring Works](#how-tailoring-works)
- [Creating Tailoring Files](#creating-tailoring-files)
- [Using Tailoring Files](#using-tailoring-files)
- [Common Variables](#common-variables)
- [Best Practices](#best-practices)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Overview

STIG tailoring allows organizations to:

- **Customize Security Controls**: Set organization-specific values for STIG variables
- **Maintain Consistency**: Ensure the same security policies across all systems
- **Version Control**: Track security policy changes in git
- **Compliance Mapping**: Document how settings meet organizational requirements
- **Environment-Specific Settings**: Different settings for dev/test/prod

### What Can Be Tailored?

- Password complexity requirements
- Account lockout policies
- Session timeout values
- Audit logging configuration
- SSH hardening settings
- Cryptographic policies
- File permission defaults
- Network security settings

## Quick Start

### 1. Create Your Organization's Tailoring Profile

```bash
# Create organization directory
mkdir -p tailoring/myorg

# Copy example template
cp tailoring/example_tailoring.yml tailoring/myorg/common.yml

# Edit with your organization's values
vim tailoring/myorg/common.yml
```

### 2. Configure Your Variables

Edit `tailoring/myorg/common.yml`:

```yaml
---
# Organization: My Company
# Created: 2026-11-03

# Password policies
var_password_pam_minlen: 15
var_accounts_passwords_pam_faillock_deny: 3
var_accounts_tmout: 600
```

### 3. Use the Tailoring Profile

**CLI:**
```bash
ansible-playbook -i inventory playbooks/rhel_stig_with_rollback.yml \
  -e rhel_stig_with_rollback_tailoring_profile=myorg
```

**AAP Survey:**
Add to your survey configuration:
```json
{
  "question_name": "Tailoring Profile",
  "variable": "rhel_stig_with_rollback_tailoring_profile",
  "type": "text",
  "default": "myorg"
}
```

**Group Variables:**
```yaml
# group_vars/production.yml
rhel_stig_with_rollback_tailoring_profile: "myorg"
```

## How Tailoring Works

### Directory Structure

```
tailoring/
├── README.md                  # Documentation
├── example_tailoring.yml      # Template
└── myorg/                     # Your organization
    ├── common.yml             # All RHEL versions
    ├── rhel8.yml             # RHEL 8 specific (optional)
    ├── rhel9.yml             # RHEL 9 specific (optional)
    └── rhel10.yml            # RHEL 10 specific (optional)
```

### Variable Loading Order

Variables are loaded and merged in this order (later overrides earlier):

1. STIG role defaults (`roles/rhel_stig_with_rollback/defaults/main.yml`)
2. Tailoring common file (`tailoring/<profile>/common.yml`)
3. Tailoring version-specific file (`tailoring/<profile>/rhel{{ version }}.yml`)
4. Group variables (`group_vars/`)
5. Host variables (`host_vars/`)
6. Playbook variables
7. Extra variables (`-e`)

This allows you to:
- Set organization-wide defaults in `common.yml`
- Override for specific RHEL versions in `rhel9.yml`
- Override for specific environments in `group_vars/production.yml`
- Override for specific hosts in `host_vars/webserver01.yml`

### Execution Flow

```
┌─────────────────────────────────────┐
│ 1. Load Role Defaults               │
└────────────────┬────────────────────┘
                 │
┌────────────────▼────────────────────┐
│ 2. Check for Tailoring Profile     │
│    (rhel_stig_with_rollback_        │
│     tailoring_profile)              │
└────────────────┬────────────────────┘
                 │
┌────────────────▼────────────────────┐
│ 3. Load common.yml (if exists)      │
└────────────────┬────────────────────┘
                 │
┌────────────────▼────────────────────┐
│ 4. Load rhel{version}.yml           │
│    (if exists, merges with common)  │
└────────────────┬────────────────────┘
                 │
┌────────────────▼────────────────────┐
│ 5. Merge with group/host/extra vars │
└────────────────┬────────────────────┘
                 │
┌────────────────▼────────────────────┐
│ 6. Variables applied to STIG        │
│    remediation                      │
└─────────────────────────────────────┘
```

## Creating Tailoring Files

### Step 1: Identify Required Variables

Find which STIG variables apply to your RHEL version:

```bash
# Generate full remediation script to see all variables
oscap xccdf generate fix \
  --profile stig \
  --fix-type ansible \
  --output /tmp/remediation.sh \
  /usr/share/xml/scap/ssg/content/ssg-rhel9-ds.xml

# Extract variable names
grep -E "^(var_|sshd_|firewalld_|sysctl_)" /tmp/remediation.sh | sort -u
```

### Step 2: Create Common Variables File

Create `tailoring/myorg/common.yml`:

```yaml
---
# Organization: My Company
# Created: 2026-11-03
# Approved By: CISO
# Review Date: 2027-02-03

# PASSWORD POLICIES
var_password_pam_minlen: 16              # Increased from default 15
var_password_pam_dcredit: -2             # Require 2 digits
var_password_pam_ucredit: -2             # Require 2 uppercase
var_password_pam_lcredit: -2             # Require 2 lowercase
var_password_pam_ocredit: -2             # Require 2 special chars

# ACCOUNT LOCKOUT
var_accounts_passwords_pam_faillock_deny: 3
var_accounts_passwords_pam_faillock_unlock_time: 1800  # 30 minutes

# SESSION MANAGEMENT
var_accounts_tmout: 900                  # 15 minutes
sshd_idle_timeout_value: 600             # 10 minutes

# AUDIT
var_auditd_space_left: 30                # Alert at 30% remaining
var_auditd_max_log_file: 250             # 250 MB per log
var_auditd_num_logs: 20                  # Keep 20 rotated logs
```

### Step 3: Create Version-Specific Overrides (Optional)

Create `tailoring/myorg/rhel9.yml` for RHEL 9 specific settings:

```yaml
---
# RHEL 9 specific overrides

# RHEL 9 supports longer passwords efficiently
var_password_pam_minlen: 18

# RHEL 9 specific crypto policy
var_system_crypto_policy: "FIPS:OSPP"
```

### Step 4: Document Your Choices

Add comments explaining organizational requirements:

```yaml
---
# Organization: Financial Services Corp
# Purpose: PCI-DSS and SOX compliance
# Reference: Security Policy SEC-2026-001

# Password length set to 16 per PCI-DSS requirement 8.2.3
var_password_pam_minlen: 16

# Account lockout per PCI-DSS requirement 8.1.6
var_accounts_passwords_pam_faillock_deny: 3
var_accounts_passwords_pam_faillock_unlock_time: 1800

# Session timeout per SOX control IT-ACC-05
var_accounts_tmout: 900
```

## Using Tailoring Files

### Method 1: Command Line (Extra Variables)

```bash
# Specify tailoring profile
ansible-playbook -i inventory playbooks/rhel_stig_with_rollback.yml \
  -e rhel_stig_with_rollback_tailoring_profile=myorg

# With other options
ansible-playbook -i inventory playbooks/rhel_stig_with_rollback.yml \
  -e rhel_stig_with_rollback_tailoring_profile=myorg \
  -e rhel_stig_with_rollback_stig_rules_to_apply='["sysctl_crypto_fips_enabled"]'
```

### Method 2: Group Variables

Set for all hosts in a group:

```yaml
# group_vars/production.yml
rhel_stig_with_rollback_tailoring_profile: "production_profile"

# group_vars/development.yml
rhel_stig_with_rollback_tailoring_profile: "dev_profile"
```

### Method 3: Playbook Variables

```yaml
---
- hosts: web_servers
  vars:
    rhel_stig_with_rollback_tailoring_profile: "webservers"
  roles:
    - rhel_stig_with_rollback
```

### Method 4: AAP Survey

Add to `docs/aap_survey_configuration.json`:

```json
{
  "question_name": "Organization Tailoring Profile",
  "question_description": "Specify organization security profile (leave empty for defaults)",
  "required": false,
  "type": "text",
  "variable": "rhel_stig_with_rollback_tailoring_profile",
  "min": 0,
  "max": 1024,
  "default": "",
  "choices": "",
  "new_question": true
}
```

## Common Variables

### Password Complexity

| Variable | Default | Description |
|----------|---------|-------------|
| `var_password_pam_minlen` | 15 | Minimum password length |
| `var_password_pam_dcredit` | -1 | Required digit characters |
| `var_password_pam_ucredit` | -1 | Required uppercase characters |
| `var_password_pam_lcredit` | -1 | Required lowercase characters |
| `var_password_pam_ocredit` | -1 | Required special characters |
| `var_password_pam_difok` | 8 | Characters different from previous |
| `var_password_pam_maxrepeat` | 3 | Max consecutive repeated characters |
| `var_password_pam_minclass` | 4 | Min character classes required |
| `var_password_pam_unix_remember` | 5 | Previous passwords remembered |

### Account Lockout

| Variable | Default | Description |
|----------|---------|-------------|
| `var_accounts_passwords_pam_faillock_deny` | 3 | Failed attempts before lockout |
| `var_accounts_passwords_pam_faillock_unlock_time` | 900 | Lockout duration (seconds) |
| `var_accounts_passwords_pam_faillock_fail_interval` | 900 | Failed attempt window (seconds) |

### Session Management

| Variable | Default | Description |
|----------|---------|-------------|
| `var_accounts_tmout` | 600 | Shell timeout (seconds) |
| `sshd_idle_timeout_value` | 300 | SSH idle timeout (seconds) |
| `var_sshd_set_keepalive` | 0 | SSH keepalive count |

### Audit Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `var_auditd_space_left` | 25 | Disk space alert (percent) |
| `var_auditd_space_left_action` | email | Action on low space |
| `var_auditd_admin_space_left` | 10 | Admin alert (percent) |
| `var_auditd_max_log_file` | 100 | Max log size (MB) |
| `var_auditd_max_log_file_action` | rotate | Action on full log |
| `var_auditd_num_logs` | 10 | Rotated logs to keep |

## Best Practices

### 1. Version Control

```bash
# Initialize git in tailoring directory
cd tailoring/myorg
git init
git add .
git commit -m "Initial tailoring profile"

# Push to organizational repository
git remote add origin git@github.com:myorg/stig-tailoring.git
git push -u origin main
```

### 2. Change Management

- **Require Approval**: Security team must approve changes
- **Document Changes**: Explain why each variable is set
- **Test First**: Test in development before production
- **Peer Review**: Have another team member review

### 3. Documentation

Include in your tailoring files:

```yaml
---
# Organization: MyOrg
# Created: 2026-11-03
# Created By: security@myorg.com
# Approved By: CISO
# Approval Date: 2026-11-05
# Review Frequency: Quarterly
# Next Review: 2027-02-03
# Compliance Frameworks: PCI-DSS, SOX, NIST 800-53
# Related Policies: SEC-001, SEC-045, CRYPTO-001
```

### 4. Environment-Specific Profiles

Create different profiles for different environments:

```
tailoring/
├── production/
│   └── common.yml          # Strict security
├── staging/
│   └── common.yml          # Same as production
└── development/
    └── common.yml          # Relaxed for productivity
```

### 5. Compliance Mapping

Document compliance requirements:

```yaml
---
# PCI-DSS Requirement 8.2.3 - Passwords must contain both numeric and alphabetic characters
var_password_pam_minlen: 16
var_password_pam_dcredit: -2
var_password_pam_lcredit: -2

# SOX IT-ACC-05 - Session timeout after 15 minutes
var_accounts_tmout: 900

# NIST 800-53 IA-5 - Account lockout
var_accounts_passwords_pam_faillock_deny: 3
```

## Examples

### Example 1: Financial Institution (High Security)

```yaml
---
# tailoring/financial/common.yml
# Purpose: PCI-DSS and SOX compliance

var_password_pam_minlen: 20
var_password_pam_dcredit: -2
var_password_pam_ucredit: -2
var_password_pam_lcredit: -2
var_password_pam_ocredit: -2
var_password_pam_difok: 10

var_accounts_passwords_pam_faillock_deny: 2
var_accounts_passwords_pam_faillock_unlock_time: 1800

var_accounts_tmout: 300
sshd_idle_timeout_value: 180

var_system_crypto_policy: "FIPS:OSPP"
firewalld_default_zone: drop
```

### Example 2: Development Environment

```yaml
---
# tailoring/development/common.yml
# Purpose: Developer productivity with acceptable security

var_password_pam_minlen: 12
var_password_pam_dcredit: -1
var_password_pam_ucredit: -1
var_password_pam_lcredit: -1
var_password_pam_ocredit: -1

var_accounts_passwords_pam_faillock_deny: 5
var_accounts_passwords_pam_faillock_unlock_time: 600

var_accounts_tmout: 1800
sshd_idle_timeout_value: 600
```

### Example 3: Multi-Environment with Version Overrides

```yaml
# tailoring/enterprise/common.yml
---
var_password_pam_minlen: 15
var_accounts_tmout: 600
```

```yaml
# tailoring/enterprise/rhel8.yml
---
# RHEL 8 cannot support extended crypto policy
var_system_crypto_policy: "FIPS"
```

```yaml
# tailoring/enterprise/rhel9.yml
---
# RHEL 9 supports extended crypto policy
var_system_crypto_policy: "FIPS:OSPP"
```

## Troubleshooting

### Issue: Tailoring Profile Not Found

**Error:**
```
Tailoring profile directory not found: /path/to/tailoring/myorg
```

**Solution:**
```bash
# Create the directory
mkdir -p tailoring/myorg

# Copy example
cp tailoring/example_tailoring.yml tailoring/myorg/common.yml
```

### Issue: Variables Not Being Applied

**Debug:**
```bash
# Run with verbose output
ansible-playbook playbooks/rhel_stig_with_rollback.yml \
  -e rhel_stig_with_rollback_tailoring_profile=myorg \
  -vv
```

**Check:**
1. Verify tailoring profile name is correct
2. Check variable precedence (extra vars override tailoring)
3. Verify YAML syntax: `yamllint tailoring/myorg/common.yml`

### Issue: Some Variables Not Taking Effect

**Cause:** Variable name mismatch or STIG version incompatibility

**Debug:**
```bash
# Check what variables the STIG remediation script uses
oscap xccdf generate fix \
  --profile stig \
  --output /tmp/remediation.sh \
  /usr/share/xml/scap/ssg/content/ssg-rhel9-ds.xml

# Search for your variable
grep "var_password_pam_minlen" /tmp/remediation.sh
```

### Issue: YAML Syntax Error

**Error:**
```
We were unable to read file '/path/to/common.yml'
```

**Solution:**
```bash
# Validate YAML syntax
yamllint tailoring/myorg/common.yml

# Check for common issues:
# - Tabs instead of spaces
# - Incorrect indentation
# - Missing quotes around special characters
```

### Issue: Different Values on Different Hosts

**Cause:** Variable precedence - host_vars or extra vars override tailoring

**Debug:**
```bash
# Check variable precedence
ansible-playbook playbooks/rhel_stig_with_rollback.yml \
  -e rhel_stig_with_rollback_tailoring_profile=myorg \
  --tags tailoring \
  -vvv | grep var_password_pam_minlen
```

## Validation

### Pre-Deployment Validation

```bash
# 1. Syntax check
ansible-playbook playbooks/rhel_stig_with_rollback.yml --syntax-check \
  -e rhel_stig_with_rollback_tailoring_profile=myorg

# 2. YAML validation
yamllint tailoring/myorg/*.yml

# 3. Dry run (audit only)
ansible-playbook -i inventory playbooks/rhel_stig_with_rollback.yml \
  -e rhel_stig_with_rollback_tailoring_profile=myorg \
  -e rhel_stig_with_rollback_apply_remediations=false \
  --check

# 4. Test in development first
ansible-playbook -i dev_inventory playbooks/rhel_stig_with_rollback.yml \
  -e rhel_stig_with_rollback_tailoring_profile=myorg \
  --limit dev_server
```

### Post-Deployment Validation

```bash
# Verify compliance score
ansible-playbook -i inventory playbooks/final_audit_report.yml

# Check specific variables were applied
ansible -i inventory all -m shell \
  -a "grep -E 'PASS_MIN_LEN|TMOUT' /etc/login.defs /etc/profile"
```

## Security Considerations

1. **Access Control**: Restrict who can modify tailoring files
2. **Audit Trail**: Log all changes to tailoring profiles
3. **Review Cycle**: Review tailoring quarterly
4. **Compliance**: Ensure tailoring doesn't violate compliance
5. **Testing**: Always test in non-production first
6. **Backup**: Keep backups of previous tailoring versions
7. **Documentation**: Document all deviations from baseline

## Additional Resources

- [DISA STIG Documentation](https://public.cyber.mil/stigs/)
- [SCAP Security Guide](https://www.open-scap.org/security-policies/scap-security-guide/)
- [NIST 800-53 Controls](https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final)
- [PCI-DSS Requirements](https://www.pcisecuritystandards.org/)
- [Main Project Documentation](README.md)
