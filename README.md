# RHEL Security Hardening with Rollback (STIG & CIS)

Ansible automation for applying **DISA STIG** or **CIS Benchmarks** to RHEL 8/9/10 systems with intelligent rollback protection and selective audit capabilities.

## Features

- ✅ **Multiple Benchmarks** - DISA STIG, CIS L1/L2 (Server/Workstation), or custom profiles
- ✅ **Selective or Full Auditing** - Audit specific rules or all rules
- ✅ **Ansible-based Remediation** - Native Ansible tasks (not bash scripts)
- ✅ **Native XML Parsing** - No Python scripts, pure Ansible using community.general.xml
- ✅ **Organization Tailoring** - Customize variables for your organization
- ✅ **Automatic Backup** - Pre-hardening snapshots with disaster recovery
- ✅ **Intelligent Rollback** - Auto-rollback on operational failures
- ✅ **AAP 2.7 Integration** - Survey-based configuration for easy deployment
- ✅ **RHEL 8/9/10 Support** - Works across multiple RHEL versions

## Quick Start

### Option 1: Interactive Mode (CLI)

```bash
ansible-playbook -i inventory playbooks/rhel_stig_with_rollback_interactive.yml
```

Prompts you for:
- Full or selective STIG audit mode
- Which STIG rules to audit (if selective)
- Whether to apply remediations
- Auto-rollback settings

### Option 2: Using the Role (Recommended for Production)

The cleanest approach - just invokes the role:

```bash
ansible-playbook -i inventory playbooks/site.yml
```

Pass variables via extra vars or group_vars:

```bash
# DISA STIG (default)
ansible-playbook -i inventory playbooks/site.yml \
  -e rhel_stig_with_rollback_tailoring_profile=myorg \
  -e rhel_stig_with_rollback_apply_remediations=true

# CIS Server Level 1
ansible-playbook -i inventory playbooks/site.yml \
  -e rhel_stig_with_rollback_benchmark_profile=cis_server_l1 \
  -e rhel_stig_with_rollback_apply_remediations=true

# CIS Server Level 2
ansible-playbook -i inventory playbooks/site.yml \
  -e rhel_stig_with_rollback_benchmark_profile=cis_server_l2 \
  -e rhel_stig_with_rollback_apply_remediations=true
```

**Available Benchmark Profiles**: `stig` (default), `cis`, `cis_server_l1`, `cis_server_l2`, `cis_workstation_l1`, `cis_workstation_l2`, `custom`

See [docs/CIS_BENCHMARK_GUIDE.md](docs/CIS_BENCHMARK_GUIDE.md) for complete CIS configuration details.

Or create your own minimal playbook:

```yaml
---
- hosts: all
  roles:
    - role: rhel_stig_with_rollback
      rhel_stig_with_rollback_stig_rules_to_apply:
        - sysctl_crypto_fips_enabled
        - audit_rules_login_events
      rhel_stig_with_rollback_apply_remediations: true
```

**Why site.yml?**
- ✅ Uses role (native Ansible parsing)
- ✅ Clean, maintainable code
- ✅ No duplicate logic
- ✅ Recommended for AAP deployments

See [docs/PLAYBOOK_USAGE.md](docs/PLAYBOOK_USAGE.md) for comparison of all playbooks.

### Option 3: Ansible Automation Platform (AAP 2.7)

1. **Create Project** pointing to this repository
2. **Create Job Template** with `playbooks/site.yml` ⭐ **(recommended - uses role)**
3. **Add Survey** manually (5 questions - see guide below)
4. **Enable Survey** on the job template
5. **Launch** and fill out the survey form

**Quick Survey Setup**: Add these 5 questions manually in AAP GUI:
- Question 1: `stig_audit_mode` - Multiple Choice: `full` or `selective`
- Question 2: `stig_rules_input` - Textarea (comma-separated rule IDs)
- Question 3: `rhel_stig_with_rollback_apply_remediations` - Multiple Choice: `true` or `false`
- Question 4: `rhel_stig_with_rollback_auto_rollback_on_failure` - Multiple Choice: `true` or `false`
- Question 5: `rhel_stig_with_rollback_tailoring_profile` - Text (optional)

**Note**: The survey works with `site.yml` because it calls the role. The role automatically processes survey variables via its `pre_tasks`.

See [docs/AAP_COMPLETE_GUIDE.md](docs/AAP_COMPLETE_GUIDE.md) for complete step-by-step instructions.

## Available Playbooks

### Production Playbooks

| Playbook | Purpose | Use Case |
|----------|---------|----------|
| `rhel_stig_with_rollback.yml` | Main STIG workflow (AAP compatible) | Production hardening with survey |
| `rhel_stig_with_rollback_interactive.yml` | Interactive CLI version | CLI-based deployment with prompts |
| `perform_rollback.yml` | Restore from backup | Rollback after failed hardening |
| `rhel_stig_audit_only.yml` | Audit without remediation | Compliance reporting only |
| `final_audit_report.yml` | Detailed audit with CAT I/II/III breakdown | Post-hardening validation |

### Diagnostic Playbooks

| Playbook | Purpose |
|----------|---------|
| `diagnose_stig_remediation.yml` | Diagnose remediation issues |
| `full_diagnostic.yml` | Complete system diagnostic |
| `verify_system_operational.yml` | Check system health |

### Utility Playbooks

| Playbook | Purpose |
|----------|---------|
| `rhel_stig_backup_state.yml` | Create backup only |
| `emergency_restore_from_controller.yml` | Restore from AAP controller backup |
| `rhel_stig_query.yml` | Query system STIG status |

## Selective STIG Workflow

**New Feature:** Audit and remediate only specific STIG rules instead of all rules.

### How It Works

1. **Specify Rules**: List specific STIG rule IDs to audit
2. **Audit Selected**: Only those rules are audited
3. **Identify Failures**: See which selected rules pass/fail
4. **Remediate Failures**: Only failed rules are remediated

### Example

```yaml
# Audit only these 3 rules
rhel_stig_with_rollback_stig_rules_to_apply:
  - sysctl_crypto_fips_enabled
  - audit_rules_login_events
  - sshd_set_idle_timeout

# Leave empty for full audit
rhel_stig_with_rollback_stig_rules_to_apply: []
```

See [docs/SURVEY_CONFIGURATION.md](docs/SURVEY_CONFIGURATION.md) for complete guide.

## Organization Tailoring

**New Feature:** Customize STIG security control variables for your organization.

### Quick Example

```bash
# Create your organization's tailoring profile
mkdir -p tailoring/myorg
cp tailoring/example_tailoring.yml tailoring/myorg/common.yml

# Edit with your values
vim tailoring/myorg/common.yml

# Apply with tailoring
ansible-playbook -i inventory playbooks/rhel_stig_with_rollback.yml \
  -e rhel_stig_with_rollback_tailoring_profile=myorg
```

### Common Tailoring Variables

- `var_password_pam_minlen` - Password length requirement
- `var_accounts_tmout` - Session timeout (seconds)
- `var_accounts_passwords_pam_faillock_deny` - Failed login attempts
- `sshd_idle_timeout_value` - SSH idle timeout
- `var_auditd_max_log_file` - Audit log size

See [docs/TAILORING_GUIDE.md](docs/TAILORING_GUIDE.md) for complete documentation.

## Native Ansible Parsing

**New Feature:** XML parsing using native Ansible modules instead of Python scripts.

### Benefits

- 🔒 **Better Security** - No script execution on target hosts
- 🚀 **Easier Maintenance** - Pure Ansible, no Python expertise required
- ✅ **Built-in Idempotency** - Declarative approach with Ansible's error handling
- 📦 **No Script Distribution** - Reduces attack surface and deployment complexity

### Usage

Native parsing is enabled by default. To use legacy Python scripts:

```yaml
# group_vars/all.yml or extra vars
rhel_stig_with_rollback_use_native_parsing: false
```

See [docs/NATIVE_ANSIBLE_MIGRATION.md](docs/NATIVE_ANSIBLE_MIGRATION.md) for complete details.

## Role Variables

### Core Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `rhel_stig_with_rollback_apply_remediations` | `true` | Apply remediations after audit |
| `rhel_stig_with_rollback_enable_auto_backup` | `true` | Create pre-hardening backup |
| `rhel_stig_with_rollback_auto_rollback_on_failure` | `true` | Auto-rollback on verification failure |

### Tailoring Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `rhel_stig_with_rollback_tailoring_profile` | `""` | Organization tailoring profile (empty = defaults) |

### Parsing Method

| Variable | Default | Description |
|----------|---------|-------------|
| `rhel_stig_with_rollback_use_native_parsing` | `true` | Use native Ansible XML parsing (recommended) |

### Selective STIG Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `rhel_stig_with_rollback_stig_rules_to_apply` | `[]` | List of STIG rule IDs (empty = full mode) |

### Paths

| Variable | Default | Description |
|----------|---------|-------------|
| `rhel_stig_with_rollback_backup_root` | `/opt/stig_backups` | Backup storage location |
| `rhel_stig_with_rollback_stig_audit_dir` | `/opt/stig_audit` | Audit results directory |
| `rhel_stig_with_rollback_controller_backup_dir` | `/var/lib/awx/projects/stig_backups` | AAP controller backup location |

See `roles/rhel_stig_with_rollback/defaults/main.yml` for all variables.

## Documentation

### Essential Guides

- **[AAP_COMPLETE_GUIDE.md](docs/AAP_COMPLETE_GUIDE.md)** - Complete AAP 2.7 setup and usage
- **[SURVEY_CONFIGURATION.md](docs/SURVEY_CONFIGURATION.md)** - Survey setup and selective STIG workflow
- **[TAILORING_GUIDE.md](docs/TAILORING_GUIDE.md)** - Organization-specific STIG variable customization
- **[NATIVE_ANSIBLE_MIGRATION.md](docs/NATIVE_ANSIBLE_MIGRATION.md)** - Native Ansible XML parsing (recommended)
- **[RHEL8_COMPATIBILITY.md](docs/RHEL8_COMPATIBILITY.md)** - RHEL 8 compatibility and try-fallback pattern
- **[TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[DISASTER_RECOVERY.md](docs/DISASTER_RECOVERY.md)** - Emergency recovery procedures

### Reference Guides

- **[PLAYBOOK_USAGE.md](docs/PLAYBOOK_USAGE.md)** - Which playbooks to use (IMPORTANT)
- **[PLAYBOOK_REFERENCE.md](docs/PLAYBOOK_REFERENCE.md)** - Complete playbook descriptions
- **[ROLE_DOCUMENTATION.md](docs/ROLE_DOCUMENTATION.md)** - Role architecture and phases

## Requirements

- RHEL 8, 9, or 10
- openscap-scanner
- scap-security-guide
- Ansible 2.9+
- Ansible Collections:
  - `community.general` >= 8.0.0 (for native XML parsing)
- python3-lxml (auto-installed on RHEL 8 if missing)

Install collections:
```bash
ansible-galaxy collection install -r requirements.yml
```

The role automatically installs missing SCAP packages and python3-lxml dependencies.

**Note**: For RHEL 8 compatibility, see [docs/RHEL8_COMPATIBILITY.md](docs/RHEL8_COMPATIBILITY.md)

## Common Tasks

### Audit Current Compliance

```bash
ansible-playbook -i inventory playbooks/rhel_stig_audit_only.yml
```

### View Detailed Audit Report

```bash
ansible-playbook -i inventory playbooks/final_audit_report.yml
```

### Perform Rollback

```bash
ansible-playbook -i inventory playbooks/perform_rollback.yml \
  -e rhel_stig_with_rollback_backup_name=pre_stig_hostname_20261102T120000
```

### Emergency Recovery (from AAP Controller)

```bash
ansible-playbook -i inventory playbooks/emergency_restore_from_controller.yml \
  -e target_host=hostname \
  -e backup_name=pre_stig_hostname_20261102T120000
```

## Project Structure

```
.
├── ansible.cfg                   # Ansible configuration
├── inventory                     # Default inventory
├── tailoring/                    # Organization-specific STIG variables
│   ├── README.md                 # Tailoring documentation
│   ├── example_tailoring.yml     # Example template
│   └── <org_name>/               # Your organization's profiles
│       ├── common.yml            # Variables for all RHEL versions
│       └── rhel{8,9,10}.yml     # Version-specific overrides
├── playbooks/                    # All playbooks
│   ├── rhel_stig_with_rollback.yml              # Main (AAP compatible)
│   ├── rhel_stig_with_rollback_interactive.yml  # Interactive CLI
│   ├── perform_rollback.yml                     # Rollback
│   ├── rhel_stig_audit_only.yml                 # Audit only
│   ├── final_audit_report.yml                   # Detailed audit
│   └── diagnose_stig_remediation.yml            # Diagnostics
├── roles/
│   └── rhel_stig_with_rollback/  # Main STIG role
│       ├── tasks/
│       │   ├── phase1_validation.yml       # Pre-flight checks
│       │   ├── phase2_backup.yml           # Backup creation
│       │   ├── phase3_baseline_audit.yml   # Audit (selective or full)
│       │   ├── phase4_remediation.yml      # Apply fixes
│       │   ├── phase5_verification.yml     # Operational checks
│       │   ├── phase6_summary.yml          # Final report
│       │   └── rollback.yml                # Rollback logic
│       ├── defaults/main.yml               # Default variables
│       └── handlers/main.yml               # Handlers
├── files/                        # Scripts and utilities
│   ├── parse_oscap_score.py                # Score parser
│   ├── parse_oscap_failures.py             # Failure categorizer
│   ├── filter_audit_results.py             # Selective audit filter
│   └── filter_remediation_playbook.py      # Selective remediation filter
├── docs/                         # Documentation
│   ├── AAP_COMPLETE_GUIDE.md               # AAP setup and usage
│   ├── SURVEY_CONFIGURATION.md             # Survey and selective STIG
│   ├── TROUBLESHOOTING.md                  # Problem solving
│   ├── DISASTER_RECOVERY.md                # Emergency recovery
│   ├── PLAYBOOK_REFERENCE.md               # All playbooks documented
│   ├── ROLE_DOCUMENTATION.md               # Role internals
│   └── aap_survey_configuration.json       # AAP survey template
├── group_vars/                   # Group variables
└── host_vars/                    # Host variables
```

## Workflow Phases

1. **Phase 1: Validation** - Check RHEL version, verify SCAP content
2. **Phase 2: Backup** - Create pre-hardening backup, copy to controller
3. **Phase 3: Baseline Audit** - Run OSCAP audit (selective or full)
4. **Phase 4: Remediation** - Generate and apply Ansible fixes (selective or full)
5. **Phase 5: Verification** - Test SSH, services, operational checks
6. **Phase 6: Summary** - Display results, rollback instructions

## Support

For issues or questions:
1. Check [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
2. Review playbook logs in `/opt/stig_work/`
3. Check audit reports in `/opt/stig_audit/`

## License

MIT
