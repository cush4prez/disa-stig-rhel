# Tailoring Quick Start

Get started with STIG tailoring in 5 minutes.

## 1. Create Your Profile

```bash
# Create organization directory
mkdir -p tailoring/myorg

# Copy template
cp tailoring/example_tailoring.yml tailoring/myorg/common.yml
```

## 2. Edit Your Variables

Edit `tailoring/myorg/common.yml`:

```yaml
---
# Your Organization Name
# Created: $(date +%Y-%m-%d)

# Essential variables (most commonly customized)
var_password_pam_minlen: 15                         # Password length
var_accounts_tmout: 600                             # Session timeout (seconds)
var_accounts_passwords_pam_faillock_deny: 3        # Failed login attempts
sshd_idle_timeout_value: 300                        # SSH timeout (seconds)
var_auditd_max_log_file: 100                       # Audit log size (MB)
var_system_crypto_policy: "FIPS"                   # Crypto policy
```

## 3. Use Your Profile

### Option A: Command Line

```bash
ansible-playbook -i inventory playbooks/rhel_stig_with_rollback.yml \
  -e rhel_stig_with_rollback_tailoring_profile=myorg
```

### Option B: Group Variables

```yaml
# group_vars/all.yml
rhel_stig_with_rollback_tailoring_profile: "myorg"
```

### Option C: AAP Survey

Add tailoring profile name in the survey field when launching the job.

## 4. Test First

```bash
# Test loading (no changes)
ansible-playbook playbooks/test_tailoring.yml \
  -e rhel_stig_with_rollback_tailoring_profile=myorg

# Audit only (no remediations)
ansible-playbook -i inventory playbooks/rhel_stig_with_rollback.yml \
  -e rhel_stig_with_rollback_tailoring_profile=myorg \
  -e rhel_stig_with_rollback_apply_remediations=false
```

## Common Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `var_password_pam_minlen` | 15 | Minimum password length |
| `var_accounts_tmout` | 600 | Shell session timeout (seconds) |
| `var_accounts_passwords_pam_faillock_deny` | 3 | Failed login attempts before lockout |
| `sshd_idle_timeout_value` | 300 | SSH idle timeout (seconds) |
| `var_auditd_max_log_file` | 100 | Maximum audit log file size (MB) |
| `var_auditd_num_logs` | 10 | Number of rotated logs to keep |
| `var_system_crypto_policy` | FIPS | System cryptographic policy |

## Version-Specific Overrides (Optional)

Create `tailoring/myorg/rhel9.yml` for RHEL 9 specific settings:

```yaml
---
# RHEL 9 specific overrides
var_system_crypto_policy: "FIPS:OSPP"    # RHEL 9 supports extended policy
```

## Need Help?

- **Full Guide**: See [docs/TAILORING_GUIDE.md](../docs/TAILORING_GUIDE.md)
- **Examples**: See [docs/TAILORING_EXAMPLES.md](../docs/TAILORING_EXAMPLES.md)
- **Template**: See [example_tailoring.yml](example_tailoring.yml)
- **Test**: Run `ansible-playbook playbooks/test_tailoring.yml`

## Validation Checklist

- [ ] Created `tailoring/myorg/` directory
- [ ] Copied and edited `common.yml`
- [ ] Added organization metadata (name, date, approval)
- [ ] Documented why each variable is set
- [ ] Tested with `test_tailoring.yml`
- [ ] Tested audit-only mode in development
- [ ] Reviewed with security team
- [ ] Committed to version control

## Quick Reference

**Load tailoring**: Set `rhel_stig_with_rollback_tailoring_profile` variable
**No tailoring**: Leave variable empty or undefined
**Test loading**: `ansible-playbook playbooks/test_tailoring.yml`
**Audit only**: Set `rhel_stig_with_rollback_apply_remediations=false`
