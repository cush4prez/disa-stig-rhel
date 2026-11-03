# RHEL DISA STIG Hardening with Rollback

Ansible automation for applying DISA STIG hardening to RHEL 8/9/10 systems with intelligent rollback protection and selective audit capabilities.

## Features

- ✅ **Selective or Full STIG Auditing** - Audit specific rules or all rules
- ✅ **Ansible-based Remediation** - Native Ansible tasks (not bash scripts)
- ✅ **Organization Tailoring** - Customize STIG variables for your organization
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

### Option 2: Using the Role

```bash
ansible-playbook -i inventory playbooks/rhel_stig_with_rollback.yml
```

Or create your own playbook:

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

### Option 3: Ansible Automation Platform (AAP 2.7)

1. **Create Project** pointing to this repository
2. **Import Survey** from `docs/aap_survey_configuration.json`
3. **Create Job Template** with `playbooks/rhel_stig_with_rollback.yml`
4. **Enable Survey** on the job template
5. **Launch** and fill out the survey form

See [docs/AAP_COMPLETE_GUIDE.md](docs/AAP_COMPLETE_GUIDE.md) for detailed instructions.

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
- **[TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[DISASTER_RECOVERY.md](docs/DISASTER_RECOVERY.md)** - Emergency recovery procedures

### Reference Guides

- **[PLAYBOOK_REFERENCE.md](docs/PLAYBOOK_REFERENCE.md)** - Complete playbook descriptions
- **[ROLE_DOCUMENTATION.md](docs/ROLE_DOCUMENTATION.md)** - Role architecture and phases

## Requirements

- RHEL 8, 9, or 10
- openscap-scanner
- scap-security-guide
- Ansible 2.9+
- Python 3.6+

The role automatically installs missing SCAP packages.

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
