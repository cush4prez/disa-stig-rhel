# Playbooks

This directory contains all playbooks for RHEL security benchmark hardening (DISA STIG, CIS, custom profiles).

## Quick Reference

| Playbook | Purpose | Use Case |
|----------|---------|----------|
| **`site.yml`** ⭐ | **Main entry point** | **Recommended for all deployments** |
| `rhel_benchmark_hardening.yml` | Full hardening workflow | Production hardening with AAP survey |
| `rhel_benchmark_hardening_interactive.yml` | Interactive CLI | CLI deployment with prompts |
| `rhel_benchmark_audit_only.yml` | Audit without remediation | Compliance reporting only |
| `rhel_benchmark_verification.yml` | Verify compliance | Post-hardening validation |
| `rhel_benchmark_rule_query.yml` | Query specific rules | Check status of individual rules |
| `rhel_system_backup_state.yml` | Create system backup | Backup before manual changes |
| `final_audit_report.yml` | Detailed compliance report | CAT I/II/III breakdown |
| `perform_rollback.yml` | Emergency rollback | Restore from backup |
| `emergency_restore_from_controller.yml` | Restore from AAP | Disaster recovery |
| `test_tailoring.yml` | Test tailoring files | Validate org-specific configs |

## Directory Structure

```
playbooks/
├── *.yml                  Production playbooks (main directory)
├── deprecated/            Legacy STIG-only playbooks (use new versions)
├── diagnostics/           Troubleshooting and diagnostic tools
├── tests/                 Development test playbooks
└── examples/              Example playbooks for different benchmarks
```

## Getting Started

### Option 1: Recommended - Use site.yml

```bash
# DISA STIG (default)
ansible-playbook -i inventory playbooks/site.yml

# CIS Server Level 1
ansible-playbook -i inventory playbooks/site.yml \
  -e rhel_stig_with_rollback_benchmark_profile=cis_server_l1

# CIS Server Level 2
ansible-playbook -i inventory playbooks/site.yml \
  -e rhel_stig_with_rollback_benchmark_profile=cis_server_l2
```

### Option 2: Interactive Mode

```bash
ansible-playbook -i inventory playbooks/rhel_benchmark_hardening_interactive.yml
```

Prompts for:
- Benchmark selection (STIG, CIS L1/L2, custom)
- Audit mode (full or selective)
- Remediation options
- Rollback settings

### Option 3: Ansible Automation Platform (AAP)

Use `site.yml` or `rhel_benchmark_hardening.yml` with survey configuration.

See: `docs/aap/AAP_COMPLETE_GUIDE.md`

## Workflow Playbooks

### Full Hardening
**`rhel_benchmark_hardening.yml`** or **`site.yml`**
- Validates system
- Creates backup
- Runs baseline audit
- Applies remediations (if enabled)
- Verifies system operational
- Reports results

### Audit Only
**`rhel_benchmark_audit_only.yml`**
- No system changes
- Generates compliance report
- Safe to run in production

### Verification
**`rhel_benchmark_verification.yml`**
- Checks current compliance
- Verifies remediations applied
- Generates audit report

### Rollback
**`perform_rollback.yml`**
- Restores from backup
- Reverts all changes
- Emergency recovery

## Benchmark Selection

All benchmark-aware playbooks support:

- **`stig`** - DISA STIG (default)
- **`cis_server_l1`** - CIS Server Level 1
- **`cis_server_l2`** - CIS Server Level 2  
- **`cis_workstation_l1`** - CIS Workstation Level 1
- **`cis_workstation_l2`** - CIS Workstation Level 2
- **`cis`** - CIS General Benchmark
- **`custom`** - Custom SCAP profile (specify profile ID)

Set via: `-e rhel_stig_with_rollback_benchmark_profile=<profile>`

## Subdirectories

### deprecated/
**Legacy STIG-only playbooks** - Replaced by benchmark-agnostic versions.

⚠️ These will be removed in future release. See `deprecated/README.md` for migration guide.

### diagnostics/
**Troubleshooting playbooks** - Help diagnose scoring, remediation, and compliance issues.

Use when: Unexpected results, debugging needed, issue investigation.

See: `diagnostics/README.md`

### tests/
**Development test playbooks** - For testing role functionality during development.

⚠️ Not for production use. See: `tests/README.md`

### examples/
**Example playbooks** - Show how to use different benchmarks and configurations.

Learn by example. Copy and adapt for your needs.

See: `examples/README.md`

## Common Patterns

### Selective Remediation

Apply only specific rules:

```bash
ansible-playbook -i inventory playbooks/site.yml \
  -e rhel_stig_with_rollback_benchmark_profile=cis_server_l1 \
  -e "rhel_stig_with_rollback_stig_rules_to_apply=['service_auditd_enabled','package_aide_installed']"
```

### Organization Tailoring

Use custom security control values:

```bash
ansible-playbook -i inventory playbooks/site.yml \
  -e rhel_stig_with_rollback_tailoring_profile=myorg
```

See: `docs/guides/TAILORING_GUIDE.md`

### Audit-Only First

Always audit before remediating:

```bash
# Step 1: Audit only
ansible-playbook -i inventory playbooks/rhel_benchmark_audit_only.yml

# Step 2: Review report in /opt/stig_audit/

# Step 3: Apply if satisfied
ansible-playbook -i inventory playbooks/site.yml
```

## Documentation

- **Quick Start**: `docs/getting-started/QUICK_START.md`
- **Benchmark Guide**: `docs/guides/BENCHMARK_GUIDE.md`
- **Playbook Reference**: `docs/reference/PLAYBOOK_REFERENCE.md`
- **AAP Setup**: `docs/aap/AAP_COMPLETE_GUIDE.md`
- **Troubleshooting**: `docs/operations/TROUBLESHOOTING.md`

## Need Help?

1. Check `docs/operations/TROUBLESHOOTING.md`
2. Run diagnostic playbooks in `diagnostics/`
3. Review examples in `examples/`
4. See full documentation in `docs/`
