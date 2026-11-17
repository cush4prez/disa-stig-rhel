# STIG Hardening Disaster Recovery Guide

## Critical Design: Controller-Based Backup

**Problem:** If STIG hardening breaks a system catastrophically (SSH lockout, PAM failure, boot issues), backups stored only on the managed node are inaccessible.

**Solution:** Backups are automatically fetched to the AAP controller during Phase 2, enabling recovery even when the managed node is completely broken.

## Backup Strategy

### Automatic Backup Flow (Default)

1. **Phase 2** - Role creates backup on managed node at `/opt/stig_backups/`
2. **Immediate fetch** - Backup is copied to AAP controller at `/var/lib/awx/projects/stig_backups/<hostname>/`
3. **Dual storage** - Backup exists in both locations for redundancy

### Configuration

```yaml
# Enable/disable fetching to controller (default: true)
rhel_stig_with_rollback_fetch_to_controller: true

# Controller backup directory (must be writable by awx user)
rhel_stig_with_rollback_controller_backup_dir: "/var/lib/awx/projects/stig_backups"
```

**Important:** The `awx` user must have write access to the controller backup directory.

## Recovery Scenarios

### Scenario 1: System Still Accessible (Automatic Rollback)

If the system passes operational checks but you want to rollback:

```bash
ansible-playbook playbooks/perform_rollback.yml -i inventory.ini -l <hostname>
```

This uses the backup **on the managed node** (fastest, no network transfer needed).

### Scenario 2: SSH Accessible But System Broken

If you can SSH but the system is misconfigured:

```bash
ansible-playbook playbooks/emergency_restore_from_controller.yml -i inventory.ini -l <hostname>
```

This **pushes the backup from AAP controller** to the managed node, then restores it.

You'll be prompted for the backup filename, e.g.:
```
pre_stig_rhel8-test_20261006T143022
```

### Scenario 3: SSH Completely Locked Out

If SSH is broken and you cannot connect via Ansible:

#### Option A: Console Access (iLO, iDRAC, VMware Console)

1. Boot into single-user/rescue mode
2. Mount filesystems
3. Manually copy backup from controller:
   ```bash
   scp root@<aap-controller>:/var/lib/awx/projects/stig_backups/<hostname>/<backup>.tar.gz /tmp/
   cd /tmp
   tar -xzf <backup>.tar.gz
   
   # Restore critical configs
   cp backup_*/config_files/etc/ssh/sshd_config /etc/ssh/sshd_config
   cp -a backup_*/config_files/etc/pam.d/* /etc/pam.d/
   cp backup_*/config_files/etc/sudoers /etc/sudoers
   
   systemctl restart sshd
   ```

4. Reboot normally
5. Once SSH works, run `emergency_restore_from_controller.yml` for complete restoration

#### Option B: Rebuild from Backup

If the system won't boot at all:

1. Rebuild/reinstall RHEL on the server
2. Restore SSH access with temporary config
3. Run `emergency_restore_from_controller.yml` to restore pre-STIG state
4. Investigate what went wrong before re-attempting STIG hardening

## Backup Retention

### On Managed Nodes

- Location: `/opt/stig_backups/`
- Retention: Manual cleanup required
- Purpose: Fast local rollback if system is still accessible

### On AAP Controller

- Location: `/var/lib/awx/projects/stig_backups/<hostname>/`
- Retention: Implement cleanup job or manual deletion
- Purpose: Disaster recovery when managed node is inaccessible

### Recommended Cleanup Strategy

Create a scheduled job in AAP to clean old backups:

```bash
# Delete backups older than 90 days
find /var/lib/awx/projects/stig_backups -name "*.tar.gz" -mtime +90 -delete
```

## Testing Recovery Procedures

### Test 1: Verify Backup Fetch

After running site.yml:

```bash
# On AAP controller
ls -lh /var/lib/awx/projects/stig_backups/*/

# Should show backup archives organized by hostname
```

### Test 2: Test Emergency Restore (Non-Destructive)

On a test system that was NOT hardened:

```bash
ansible-playbook playbooks/emergency_restore_from_controller.yml -i inventory.ini -l test-host
```

This verifies the restore mechanism works without breaking anything.

### Test 3: Simulate SSH Lockout

On a **disposable test VM only:**

1. Break SSH on purpose: `echo "DenyUsers *" >> /etc/ssh/sshd_config && systemctl restart sshd`
2. Verify you cannot SSH
3. Use console access to manually restore from controller backup
4. Verify SSH works again

## What Gets Backed Up

The backup includes:

- `/etc/passwd`, `/etc/shadow`, `/etc/group` - User accounts
- `/etc/sudoers` - Sudo configuration
- `/etc/ssh/sshd_config` - SSH daemon config
- `/etc/pam.d/*` - PAM authentication
- `/etc/login.defs` - Login policies
- `/etc/security/*` - Security settings
- `/etc/audit/*` - Audit configuration
- `/etc/sysctl.conf`, `/etc/sysctl.d/*` - Kernel parameters
- `/etc/selinux/*` - SELinux config
- `/etc/firewalld/*` - Firewall rules
- Enabled/running services list

## What Does NOT Get Backed Up

- User home directories
- Application data
- Database contents
- `/var/log/*` - Log files
- Package installations (RPMs)
- Boot loader configs (GRUB2)

## Emergency Contacts

Before running STIG hardening in production:

1. Document who has console access (iLO/iDRAC credentials)
2. Verify AAP controller backup directory has sufficient space
3. Test restore procedure on non-production systems
4. Have rollback window planned (late night/weekend)
5. Ensure backup team is available during hardening window

## Troubleshooting

### "Failed to fetch backup to controller"

**Cause:** AAP controller doesn't have write permission to backup directory

**Fix:**
```bash
# On AAP controller as root
mkdir -p /var/lib/awx/projects/stig_backups
chown awx:awx /var/lib/awx/projects/stig_backups
chmod 755 /var/lib/awx/projects/stig_backups
```

### "Backup file not found on controller"

**Cause:** Wrong hostname or backup wasn't fetched

**Fix:**
```bash
# On AAP controller
ls -R /var/lib/awx/projects/stig_backups/

# Use the exact filename shown
```

### "Cannot connect to managed node after restore"

**Cause:** Network config or firewall may have been altered

**Fix:** Use console access to check:
- `systemctl status sshd`
- `firewall-cmd --list-all`
- `ip addr show` (verify IP address)
- Check `/var/log/messages` for errors

## Disabling Controller Fetch (Not Recommended)

If you absolutely must disable controller backup fetch:

```yaml
# In group_vars/all.yml or job template extra vars
rhel_stig_with_rollback_fetch_to_controller: false
```

**Warning:** This removes your safety net. Only disable if:
- You have alternative backup solution (Veeam, Commvault, etc.)
- You're testing in disposable VMs
- You have console access and skilled team available 24/7
