# STIG Tailoring Files

This directory contains organization-specific tailoring files for customizing DISA STIG security control variables.

## Purpose

Tailoring files allow organizations to:
- Override default STIG variable values
- Document organization-specific security requirements
- Maintain consistent security policies across multiple systems
- Version control security control customizations

## Directory Structure

```
tailoring/
├── README.md                    # This file
├── example_tailoring.yml        # Example template
└── <org_name>/                  # Your organization's tailoring files
    ├── common.yml               # Variables for all RHEL versions
    ├── rhel8.yml               # RHEL 8 specific variables
    ├── rhel9.yml               # RHEL 9 specific variables
    └── rhel10.yml              # RHEL 10 specific variables
```

## Creating a Tailoring File

### Step 1: Create Organization Directory

```bash
mkdir -p tailoring/myorg
```

### Step 2: Create Tailoring File

Create `tailoring/myorg/common.yml` with your organization's variables:

```yaml
---
# Organization: My Organization
# Created: 2026-11-03
# Purpose: Custom STIG variables for compliance with internal security policies

# STIG Control Variables
# ======================

# Password policies
var_password_pam_minlen: 15                    # Minimum password length
var_password_pam_dcredit: -2                   # Required digit characters
var_password_pam_ucredit: -2                   # Required uppercase characters
var_password_pam_lcredit: -2                   # Required lowercase characters
var_password_pam_ocredit: -2                   # Required special characters
var_password_pam_difok: 8                      # Characters different from previous password
var_password_pam_maxrepeat: 3                  # Max consecutive repeated characters
var_password_pam_minclass: 4                   # Min character classes required

# Account lockout
var_accounts_passwords_pam_faillock_deny: 3    # Max failed login attempts
var_accounts_passwords_pam_faillock_unlock_time: 900  # Account lockout duration (seconds)
var_accounts_passwords_pam_faillock_fail_interval: 900  # Failed attempt window (seconds)

# Session timeout
var_accounts_tmout: 600                        # Session timeout (seconds)

# Audit settings
var_auditd_space_left: 25                      # Percent disk space for audit alert
var_auditd_space_left_action: email            # Action when space low
var_auditd_admin_space_left: 10                # Percent for admin alert
var_auditd_max_log_file: 100                   # Max audit log file size (MB)
var_auditd_max_log_file_action: rotate         # Action when log full
var_auditd_num_logs: 10                        # Number of rotated logs to keep

# SSH configuration
sshd_idle_timeout_value: 300                   # SSH idle timeout (seconds)
var_sshd_set_keepalive: 0                      # SSH keepalive messages

# System umask
var_accounts_user_umask: '077'                 # Default user file creation mask

# Firewall
firewalld_default_zone: drop                   # Default firewall zone

# Cryptography
var_system_crypto_policy: FIPS:OSPP           # System crypto policy
```

### Step 3: Create Version-Specific Files (Optional)

For RHEL version-specific overrides, create `rhel8.yml`, `rhel9.yml`, or `rhel10.yml`:

```yaml
---
# RHEL 9 specific overrides
# These supplement or override common.yml for RHEL 9 systems

var_password_pam_minlen: 16                    # RHEL 9 requires longer passwords
```

## Using Tailoring Files

### Method 1: Specify in Playbook

```yaml
---
- hosts: all
  vars:
    rhel_stig_with_rollback_tailoring_profile: "myorg"
  roles:
    - role: rhel_stig_with_rollback
```

### Method 2: Extra Variables (CLI)

```bash
ansible-playbook -i inventory playbooks/rhel_stig_with_rollback.yml \
  -e rhel_stig_with_rollback_tailoring_profile=myorg
```

### Method 3: AAP Survey Variable

In Ansible Automation Platform, add a survey question:
- Variable: `rhel_stig_with_rollback_tailoring_profile`
- Type: Text
- Default: (leave empty for no tailoring)

### Method 4: Group Variables

Add to `group_vars/all.yml` or `group_vars/production.yml`:

```yaml
rhel_stig_with_rollback_tailoring_profile: "myorg"
```

## Variable Loading Order

Variables are loaded in this order (later overrides earlier):

1. STIG role defaults (`roles/rhel_stig_with_rollback/defaults/main.yml`)
2. Tailoring common file (`tailoring/<profile>/common.yml`)
3. Tailoring version-specific file (`tailoring/<profile>/rhel{{ version }}.yml`)
4. Group variables (`group_vars/`)
5. Host variables (`host_vars/`)
6. Playbook variables
7. Extra variables (`-e`)

## Available STIG Variables

Common STIG variables that organizations typically tailor:

### Password Complexity
- `var_password_pam_minlen` - Minimum password length
- `var_password_pam_dcredit` - Digit character requirement
- `var_password_pam_ucredit` - Uppercase character requirement
- `var_password_pam_lcredit` - Lowercase character requirement
- `var_password_pam_ocredit` - Special character requirement
- `var_password_pam_difok` - Characters different from previous
- `var_password_pam_maxrepeat` - Max repeated characters
- `var_password_pam_minclass` - Min character classes

### Account Lockout
- `var_accounts_passwords_pam_faillock_deny` - Failed login attempts
- `var_accounts_passwords_pam_faillock_unlock_time` - Lockout duration
- `var_accounts_passwords_pam_faillock_fail_interval` - Attempt window

### Session Management
- `var_accounts_tmout` - Session timeout (seconds)
- `sshd_idle_timeout_value` - SSH idle timeout
- `var_sshd_set_keepalive` - SSH keepalive count

### Audit Configuration
- `var_auditd_space_left` - Disk space alert threshold
- `var_auditd_space_left_action` - Action on low space
- `var_auditd_admin_space_left` - Admin alert threshold
- `var_auditd_max_log_file` - Max log file size
- `var_auditd_max_log_file_action` - Action on full log
- `var_auditd_num_logs` - Log rotation count

### Cryptography
- `var_system_crypto_policy` - System-wide crypto policy

### File Permissions
- `var_accounts_user_umask` - Default file creation mask

### Network Security
- `firewalld_default_zone` - Default firewall zone

For a complete list of available variables, run:

```bash
oscap xccdf generate fix --profile stig --output /tmp/remediation.sh /usr/share/xml/scap/ssg/content/ssg-rhel9-ds.xml
grep -E "^(var_|sshd_|firewalld_)" /tmp/remediation.sh | sort -u
```

## Best Practices

1. **Document Everything**: Add comments explaining why each variable is set
2. **Version Control**: Track tailoring files in git
3. **Test First**: Test tailoring files in development before production
4. **Peer Review**: Have security team review variable changes
5. **Compliance Mapping**: Reference organizational policies or compliance frameworks
6. **Regular Review**: Review tailoring files quarterly for relevance
7. **Backup**: Keep backups before applying new tailoring profiles

## Example Scenarios

### Scenario 1: Financial Institution

Higher security requirements:

```yaml
var_password_pam_minlen: 20
var_password_pam_difok: 10
var_accounts_passwords_pam_faillock_deny: 2
var_accounts_tmout: 300
sshd_idle_timeout_value: 180
```

### Scenario 2: Development Environment

Relaxed for developer productivity:

```yaml
var_password_pam_minlen: 12
var_accounts_passwords_pam_faillock_deny: 5
var_accounts_tmout: 1800
sshd_idle_timeout_value: 600
```

### Scenario 3: DoD Classified System

Maximum security:

```yaml
var_password_pam_minlen: 15
var_accounts_passwords_pam_faillock_deny: 3
var_accounts_tmout: 600
var_system_crypto_policy: "FIPS:OSPP"
firewalld_default_zone: drop
```

## Validation

After creating a tailoring file, validate it:

```bash
# Syntax check
ansible-playbook playbooks/rhel_stig_with_rollback.yml --syntax-check \
  -e rhel_stig_with_rollback_tailoring_profile=myorg

# Dry run (check mode)
ansible-playbook -i inventory playbooks/rhel_stig_with_rollback.yml \
  -e rhel_stig_with_rollback_tailoring_profile=myorg \
  -e rhel_stig_with_rollback_apply_remediations=false \
  --check
```

## Troubleshooting

### Issue: Variables Not Applied

**Check variable precedence:**
```bash
ansible-playbook playbooks/rhel_stig_with_rollback.yml \
  -e rhel_stig_with_rollback_tailoring_profile=myorg \
  -vv | grep "var_password_pam_minlen"
```

### Issue: Invalid Variable Value

**Review audit logs:**
```bash
cat /opt/stig_work/remediation_*.log
```

### Issue: Tailoring File Not Found

**Verify path:**
```bash
ls -la tailoring/myorg/
```

## Security Considerations

1. **Access Control**: Limit write access to tailoring files
2. **Audit Changes**: Log all modifications to tailoring files
3. **Approval Process**: Require security team approval for changes
4. **Compliance Review**: Ensure tailoring doesn't violate compliance requirements
5. **Documentation**: Document deviations from baseline STIG

## Support

For questions about STIG variables:
- DISA STIG documentation: https://public.cyber.mil/stigs/
- SCAP Security Guide: https://www.open-scap.org/security-policies/scap-security-guide/

For questions about this tailoring system:
- See main project documentation in `docs/`
