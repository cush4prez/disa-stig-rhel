# Troubleshooting Guide

Complete troubleshooting guide for RHEL DISA STIG hardening.

## Table of Contents

- [Common Issues](#common-issues)
- [Phase-Specific Issues](#phase-specific-issues)
- [Selective STIG Issues](#selective-stig-issues)
- [Rollback Issues](#rollback-issues)
- [AAP-Specific Issues](#aap-specific-issues)
- [Emergency Recovery](#emergency-recovery)
- [Diagnostic Tools](#diagnostic-tools)

---

## Common Issues

### Issue: Host Unreachable After Hardening

**Symptoms:**
```
UNREACHABLE! => {
    "msg": "Failed to connect to the host via ssh"
}
```

**Causes:**
- SSH configuration changed by STIG rules
- Firewall rules blocking SSH
- SELinux denying SSH access
- Service stopped during remediation

**Solutions:**

1. **Access via console** (physical, IPMI, or cloud console)

2. **Check SSH service:**
   ```bash
   systemctl status sshd
   systemctl start sshd
   ```

3. **Check firewall:**
   ```bash
   firewall-cmd --list-all
   firewall-cmd --add-service=ssh --permanent
   firewall-cmd --reload
   ```

4. **Check SELinux:**
   ```bash
   ausearch -m avc -ts recent
   setenforce 0  # Temporarily if needed
   ```

5. **Restore SSH config from backup:**
   ```bash
   cp /opt/stig_backups/backup_*/config_files/etc/ssh/sshd_config /etc/ssh/
   systemctl restart sshd
   ```

6. **Full rollback:**
   ```bash
   ansible-playbook -i inventory playbooks/perform_rollback.yml \
     -e rhel_stig_with_rollback_backup_name=pre_stig_hostname_TIMESTAMP
   ```

---

### Issue: No Compliance Improvement After Hardening

**Symptoms:**
```
Baseline Compliance    : 54%
Post-Hardening Compliance : 54%
Compliance Improvement    : +0.0%
```

**Causes:**
- Remediation script didn't actually apply fixes
- STIG rules require manual intervention
- Conflicting rules
- System limitations prevent compliance

**Solutions:**

1. **Check remediation log:**
   ```bash
   cat /opt/stig_work/remediation_*.log
   ```

2. **Verify remediation was executed:**
   ```bash
   # Check if remediation file exists and has content
   ls -lh /opt/stig_work/remediation_*.yml
   ```

3. **Review failed rules:**
   ```bash
   ansible-playbook -i inventory playbooks/final_audit_report.yml
   ```

4. **Check for errors in specific rules:**
   ```bash
   # Look for rule-specific failures
   grep -i "error\|failed" /opt/stig_work/remediation_*.log
   ```

5. **Try selective remediation on specific failing rules:**
   ```yaml
   rhel_stig_with_rollback_stig_rules_to_apply:
     - rule_that_failed_1
     - rule_that_failed_2
   ```

---

### Issue: Remediation Script Empty or Not Generated

**Symptoms:**
```
FAILED! => {
    "msg": "Remediation script was not generated or is empty"
}
```

**Causes:**
- SCAP content missing or corrupted
- Profile ID incorrect
- OSCAP tool failure

**Solutions:**

1. **Verify SCAP content exists:**
   ```bash
   ls -lh /usr/share/xml/scap/ssg/content/ssg-rhel*.xml
   ```

2. **Reinstall SCAP packages:**
   ```bash
   dnf reinstall openscap-scanner scap-security-guide
   ```

3. **Test OSCAP manually:**
   ```bash
   oscap info /usr/share/xml/scap/ssg/content/ssg-rhel8-ds.xml
   ```

4. **Generate fix manually to test:**
   ```bash
   oscap xccdf generate fix \
     --fix-type ansible \
     --profile xccdf_org.ssgproject.content_profile_stig \
     /usr/share/xml/scap/ssg/content/ssg-rhel8-ds.xml
   ```

---

## Phase-Specific Issues

### Phase 1: Validation Failures

**Issue: Unsupported RHEL version**

```
FAILED! => {
    "msg": "This playbook supports RHEL 8, 9, and 10 only"
}
```

**Solution:**
- Verify RHEL version: `cat /etc/redhat-release`
- This playbook only supports RHEL 8, 9, and 10

---

### Phase 2: Backup Failures

**Issue: Insufficient disk space for backup**

```
FAILED! => {
    "msg": "No space left on device"
}
```

**Solution:**

1. **Check disk space:**
   ```bash
   df -h /opt/stig_backups
   ```

2. **Clean old backups:**
   ```bash
   find /opt/stig_backups -name "*.tar.gz" -mtime +30 -delete
   ```

3. **Use different backup location:**
   ```yaml
   rhel_stig_with_rollback_backup_root: /mnt/large_volume/stig_backups
   ```

---

### Phase 3: Audit Failures

**Issue: OSCAP scan hangs or times out**

**Solution:**

1. **Check system resources:**
   ```bash
   top
   free -h
   ```

2. **Kill hung OSCAP process:**
   ```bash
   pkill -9 oscap
   ```

3. **Reduce audit scope (use selective mode):**
   ```yaml
   rhel_stig_with_rollback_stig_rules_to_apply:
     - sysctl_crypto_fips_enabled
     # Add only rules you care about
   ```

---

### Phase 4: Remediation Failures

**Issue: Remediation applies but services fail**

**Symptoms:**
```
TASK [Execute remediation playbook] ****************************
fatal: [host]: FAILED! => {
    "msg": "service failed to start"
}
```

**Solution:**

1. **Check which service failed:**
   ```bash
   systemctl list-units --failed
   ```

2. **Review service logs:**
   ```bash
   journalctl -xe -u <service-name>
   ```

3. **Check remediation log for details:**
   ```bash
   grep -A 10 "FAILED" /opt/stig_work/remediation_*.log
   ```

4. **Manual service recovery:**
   ```bash
   systemctl status <service>
   systemctl restart <service>
   ```

---

### Phase 5: Verification Failures

**Issue: Operational check fails**

```
❌ SYSTEM IS INOPERABLE

Critical failures detected:
  • SSH connectivity test failed
  • NetworkManager is not running
```

**Solution:**

1. **Auto-rollback should trigger** if enabled
2. If not, **manual rollback:**
   ```bash
   ansible-playbook -i inventory playbooks/perform_rollback.yml
   ```

3. **Check specific failures:**
   ```bash
   # SSH
   systemctl status sshd
   
   # Network
   systemctl status NetworkManager
   
   # Firewall
   systemctl status firewalld
   ```

---

## Selective STIG Issues

### Issue: Rules Not Found in Audit

**Symptoms:**
```
⚠️  WARNING: Some requested rules were not found:
  - sysctl_crypto_fips_enabled2
  - invalid_rule_name
```

**Causes:**
- Typo in rule ID
- Rule doesn't exist in SCAP content
- Wrong SCAP content version

**Solutions:**

1. **List available rules:**
   ```bash
   oscap info /usr/share/xml/scap/ssg/content/ssg-rhel8-ds.xml | grep -i "rule.*crypto"
   ```

2. **Use correct short ID format:**
   - ✅ Correct: `sysctl_crypto_fips_enabled`
   - ❌ Wrong: `xccdf_org.ssgproject.content_rule_sysctl_crypto_fips_enabled`
   - ❌ Wrong: `sysctl_crypto_fips_enabled2` (typo)

3. **Run audit-only first to find valid rule IDs:**
   ```bash
   ansible-playbook -i inventory playbooks/final_audit_report.yml
   ```

---

### Issue: Selective Audit Shows 0 Failed Rules

**Symptoms:**
```
FAILED RULES (will be remediated):

✅ All selected rules passed!
```

**Meaning:**
- This is **NOT an error**
- Your selected rules are already compliant
- No remediation needed

**Actions:**
- If you expected failures, verify you selected the right rules
- Run full audit to find other failing rules
- Consider this a success!

---

### Issue: Filtered Remediation Playbook is Empty

**Symptoms:**
```
❌ ERROR: No matching tasks found!
This likely means the rule IDs don't match the playbook.
```

**Causes:**
- Rule IDs don't match generated remediation playbook
- OSCAP didn't generate tasks for those rules
- Rule IDs in audit don't match remediation format

**Solutions:**

1. **Check remediation playbook content:**
   ```bash
   less /opt/stig_work/remediation_*.yml
   ```

2. **Verify rules exist in full remediation:**
   ```bash
   grep -i "sysctl_crypto" /opt/stig_work/remediation_*.yml
   ```

3. **Try full remediation mode instead:**
   ```yaml
   rhel_stig_with_rollback_stig_rules_to_apply: []  # Empty = full mode
   ```

---

## Rollback Issues

### Issue: Rollback Fails - Backup Not Found

**Symptoms:**
```
FAILED! => {
    "msg": "Backup file not found"
}
```

**Solutions:**

1. **List available backups:**
   ```bash
   ls -lh /opt/stig_backups/
   ```

2. **Check backup name format:**
   ```
   Correct: pre_stig_hostname_20261102T120000
   Find: ls /opt/stig_backups/pre_stig_*
   ```

3. **Restore from controller backup:**
   ```bash
   ansible-playbook -i inventory playbooks/emergency_restore_from_controller.yml \
     -e target_host=hostname \
     -e backup_name=pre_stig_hostname_TIMESTAMP
   ```

4. **Manual restore:**
   ```bash
   cd /opt/stig_backups
   tar -xzf pre_stig_*.tar.gz
   # Manually restore critical files
   ```

---

### Issue: Partial Rollback - Some Services Still Broken

**Symptoms:**
- Rollback completes but services still failing
- SSH works but other services broken

**Solutions:**

1. **Restore specific services manually:**
   ```bash
   # Restore service config
   cp /opt/stig_backups/backup_*/config_files/etc/systemd/* /etc/systemd/
   systemctl daemon-reload
   systemctl restart <service>
   ```

2. **Restore from enabled services list:**
   ```bash
   cat /opt/stig_backups/backup_*/enabled_services.txt
   # Enable each service
   systemctl enable <service>
   ```

3. **Check rollback log:**
   ```bash
   grep -i "error\|failed" /var/log/ansible.log
   ```

---

## AAP-Specific Issues

### Issue: Survey Not Showing in AAP

**Symptoms:**
- Job template launches without survey prompts

**Solutions:**

1. **Verify survey is enabled:**
   - Edit job template
   - Check **Survey Enabled** toggle is ON

2. **Re-import survey:**
   - Survey tab → Delete existing
   - Import from `docs/aap_survey_configuration.json`

3. **Check variable names are exact:**
   - Must be exactly: `stig_audit_mode`, `stig_rules_input`, etc.
   - Case-sensitive

---

### Issue: Job Fails to Find Role

**Symptoms:**
```
ERROR! The role 'rhel_stig_with_rollback' was not found
```

**Solutions:**

1. **Sync project:**
   - Resources → Projects → [Your Project] → Sync

2. **Verify project structure:**
   ```bash
   # On AAP controller
   ls /var/lib/awx/projects/[project_id]/roles/rhel_stig_with_rollback
   ```

3. **Check playbook path:**
   - Must be: `playbooks/rhel_stig_with_rollback.yml`
   - Not: `rhel_stig_with_rollback.yml`

---

### Issue: Backup Not Copied to Controller

**Symptoms:**
- Backup created on target but not on controller

**Solutions:**

1. **Check controller backup directory exists:**
   ```bash
   mkdir -p /var/lib/awx/projects/stig_backups
   chown awx:awx /var/lib/awx/projects/stig_backups
   ```

2. **Verify fetch_to_controller is enabled:**
   ```yaml
   rhel_stig_with_rollback_fetch_to_controller: true
   ```

3. **Check controller disk space:**
   ```bash
   df -h /var/lib/awx
   ```

---

## Emergency Recovery

### Scenario: Complete System Lockout

**Symptoms:**
- Cannot SSH to host
- AAP jobs fail with "unreachable"
- Console shows system booted but inaccessible

**Recovery Steps:**

1. **Access via console** (physical, IPMI, KVM, cloud console)

2. **Check SSH is running:**
   ```bash
   systemctl status sshd
   systemctl start sshd
   ```

3. **Check SSH config:**
   ```bash
   sshd -t  # Test config
   cat /etc/ssh/sshd_config | grep -i "^PermitRoot\|^PasswordAuth"
   ```

4. **Restore SSH from backup:**
   ```bash
   cp /opt/stig_backups/backup_*/config_files/etc/ssh/sshd_config /etc/ssh/
   systemctl restart sshd
   ```

5. **Test SSH connection:**
   ```bash
   # From another host
   ssh -v username@hostname
   ```

6. **Full rollback once SSH works:**
   ```bash
   ansible-playbook -i inventory playbooks/perform_rollback.yml \
     -e rhel_stig_with_rollback_backup_name=pre_stig_hostname_TIMESTAMP
   ```

---

### Scenario: Rollback Playbook Won't Run

**If you cannot run Ansible playbooks:**

1. **Manual restoration:**
   ```bash
   # On target host via console
   cd /opt/stig_backups
   tar -xzf pre_stig_*.tar.gz
   
   # Restore SSH
   cp backup_*/config_files/etc/ssh/sshd_config /etc/ssh/
   systemctl restart sshd
   
   # Restore firewall
   cp -r backup_*/config_files/etc/firewalld/* /etc/firewalld/
   systemctl restart firewalld
   
   # Restore SELinux
   cp backup_*/config_files/etc/selinux/config /etc/selinux/
   
   # Restore sysctl
   cp backup_*/config_files/etc/sysctl.conf /etc/
   sysctl -p
   ```

2. **Verify critical services:**
   ```bash
   systemctl status sshd NetworkManager firewalld
   ```

---

## Diagnostic Tools

### Run Full Diagnostic

```bash
ansible-playbook -i inventory playbooks/full_diagnostic.yml
```

This checks:
- OSCAP installation
- SCAP content availability
- Backup status
- Audit reports
- Remediation logs
- Service status

### Check STIG Remediation Status

```bash
ansible-playbook -i inventory playbooks/diagnose_stig_remediation.yml
```

Shows:
- What was remediated
- What failed
- Current compliance state

### Verify System Operational

```bash
ansible-playbook -i inventory playbooks/verify_system_operational.yml
```

Tests:
- SSH connectivity
- Critical services
- Network connectivity
- Firewall status

---

## Log Locations

| Log Type | Location | Description |
|----------|----------|-------------|
| Audit Results | `/opt/stig_audit/baseline_*.xml` | OSCAP audit output |
| Audit Reports | `/opt/stig_audit/*.html` | Human-readable reports |
| Remediation Logs | `/opt/stig_work/remediation_*.log` | Remediation execution log |
| Remediation Scripts | `/opt/stig_work/remediation_*.yml` | Generated Ansible playbooks |
| Backups | `/opt/stig_backups/` | Pre-hardening backups |
| Rollback Instructions | `/opt/stig_backups/ROLLBACK_INSTRUCTIONS.txt` | Recovery procedures |
| Controller Backups | `/var/lib/awx/projects/stig_backups/` | AAP backup copies |

---

## Getting Help

If issues persist:

1. **Collect diagnostic information:**
   ```bash
   # Run diagnostic playbook
   ansible-playbook -i inventory playbooks/full_diagnostic.yml > diagnostic.log
   
   # Collect logs
   tar -czf stig_logs.tar.gz /opt/stig_audit/ /opt/stig_work/ /opt/stig_backups/*.txt
   ```

2. **Check documentation:**
   - [SURVEY_CONFIGURATION.md](SURVEY_CONFIGURATION.md) - Selective STIG and survey help
   - [AAP_COMPLETE_GUIDE.md](AAP_COMPLETE_GUIDE.md) - AAP setup and usage
   - [DISASTER_RECOVERY.md](DISASTER_RECOVERY.md) - Emergency procedures

3. **Review playbook output:**
   - AAP: Check job output in GUI
   - CLI: Review console output and logs
