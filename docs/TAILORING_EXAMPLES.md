# STIG Tailoring Examples

Real-world examples of organization-specific STIG tailoring profiles.

## Table of Contents

- [Financial Services](#financial-services)
- [Healthcare / HIPAA](#healthcare--hipaa)
- [Government / DoD](#government--dod)
- [Development Environment](#development-environment)
- [Multi-Tier Environment](#multi-tier-environment)
- [Compliance-Specific](#compliance-specific)

## Financial Services

### Profile: High Security Bank

**Use Case:** PCI-DSS compliant financial institution with strict security requirements.

**Location:** `tailoring/financial-highsec/common.yml`

```yaml
---
# Organization: High Security Bank
# Purpose: PCI-DSS Compliance
# Created: 2026-11-03
# Approved By: CISO
# Review Cycle: Quarterly

# ==========================================
# PCI-DSS Requirement 8.2: User Passwords
# ==========================================

# PCI-DSS 8.2.3: Minimum length of 15 (we use 20 for enhanced security)
var_password_pam_minlen: 20

# PCI-DSS 8.2.3: Must contain numeric and alphabetic characters
var_password_pam_dcredit: -2              # Require 2 digits
var_password_pam_ucredit: -2              # Require 2 uppercase
var_password_pam_lcredit: -2              # Require 2 lowercase
var_password_pam_ocredit: -2              # Require 2 special chars

# Enhanced password complexity
var_password_pam_difok: 10                # 10 chars different from previous
var_password_pam_maxrepeat: 2             # Max 2 consecutive repeats
var_password_pam_minclass: 4              # All 4 character classes
var_password_pam_unix_remember: 24        # Remember last 24 passwords

# ==========================================
# PCI-DSS Requirement 8.1.6: Account Lockout
# ==========================================

var_accounts_passwords_pam_faillock_deny: 3            # 3 failed attempts max
var_accounts_passwords_pam_faillock_unlock_time: 1800  # 30 minute lockout
var_accounts_passwords_pam_faillock_fail_interval: 900 # 15 minute window

# ==========================================
# PCI-DSS Requirement 8.1.8: Session Timeout
# ==========================================

var_accounts_tmout: 600                   # 10 minute shell timeout
sshd_idle_timeout_value: 300              # 5 minute SSH timeout
var_sshd_set_keepalive: 0                 # No keepalive

# ==========================================
# PCI-DSS Requirement 10: Logging and Monitoring
# ==========================================

var_auditd_space_left: 30                 # Alert at 30% space remaining
var_auditd_space_left_action: email       # Email when low
var_auditd_admin_space_left: 15           # Admin alert at 15%
var_auditd_admin_space_left_action: halt  # Halt system if critical
var_auditd_max_log_file: 250              # 250 MB log files
var_auditd_max_log_file_action: rotate    # Rotate when full
var_auditd_num_logs: 30                   # Keep 30 rotated logs (90 days)
var_auditd_action_mail_acct: security-team@bank.com

# ==========================================
# Additional Security Controls
# ==========================================

var_accounts_user_umask: '077'            # Most restrictive umask
var_system_crypto_policy: "FIPS:OSPP"    # FIPS + OSPP crypto policy
firewalld_default_zone: drop              # Drop all by default

# SSH Hardening
var_sshd_disable_empty_passwords: true
var_sshd_disable_root_login: true
var_sshd_set_max_auth_tries: 3
```

### Usage:

```bash
ansible-playbook -i inventory playbooks/rhel_stig_with_rollback.yml \
  -e rhel_stig_with_rollback_tailoring_profile=financial-highsec
```

## Healthcare / HIPAA

### Profile: Healthcare Provider

**Use Case:** HIPAA-compliant healthcare organization protecting PHI.

**Location:** `tailoring/healthcare/common.yml`

```yaml
---
# Organization: Healthcare Provider Inc.
# Purpose: HIPAA Compliance - PHI Protection
# Reference: HIPAA Security Rule 164.308(a)(5)

# ==========================================
# HIPAA 164.308(a)(5)(ii)(D): Password Management
# ==========================================

var_password_pam_minlen: 16               # HIPAA recommended minimum
var_password_pam_dcredit: -1
var_password_pam_ucredit: -1
var_password_pam_lcredit: -1
var_password_pam_ocredit: -1
var_password_pam_difok: 8
var_password_pam_unix_remember: 12        # Remember last 12 passwords

# ==========================================
# HIPAA 164.308(a)(5)(ii)(C): Automatic Logoff
# ==========================================

var_accounts_tmout: 900                   # 15 minute timeout per policy
sshd_idle_timeout_value: 600              # 10 minute SSH timeout

# ==========================================
# HIPAA 164.312(a)(2)(i): Unique User Identification
# ==========================================

var_accounts_passwords_pam_faillock_deny: 5
var_accounts_passwords_pam_faillock_unlock_time: 1200  # 20 minutes

# ==========================================
# HIPAA 164.312(b): Audit Controls
# ==========================================

var_auditd_space_left: 25
var_auditd_space_left_action: email
var_auditd_admin_space_left: 10
var_auditd_max_log_file: 200
var_auditd_num_logs: 15                   # 60 days retention
var_auditd_action_mail_acct: hipaa-compliance@healthcare.org

# ==========================================
# HIPAA 164.312(e)(2)(ii): Encryption
# ==========================================

var_system_crypto_policy: "FIPS"
```

## Government / DoD

### Profile: DoD Classified System

**Use Case:** Department of Defense classified information system.

**Location:** `tailoring/dod-classified/common.yml`

```yaml
---
# Organization: DoD Agency
# Purpose: Classified Information Protection
# Classification: SECRET
# Reference: DoDI 8500.01, RMF, NIST 800-53

# ==========================================
# NIST 800-53 IA-5: Authenticator Management
# ==========================================

var_password_pam_minlen: 15               # CAC + password minimum
var_password_pam_dcredit: -1
var_password_pam_ucredit: -1
var_password_pam_lcredit: -1
var_password_pam_ocredit: -1
var_password_pam_difok: 8
var_password_pam_minclass: 4
var_password_pam_unix_remember: 24

# ==========================================
# NIST 800-53 AC-11: Session Lock
# ==========================================

var_accounts_tmout: 600                   # 10 minutes per STIG
sshd_idle_timeout_value: 600              # Match shell timeout

# ==========================================
# NIST 800-53 AC-7: Unsuccessful Login Attempts
# ==========================================

var_accounts_passwords_pam_faillock_deny: 3
var_accounts_passwords_pam_faillock_unlock_time: 900
var_accounts_passwords_pam_faillock_fail_interval: 900

# ==========================================
# NIST 800-53 AU-11: Audit Record Retention
# ==========================================

var_auditd_space_left: 30
var_auditd_space_left_action: email
var_auditd_admin_space_left: 10
var_auditd_admin_space_left_action: halt  # Never lose audit data
var_auditd_max_log_file: 500              # Large logs for investigation
var_auditd_num_logs: 50                   # Long retention
var_auditd_action_mail_acct: isso@dod.mil

# ==========================================
# NIST 800-53 SC-13: Cryptographic Protection
# ==========================================

var_system_crypto_policy: "FIPS:OSPP"    # Maximum crypto strength
var_accounts_user_umask: '077'            # No group/other access
firewalld_default_zone: drop              # Default deny all

# SSH Configuration for DoD
var_sshd_disable_root_login: true
var_sshd_disable_gssapi_auth: false       # Keep for CAC/PKI
var_sshd_set_max_auth_tries: 3
```

## Development Environment

### Profile: Developer Workstations

**Use Case:** Development environment balancing security with productivity.

**Location:** `tailoring/development/common.yml`

```yaml
---
# Organization: Software Development Team
# Purpose: Development Environment
# Note: Relaxed settings for developer productivity

# ==========================================
# Password Policies - Relaxed but Secure
# ==========================================

var_password_pam_minlen: 12               # Shorter for dev convenience
var_password_pam_dcredit: -1
var_password_pam_ucredit: -1
var_password_pam_lcredit: -1
var_password_pam_ocredit: -1
var_password_pam_difok: 5
var_password_pam_unix_remember: 5

# ==========================================
# Account Lockout - More Forgiving
# ==========================================

var_accounts_passwords_pam_faillock_deny: 5      # More attempts
var_accounts_passwords_pam_faillock_unlock_time: 600   # 10 min lockout
var_accounts_passwords_pam_faillock_fail_interval: 1800

# ==========================================
# Session Management - Longer Timeouts
# ==========================================

var_accounts_tmout: 1800                  # 30 minutes (long debugging sessions)
sshd_idle_timeout_value: 900              # 15 minutes SSH

# ==========================================
# Audit - Smaller Logs
# ==========================================

var_auditd_space_left: 20
var_auditd_space_left_action: syslog      # Don't halt dev systems
var_auditd_admin_space_left: 10
var_auditd_admin_space_left_action: suspend
var_auditd_max_log_file: 50
var_auditd_num_logs: 5

# ==========================================
# Cryptography - Standard FIPS
# ==========================================

var_system_crypto_policy: "FIPS"          # FIPS but not OSPP
firewalld_default_zone: public            # Allow more connectivity
```

## Multi-Tier Environment

### Production Profile

**Location:** `tailoring/production/common.yml`

```yaml
---
# Organization: Multi-Tier Corp
# Environment: Production
# Purpose: Production system hardening

var_password_pam_minlen: 16
var_password_pam_dcredit: -2
var_password_pam_ucredit: -2
var_password_pam_lcredit: -2
var_password_pam_ocredit: -1

var_accounts_passwords_pam_faillock_deny: 3
var_accounts_passwords_pam_faillock_unlock_time: 1800

var_accounts_tmout: 600
sshd_idle_timeout_value: 300

var_auditd_space_left: 30
var_auditd_max_log_file: 250
var_auditd_num_logs: 30

var_system_crypto_policy: "FIPS:OSPP"
firewalld_default_zone: drop
```

### Staging Profile

**Location:** `tailoring/staging/common.yml`

```yaml
---
# Organization: Multi-Tier Corp
# Environment: Staging
# Purpose: Pre-production testing (matches production)

# Same as production for realistic testing
var_password_pam_minlen: 16
var_password_pam_dcredit: -2
var_password_pam_ucredit: -2
var_password_pam_lcredit: -2
var_password_pam_ocredit: -1

var_accounts_passwords_pam_faillock_deny: 3
var_accounts_tmout: 600

var_system_crypto_policy: "FIPS:OSPP"

# Slightly relaxed audit for testing
var_auditd_num_logs: 10
```

### Development Profile

See [Development Environment](#development-environment) above.

### Group Variable Assignment

```yaml
# group_vars/production.yml
rhel_stig_with_rollback_tailoring_profile: "production"

# group_vars/staging.yml
rhel_stig_with_rollback_tailoring_profile: "staging"

# group_vars/development.yml
rhel_stig_with_rollback_tailoring_profile: "development"
```

## Compliance-Specific

### SOX Compliance

**Location:** `tailoring/sox-compliance/common.yml`

```yaml
---
# Organization: Public Company
# Purpose: SOX IT Controls Compliance
# Reference: SOX 404, COBIT, ITGC

# SOX ITGC-ACC-05: Session Timeout
var_accounts_tmout: 900                   # 15 minutes per policy
sshd_idle_timeout_value: 600

# SOX ITGC-ACC-03: Password Complexity
var_password_pam_minlen: 15
var_password_pam_dcredit: -1
var_password_pam_ucredit: -1
var_password_pam_lcredit: -1
var_password_pam_ocredit: -1
var_password_pam_unix_remember: 12        # Prevent reuse

# SOX ITGC-ACC-04: Account Lockout
var_accounts_passwords_pam_faillock_deny: 5
var_accounts_passwords_pam_faillock_unlock_time: 1200

# SOX ITGC-AUD-01: Audit Logging
var_auditd_space_left: 25
var_auditd_max_log_file: 200
var_auditd_num_logs: 20                   # 7 year retention via archival
var_auditd_action_mail_acct: sox-compliance@company.com
```

### ISO 27001

**Location:** `tailoring/iso27001/common.yml`

```yaml
---
# Organization: ISO 27001 Certified Corp
# Purpose: ISO 27001:2013 Compliance
# Reference: Annex A Controls

# A.9.4.2: Secure log-on procedures
var_password_pam_minlen: 15
var_password_pam_minclass: 4
var_accounts_passwords_pam_faillock_deny: 3

# A.11.2.8: Unattended user equipment
var_accounts_tmout: 600
sshd_idle_timeout_value: 600

# A.12.4.1: Event logging
var_auditd_space_left: 25
var_auditd_max_log_file: 200
var_auditd_num_logs: 15

# A.10.1.1: Policy on the use of cryptographic controls
var_system_crypto_policy: "FIPS"
```

## Version-Specific Overrides

### RHEL 8 Limitations

**Location:** `tailoring/myorg/rhel8.yml`

```yaml
---
# RHEL 8 Specific Overrides
# Some features not available in RHEL 8

# RHEL 8 doesn't support OSPP subpolicy
var_system_crypto_policy: "FIPS"

# RHEL 8 has older PAM modules
var_password_pam_minclass: 3              # RHEL 8 limitation
```

### RHEL 9+ Enhanced Features

**Location:** `tailoring/myorg/rhel9.yml`

```yaml
---
# RHEL 9+ Enhanced Security Features

# RHEL 9 supports extended crypto policies
var_system_crypto_policy: "FIPS:OSPP"

# RHEL 9 enhanced PAM features
var_password_pam_minclass: 4
var_password_pam_maxclassrepeat: 3

# RHEL 9 improved faillock
var_accounts_passwords_pam_faillock_deny: 3
var_accounts_passwords_pam_faillock_unlock_time: 1800
```

## Testing Your Tailoring

### Validation Commands

```bash
# 1. Test loading variables
ansible-playbook playbooks/test_tailoring.yml \
  -e rhel_stig_with_rollback_tailoring_profile=myorg

# 2. Audit only with tailoring
ansible-playbook -i inventory playbooks/rhel_stig_with_rollback.yml \
  -e rhel_stig_with_rollback_tailoring_profile=myorg \
  -e rhel_stig_with_rollback_apply_remediations=false

# 3. Apply to test system
ansible-playbook -i inventory playbooks/rhel_stig_with_rollback.yml \
  -e rhel_stig_with_rollback_tailoring_profile=myorg \
  --limit test-server

# 4. Verify applied settings
ansible -i inventory all -m shell -a "grep PASS_MIN_LEN /etc/login.defs"
```

## Best Practices from Examples

1. **Document Everything**: Each variable has a comment explaining the requirement
2. **Reference Standards**: Link to PCI-DSS, HIPAA, NIST, etc.
3. **Include Metadata**: Organization, date, approval, review cycle
4. **Version Control**: Track changes to tailoring files
5. **Environment-Specific**: Different profiles for dev/staging/prod
6. **Test First**: Always test in development before production
7. **Compliance Mapping**: Map variables to specific controls
8. **Regular Review**: Schedule quarterly reviews

## Additional Resources

- [TAILORING_GUIDE.md](TAILORING_GUIDE.md) - Complete tailoring documentation
- [DISA STIG Viewer](https://public.cyber.mil/stigs/srg-stig-tools/)
- [NIST 800-53 Controls](https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final)
- [PCI-DSS Requirements](https://www.pcisecuritystandards.org/)
- [HIPAA Security Rule](https://www.hhs.gov/hipaa/for-professionals/security/index.html)
