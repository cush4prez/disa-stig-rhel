# RHEL 8 Compatibility Guide

## Overview

This role uses a **try-fallback pattern** to ensure compatibility across all RHEL versions (8, 9, 10) without always relying on shell commands.

## Key Strategy: Try Ansible Modules First

Instead of always using shell/command, the role:
1. **Tries** to use proper Ansible modules (community.general.archive, community.general.xml)
2. **Auto-installs** missing dependencies (python3-lxml)
3. **Falls back** to command-based alternatives only if modules fail

This means **RHEL 8 can still use native Ansible modules** if dependencies are available!

## What Was the Real Issue?

**Not Python 3.6!** The issue was missing dependencies:
- `community.general.archive` - Works fine on Python 3.6
- `community.general.xml` - Requires `python3-lxml` library

Once `python3-lxml` is installed, native Ansible parsing works perfectly on RHEL 8!

## Try-Fallback Pattern

### Backup Creation

```yaml
- name: Create compressed backup
  block:
    # Try the proper Ansible way first
    - community.general.archive:
        path: /path/to/backup
        dest: /path/to/backup.tar.gz
      register: archive_result
      failed_when: false

    # Only use tar if module failed
    - ansible.builtin.command: tar czf ...
      when: archive_result is failed
      creates: /path/to/backup.tar.gz  # Makes it idempotent
```

**Benefits**:
- ✅ Uses Ansible module when it works (RHEL 8 included!)
- ✅ Automatic fallback on problematic systems
- ✅ Uses `command` module (safer than `shell`)
- ✅ Idempotent with `creates` parameter

### XML Parsing

```yaml
# Phase 1: Ensure dependencies
- Check if lxml available: python3 -c "import lxml.etree"
- If missing: Install python3-lxml package  
- If install succeeds: Use native Ansible parsing
- If install fails: Fall back to Python scripts
```

**Benefits**:
- ✅ Tries to enable native parsing on all systems
- ✅ Works on Python 3.6+ with lxml
- ✅ Automatic fallback if lxml can't be installed

## Configuration

### Default (Recommended)

```yaml
rhel_stig_with_rollback_use_native_parsing: true
rhel_stig_with_rollback_auto_detect_python: true
rhel_stig_with_rollback_auto_install_deps: true
```

**Behavior**: Tries to install lxml, uses native parsing if available, falls back if needed

### Don't Auto-Install Dependencies

```yaml
rhel_stig_with_rollback_auto_install_deps: false
```

**Behavior**: Checks for lxml, uses native parsing if present, falls back if missing

### Force Python Scripts

```yaml
rhel_stig_with_rollback_use_native_parsing: false
```

**Behavior**: Always uses Python scripts, skips all checks

## Expected Behavior by RHEL Version

### RHEL 8 (Python 3.6)
1. Check lxml → Usually missing
2. **Install python3-lxml** → Usually succeeds
3. Use native Ansible parsing ✅

Only falls back to Python scripts if lxml install fails.

### RHEL 9/10 (Python 3.9+)
1. Check lxml → Usually installed
2. Use native Ansible parsing ✅

## Why This Is Better Than Shell

| Aspect | Shell-Only | Try-Fallback |
|--------|-----------|--------------|
| Uses Ansible modules | ❌ Never | ✅ When available |
| Security | ⚠️ Shell execution | ✅ Module or command |
| Idempotency | Manual | ✅ Built-in |
| Works RHEL 8 | ✅ Yes | ✅ Yes (better!) |
| Works RHEL 9+ | ✅ Yes | ✅ Yes (optimal!) |

## Testing

### RHEL 8 Without lxml

```bash
ansible-playbook -i rhel8 playbooks/site.yml
```

**Expected**:
- Detects missing lxml
- Installs python3-lxml
- Uses native Ansible parsing ✅

### RHEL 8 With Auto-Install Disabled

```bash
ansible-playbook -i rhel8 playbooks/site.yml \
  -e rhel_stig_with_rollback_auto_install_deps=false
```

**Expected**:
- Detects missing lxml
- Does not install
- Falls back to Python scripts

### Verify Which Method Was Used

During playbook run, look for:

```
TASK [Display parsing method]
ok: [rhel8] =>
  msg: 'Parsing method: Native Ansible (community.general.xml)'
```

or

```
ok: [rhel8] =>
  msg: 'Parsing method: Python scripts (legacy)'
```

## Troubleshooting

### Backup Creation Fails

**Symptom**: "Create compressed backup archive" task fails

**Solution**: The try-fallback pattern handles this automatically. Check if both module AND command failed.

### lxml Auto-Install Fails

**Symptom**: Warning about lxml not available

**Solution**: Manually install:
```bash
dnf install python3-lxml
```

Then re-run the playbook.

### Force Use of Ansible Modules

If you want to ensure modules are used (fail if they don't work):

```yaml
rhel_stig_with_rollback_auto_detect_python: false
```

This will fail instead of falling back, helping you identify dependency issues.

## Summary

- ✅ No shell module needed
- ✅ Tries proper Ansible modules first
- ✅ Auto-installs dependencies (lxml)
- ✅ Automatic fallback if needed
- ✅ Works on all Python 3.6+ versions
- ✅ More secure than shell-based approach
- ✅ Better Ansible practices

**The key insight**: The issue was missing `python3-lxml`, not Python version!
