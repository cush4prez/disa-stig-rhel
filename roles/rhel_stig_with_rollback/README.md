# rhel_stig_with_rollback

Ansible role for applying DISA STIG hardening to RHEL 8/9/10 systems with automated rollback protection.

## Description

This role automates DISA STIG (Defense Information Systems Agency Security Technical Implementation Guide) compliance hardening for Red Hat Enterprise Linux systems. It provides intelligent rollback capabilities that automatically revert changes if the system becomes inoperable.

**Key Features:**
- **Multi-version support**: RHEL 8, 9, and 10
- **Automated backup**: Creates pre-hardening system state snapshots
- **Operational verification**: Checks if system remains functional after hardening
- **Smart rollback**: Automatically reverts changes if critical services fail
- **noexec-compatible**: All paths work with DISA-hardened systems (noexec on /var, /tmp, /home)
- **Sudo-user ready**: Designed for DISA environments where root is disabled
- **Modular phases**: Each hardening phase is a separate, tagged task file

## Requirements

### Target System Requirements
- RHEL 8, 9, or 10
- `openscap-scanner` package
- `scap-security-guide` package
- At least 2GB free space in `/opt` for backups and work files

### Ansible Requirements
- Ansible 2.9 or higher
- `ansible.posix` collection (for synchronize module in rollback)

## Role Variables

All variables are defined in `defaults/main.yml` and can be overridden.

### Backup Configuration

```yaml
# Enable/disable automatic backup before hardening
rhel_stig_with_rollback_enable_auto_backup: true

# Root directory for backups
rhel_stig_with_rollback_backup_root: "/opt/stig_backups"

# Backup naming (auto-generated timestamp)
rhel_stig_with_rollback_backup_timestamp: "{{ ansible_date_time.iso8601_basic_short }}"
rhel_stig_with_rollback_backup_name: "pre_stig_{{ ansible_hostname }}_{{ rhel_stig_with_rollback_backup_timestamp }}"
```

### STIG Configuration

```yaml
# Path to SCAP data stream (auto-detects RHEL version)
rhel_stig_with_rollback_scap_ds_path: "/usr/share/xml/scap/ssg/content/ssg-rhel{{ ansible_distribution_major_version }}-ds.xml"

# STIG profile to apply
rhel_stig_with_rollback_stig_profile_id: "xccdf_org.ssgproject.content_profile_stig"

# Audit output directory (noexec-safe)
rhel_stig_with_rollback_stig_audit_dir: "/opt/stig_audit"

# Working directory for scripts (noexec-safe)
rhel_stig_with_rollback_stig_work_dir: "/opt/stig_work"
```

### Remediation Control

```yaml
# Apply STIG remediations (set false for audit-only)
rhel_stig_with_rollback_apply_remediations: true

# Require user confirmation before applying (not yet implemented)
rhel_stig_with_rollback_require_confirmation: true
```

### Rollback Configuration

```yaml
# Automatically rollback if system becomes inoperable
rhel_stig_with_rollback_auto_rollback_on_failure: true

# Rollback if critical services fail
rhel_stig_with_rollback_rollback_on_critical_service_failure: true

# Services that must remain running
rhel_stig_with_rollback_critical_services:
  - sshd
  - NetworkManager
```

## Dependencies

None. This is a standalone role.

## Example Playbooks

### Basic Usage

```yaml
---
- name: Harden RHEL systems with STIG
  hosts: rhel_servers
  become: true
  gather_facts: true

  roles:
    - rhel_stig_with_rollback
```

### Audit Only (No Remediation)

```yaml
---
- name: Audit RHEL STIG compliance without applying fixes
  hosts: rhel_servers
  become: true
  gather_facts: true

  roles:
    - role: rhel_stig_with_rollback
      vars:
        rhel_stig_with_rollback_apply_remediations: false
```

### Custom Backup Location

```yaml
---
- name: Harden with custom backup path
  hosts: rhel_servers
  become: true
  gather_facts: true

  roles:
    - role: rhel_stig_with_rollback
      vars:
        rhel_stig_with_rollback_backup_root: "/production/backups"
        rhel_stig_with_rollback_enable_auto_backup: true
```

### Disable Backup (Not Recommended)

```yaml
---
- name: Harden without backup (use with caution!)
  hosts: rhel_servers
  become: true
  gather_facts: true

  roles:
    - role: rhel_stig_with_rollback
      vars:
        rhel_stig_with_rollback_enable_auto_backup: false
```

## Using Tags

The role supports tags for running specific phases:

```bash
# Run only validation
ansible-playbook site.yml --tags validation

# Run backup and audit only
ansible-playbook site.yml --tags backup,audit

# Skip backup
ansible-playbook site.yml --skip-tags backup

# Run remediation only (assumes backup and audit already done)
ansible-playbook site.yml --tags remediation

# Get summary without applying fixes
ansible-playbook site.yml --tags audit,summary -e rhel_stig_with_rollback_apply_remediations=false
```

### Available Tags

- `validation` - Pre-flight checks (always runs)
- `backup` - Create pre-hardening backup
- `audit`, `baseline` - Baseline compliance scan
- `remediation` - Apply STIG fixes
- `verification`, `operational-check` - Post-hardening verification
- `summary`, `report` - Final compliance report

## Role Phases

The role executes in 6 phases:

### Phase 1: Pre-hardening Validation
**File:** `tasks/phase1_validation.yml`

- Verifies RHEL version (8, 9, or 10)
- Checks for SCAP content
- Installs openscap-scanner and scap-security-guide if missing
- Displays hardening plan

### Phase 2: Create Pre-hardening Backup
**File:** `tasks/phase2_backup.yml`

- Creates backup directories
- Backs up critical configuration files
- Backs up security state (firewall, SELinux, etc.)
- Creates compressed backup archive
- Can be skipped with `rhel_stig_with_rollback_enable_auto_backup: false`

### Phase 3: Baseline Audit
**File:** `tasks/phase3_baseline_audit.yml`

- Runs OpenSCAP compliance scan
- Generates baseline HTML report
- Parses compliance score
- Displays current compliance percentage

### Phase 4: Generate and Apply Remediations
**File:** `tasks/phase4_remediation.yml`

- Generates bash remediation script from baseline scan
- Validates script was created and has content
- Executes remediation script
- Logs all output
- Handles non-zero exit codes gracefully
- Can be skipped with `rhel_stig_with_rollback_apply_remediations: false`

### Phase 5: Post-hardening Verification
**File:** `tasks/phase5_verification.yml`

- Runs comprehensive operational checks:
  - SSH service status and connectivity
  - PAM authentication files
  - Filesystem writability
  - Critical services status
- Decides if rollback is needed based on operability
- Executes emergency rollback if system is inoperable
- Runs post-hardening compliance scan
- Parses final compliance score

### Phase 6: Final Summary
**File:** `tasks/phase6_summary.yml`

- Displays before/after compliance scores
- Shows compliance improvement percentage
- Lists all report and log file locations
- Creates rollback instructions file
- Provides manual rollback commands

## Rollback Mechanism

### When Rollback Occurs

The role automatically initiates rollback when:
1. Critical services (SSH, NetworkManager) fail after hardening
2. System becomes inoperable (cannot execute commands, filesystem read-only, PAM broken)
3. `rhel_stig_with_rollback_auto_rollback_on_failure: true` (default)

### What Gets Rolled Back

**Emergency rollback restores:**
- SSH configuration (`/etc/ssh/sshd_config`)
- PAM configuration (`/etc/pam.d/*`)
- Sudoers configuration (`/etc/sudoers`)
- Login definitions (`/etc/login.defs`)
- Critical services are restarted

**Full rollback** (using `playbooks/perform_rollback.yml`) restores everything.

### Manual Rollback

```bash
# Using rollback playbook
ansible-playbook -i inventory playbooks/perform_rollback.yml \
  -e rhel_stig_with_rollback_backup_name=pre_stig_hostname_20261001T120000

# Manual extraction
cd /opt/stig_backups
tar -xzf pre_stig_hostname_20261001T120000.tar.gz
cp -r backup_20261001T120000/config_files/etc/* /etc/
```

## File Locations

All files are stored in noexec-safe locations:

| Type | Location | Example |
|------|----------|---------|
| Backups | `/opt/stig_backups/` | `pre_stig_host_20261001T120000.tar.gz` |
| Audit Reports | `/opt/stig_audit/` | `baseline_20261001T120000.html` |
| Remediation Scripts | `/opt/stig_work/` | `remediation_20261001T120000.sh` |
| Remediation Logs | `/opt/stig_work/` | `remediation_20261001T120000.log` |
| Rollback Instructions | `/opt/stig_backups/` | `ROLLBACK_INSTRUCTIONS.txt` |

## Troubleshooting

### STIGs Not Being Applied

If compliance score remains unchanged:

1. **Check remediation script was generated:**
   ```bash
   ls -lh /opt/stig_work/remediation_*.sh
   ```

2. **Check script has actual fixes:**
   ```bash
   wc -l /opt/stig_work/remediation_*.sh
   grep -c "^# Remediates:" /opt/stig_work/remediation_*.sh
   ```

3. **Review remediation log:**
   ```bash
   cat /opt/stig_work/remediation_*.log
   ```

4. **Run diagnostic playbook:**
   ```bash
   ansible-playbook -i inventory playbooks/diagnose_remediation.yml
   ```

### Permission Denied on Scripts

This role is designed to work with noexec filesystems. If you get permission errors:

- Scripts are executed from `/opt/stig_work/` (should not have noexec)
- Verify `/opt` is not mounted with noexec:
  ```bash
  mount | grep /opt
  ```

### System Became Inoperable

If the role rolled back automatically:

1. **Check failure summary:**
   ```bash
   cat /opt/stig_audit/ROLLBACK_FAILURE_SUMMARY.txt
   ```

2. **Review what failed:**
   ```bash
   cat /opt/stig_work/remediation_*.log | grep -i "error\|fail"
   ```

3. **Run audit-only mode to identify problematic rules:**
   ```bash
   ansible-playbook site.yml -e rhel_stig_with_rollback_apply_remediations=false
   ```

## Security Considerations

1. **Backup Security**: Backups contain sensitive system configuration. Ensure `/opt/stig_backups/` has appropriate permissions.

2. **Sudo vs Root**: This role uses `become: true`. Ensure your user has appropriate sudo privileges.

3. **Network Lockout**: The role checks SSH accessibility before finalizing. Manual console access may still be needed if SSH configuration is incompatible with your environment.

4. **Compliance vs. Operability**: The role prioritizes operability over compliance. It will rollback changes that break the system even if they are STIG-required.

## License

MIT

## Author Information

This role was created for RHEL DISA STIG hardening automation.

For issues, questions, or contributions, see the project repository.

## Related Playbooks

- `playbooks/site.yml` - Main playbook using this role
- `playbooks/diagnose_remediation.yml` - Diagnostic playbook for troubleshooting
- `playbooks/perform_rollback.yml` - Full system rollback
- `playbooks/verify_system_operational.yml` - Standalone operational checks
