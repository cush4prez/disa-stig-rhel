# Playbook Usage Guide

## Recommended Playbooks (Native Parsing Enabled)

These playbooks use the `rhel_stig_with_rollback` role which has **native Ansible XML parsing enabled by default**.

### ✅ Production Playbooks (Use These)

| Playbook | Use Case | Native Parsing |
|----------|----------|----------------|
| `site.yml` | Simplest - just calls the role | ✅ Yes (via role) |
| `rhel_stig_with_rollback_interactive.yml` | CLI with prompts | ✅ Yes (via role) |

**Recommendation**: Use `site.yml` for AAP deployments or `rhel_stig_with_rollback_interactive.yml` for CLI.

### ⚠️ Legacy Playbook (Not Recommended)

| Playbook | Status | Issue |
|----------|--------|-------|
| `rhel_stig_with_rollback.yml` | Legacy | Contains duplicate post_tasks with Python scripts |

**Issue**: This playbook calls the role (which uses native parsing) but then has 450 lines of duplicate post_tasks that re-implement all phases using Python scripts. This duplicates work and uses deprecated Python scripts.

**Solution**: Use `site.yml` or `rhel_stig_with_rollback_interactive.yml` instead.

## Quick Start

### For AAP Deployment

```bash
# Use site.yml playbook in your job template
Playbook: playbooks/site.yml
Survey: docs/aap_survey_configuration.json
```

### For CLI Deployment

```bash
# Interactive mode (prompts for configuration)
ansible-playbook -i inventory playbooks/rhel_stig_with_rollback_interactive.yml

# Or simple mode with extra vars
ansible-playbook -i inventory playbooks/site.yml \
  -e rhel_stig_with_rollback_tailoring_profile=myorg
```

## Verifying Native Parsing

To confirm native parsing is enabled:

```bash
# Check default value in role
grep "use_native_parsing" roles/rhel_stig_with_rollback/defaults/main.yml

# Output should show:
# rhel_stig_with_rollback_use_native_parsing: true
```

## Switching to Legacy Python Scripts

If you need to use Python scripts (not recommended):

```yaml
# group_vars/all.yml or extra vars
rhel_stig_with_rollback_use_native_parsing: false
```

## Playbook Comparison

### site.yml (Recommended)
- **Lines**: ~10
- **Approach**: Calls role
- **Parsing**: Native Ansible ✅
- **Maintainability**: Excellent
- **AAP Compatible**: Yes

### rhel_stig_with_rollback_interactive.yml (Recommended for CLI)
- **Lines**: ~120
- **Approach**: Prompts + calls role  
- **Parsing**: Native Ansible ✅
- **Maintainability**: Excellent
- **AAP Compatible**: No (prompts don't work in AAP)

### rhel_stig_with_rollback.yml (Legacy - Not Recommended)
- **Lines**: ~480
- **Approach**: Calls role + duplicate post_tasks
- **Parsing**: Role uses native, post_tasks use Python scripts ⚠️
- **Maintainability**: Poor (duplicate code)
- **AAP Compatible**: Yes, but not recommended

## Migration Path

If you're currently using `rhel_stig_with_rollback.yml`:

1. **Switch to `site.yml`**:
   ```bash
   # Change from:
   ansible-playbook playbooks/rhel_stig_with_rollback.yml
   
   # To:
   ansible-playbook playbooks/site.yml
   ```

2. **Update AAP job templates**:
   - Change playbook path from `rhel_stig_with_rollback.yml` to `site.yml`
   - Keep the same survey configuration

3. **Benefits**:
   - Native Ansible parsing (better security, easier maintenance)
   - Cleaner code (no duplicate logic)
   - Faster execution (role runs once, not twice)

## All Available Playbooks

See [PLAYBOOK_REFERENCE.md](PLAYBOOK_REFERENCE.md) for complete playbook documentation.

### By Use Case

**Initial Hardening**:
- `site.yml` ← Recommended
- `rhel_stig_with_rollback_interactive.yml` ← CLI alternative

**Audit Only**:
- `rhel_stig_audit_only.yml`

**Reporting**:
- `final_audit_report.yml`

**Rollback**:
- `perform_rollback.yml`

**Diagnostics**:
- `diagnose_stig_remediation.yml`
- `verify_system_operational.yml`

## Summary

✅ **DO**: Use `site.yml` or `rhel_stig_with_rollback_interactive.yml`

❌ **AVOID**: `rhel_stig_with_rollback.yml` (legacy with duplicate code)

Both recommended playbooks use the role which has **native Ansible parsing enabled by default**.
