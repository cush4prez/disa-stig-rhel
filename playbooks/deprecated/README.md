# Deprecated Playbooks

⚠️ **These playbooks are deprecated and will be removed in a future release.**

## Why Deprecated?

These playbooks were designed for DISA STIG only. The repository now supports multiple security benchmarks (DISA STIG, CIS L1/L2, custom profiles), and these have been replaced by benchmark-agnostic versions.

## Migration Guide

| Deprecated Playbook | New Playbook | Notes |
|---------------------|--------------|-------|
| `rhel_stig_with_rollback.yml` | `rhel_benchmark_hardening.yml` | Same functionality, supports all benchmarks |
| `rhel_stig_with_rollback_interactive.yml` | `rhel_benchmark_hardening_interactive.yml` | Now includes benchmark selection prompt |
| `rhel_stig_audit_only.yml` | `rhel_benchmark_audit_only.yml` | Works with any benchmark |
| `rhel_stig_query.yml` | `rhel_benchmark_rule_query.yml` | Query rules from any benchmark |
| `rhel_stig_verification.yml` | `rhel_benchmark_verification.yml` | Verify any benchmark |
| `rhel_stig_backup_state.yml` | `rhel_system_backup_state.yml` | Generic system backup (not benchmark-specific) |

## How to Migrate

### Simple Replacement

The easiest migration is to simply replace the old playbook name with the new one:

**Before**:
```bash
ansible-playbook -i inventory playbooks/rhel_stig_with_rollback.yml
```

**After**:
```bash
ansible-playbook -i inventory playbooks/rhel_benchmark_hardening.yml
```

By default, this will use DISA STIG (same as before), so your existing workflows continue to work.

### Using CIS Benchmarks

To switch to CIS Server Level 1:

```bash
ansible-playbook -i inventory playbooks/rhel_benchmark_hardening.yml \
  -e rhel_stig_with_rollback_benchmark_profile=cis_server_l1
```

### Updating AAP Job Templates

1. Edit job template
2. Change **Playbook** from `playbooks/rhel_stig_with_rollback.yml` to `playbooks/rhel_benchmark_hardening.yml`
3. Add 6th survey question for benchmark profile selection (see `docs/aap/AAP_SURVEY_CONFIGURATION.md`)
4. Save and test

### Variable Compatibility

All existing variables continue to work:
- `rhel_stig_with_rollback_apply_remediations`
- `rhel_stig_with_rollback_auto_rollback_on_failure`
- `rhel_stig_with_rollback_stig_rules_to_apply`
- `rhel_stig_with_rollback_tailoring_profile`

New variable for benchmark selection:
- `rhel_stig_with_rollback_benchmark_profile` (default: `stig`)

## Timeline

- **Current**: Deprecated playbooks remain functional with warnings
- **6 months**: Deprecation notices in all documentation
- **12 months**: Deprecated playbooks removed from repository

## Need Help?

See:
- `docs/guides/BENCHMARK_GUIDE.md` - Multi-benchmark usage guide
- `docs/operations/MIGRATION_GUIDE.md` - Complete migration guide
- `docs/aap/AAP_COMPLETE_GUIDE.md` - AAP migration steps
