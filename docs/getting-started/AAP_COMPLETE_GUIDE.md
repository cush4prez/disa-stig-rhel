# Ansible Automation Platform (AAP) 2.7 - Complete Setup Guide

Complete guide for deploying RHEL DISA STIG hardening using Ansible Automation Platform 2.7.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Step 1: Create Execution Environment](#step-1-create-execution-environment)
- [Step 2: Create Project](#step-2-create-project)
- [Step 3: Create Inventory](#step-3-create-inventory)
- [Step 4: Create Job Templates](#step-4-create-job-templates)
- [Step 5: Configure Surveys](#step-5-configure-surveys)
- [Running Jobs](#running-jobs)
- [Monitoring and Results](#monitoring-and-results)
- [Emergency Recovery](#emergency-recovery)
- [Troubleshooting](#troubleshooting)

---

## Overview

This role is fully compatible with AAP 2.7 and provides:

- ✅ Survey-based GUI configuration
- ✅ Selective or full STIG auditing
- ✅ Automatic backup with disaster recovery
- ✅ Intelligent auto-rollback on failures
- ✅ RHEL 8, 9, and 10 support
- ✅ Native Ansible parsing (no Python scripts)

---

## Prerequisites

### Required

- **AAP 2.6 or later** installed and operational
- **Git repository** containing this project
- **RHEL hosts** to harden (RHEL 8, 9, or 10)
- **Credentials** with sudo/root access to target hosts
- **RHEL 8 hosts** have python 3.9 or later

### Recommended

- **Red Hat Satellite** or **RHEL subscription** for SCAP content
- **Backup storage** on AAP controller: `/var/lib/awx/projects/stig_backups/`

---

## Step 1: Create Execution Environment

The role requires `community.general` collection version 8.0.0+ and `python3-lxml` on target hosts.

### Option A: Use Existing EE (if it has community.general 8.0+)

Check your execution environment:

1. **Administration → Execution Environments**
2. Verify one includes `community.general >= 8.0.0`
3. Note the name for later use

### Option B: Create Custom EE

If your existing execution environments don't have `community.general >= 8.0.0`, build a custom one.

#### Prerequisites for Building EE

Install ansible-builder on your workstation:

```bash
# RHEL/CentOS
sudo dnf install ansible-builder podman

# Or via pip
pip install ansible-builder
```

#### Step B.1: Create EE Definition Files

Create a directory for your execution environment:

```bash
mkdir -p ~/rhel-stig-ee
cd ~/rhel-stig-ee
```

Create `execution-environment.yml`:

```yaml
---
version: 3

images:
  base_image:
    name: registry.redhat.io/ansible-automation-platform-24/ee-minimal-rhel9:latest

dependencies:
  galaxy: requirements.yml
  python:
    - python3-lxml

additional_build_steps:
  append_final:
    - RUN microdnf install -y python3-lxml && microdnf clean all
```

Create `requirements.yml`:

```yaml
---
collections:
  - name: community.general
    version: ">=8.0.0"
  - name: ansible.posix
    version: ">=1.3.0"
```

#### Step B.2: Build the Execution Environment

Build the container image:

```bash
# Build with podman (default)
ansible-builder build --tag rhel-stig-ee:1.0.0 --container-runtime podman

# Or with docker
ansible-builder build --tag rhel-stig-ee:1.0.0 --container-runtime docker
```

This creates:
- `context/` directory with build files
- Container image `rhel-stig-ee:1.0.0`

Verify the image:

```bash
podman images | grep rhel-stig-ee
# or
docker images | grep rhel-stig-ee
```

#### Step B.3: Push to Container Registry

**Option 1: Red Hat Quay.io**

```bash
# Login
podman login quay.io

# Tag for registry
podman tag rhel-stig-ee:1.0.0 quay.io/your-org/rhel-stig-ee:1.0.0
podman tag rhel-stig-ee:1.0.0 quay.io/your-org/rhel-stig-ee:latest

# Push
podman push quay.io/your-org/rhel-stig-ee:1.0.0
podman push quay.io/your-org/rhel-stig-ee:latest
```

**Option 2: Private Registry**

```bash
# Login
podman login your-registry.example.com

# Tag
podman tag rhel-stig-ee:1.0.0 your-registry.example.com/rhel-stig-ee:1.0.0
podman tag rhel-stig-ee:1.0.0 your-registry.example.com/rhel-stig-ee:latest

# Push
podman push your-registry.example.com/rhel-stig-ee:1.0.0
podman push your-registry.example.com/rhel-stig-ee:latest
```

**Option 3: AAP Private Automation Hub**

```bash
# Login to your Automation Hub
podman login hub.example.com

# Tag
podman tag rhel-stig-ee:1.0.0 hub.example.com/rhel-stig-ee:1.0.0
podman tag rhel-stig-ee:1.0.0 hub.example.com/rhel-stig-ee:latest

# Push
podman push hub.example.com/rhel-stig-ee:1.0.0
podman push hub.example.com/rhel-stig-ee:latest
```

#### Step B.4: Add Registry Credential in AAP (if private registry)

If using a private registry:

1. **Resources → Credentials → Add**
2. **Name**: `Container Registry - RHEL STIG`
3. **Organization**: Your organization
4. **Credential Type**: `Container Registry`
5. **Authentication URL**: `https://your-registry.example.com`
6. **Username**: Your registry username
7. **Password/Token**: Your registry password or token
8. **Save**

#### Step B.5: Add Execution Environment to AAP

1. **Administration → Execution Environments → Add**
2. Configure:
   - **Name**: `RHEL STIG EE`
   - **Image**: `quay.io/your-org/rhel-stig-ee:latest` (or your registry URL)
   - **Pull**: `Always` (or `If not present`)
   - **Registry credential**: Select credential from Step B.4 (if private)
   - **Organization**: Your organization
3. **Save**

#### Step B.6: Verify Execution Environment

Test the EE works:

1. **Resources → Templates → Add → Add job template**
2. Create a test template:
   - **Name**: `Test RHEL STIG EE`
   - **Job Type**: `Run`
   - **Inventory**: Any inventory
   - **Project**: Any project with a simple playbook
   - **Execution Environment**: `RHEL STIG EE`
   - **Playbook**: Simple test playbook
3. **Launch** the job
4. Verify in job output:
   - EE image pulls successfully
   - Collections are available
   - No errors about missing dependencies

#### Troubleshooting EE Build

**Issue: Build fails with "base image not found"**

Solution: Login to Red Hat registry first:
```bash
podman login registry.redhat.io
# Use your Red Hat credentials
```

**Issue: "collection not found" during build**

Solution: Ensure `requirements.yml` is in the same directory as `execution-environment.yml`

**Issue: AAP can't pull image from registry**

Solution:
1. Verify registry credential is correct
2. Check registry URL format (include `https://` if needed)
3. Ensure EE image was pushed successfully
4. Test pull manually on AAP controller:
   ```bash
   podman pull quay.io/your-org/rhel-stig-ee:latest
   ```

**Issue: python3-lxml not installed in EE**

Solution: Add to `additional_build_steps` in `execution-environment.yml`:
```yaml
additional_build_steps:
  append_final:
    - RUN microdnf install -y python3-lxml && microdnf clean all
```

---

## Step 2: Create Project

### Step 2.1: Add Git Credential (if private repo)

1. **Resources → Credentials → Add**
2. **Name**: `GitHub - RHEL STIG`
3. **Organization**: Your organization
4. **Credential Type**: `Source Control`
5. **Username**: Your Git username
6. **Password/Token**: Personal access token or password
7. **Save**

### Step 2.2: Create Project

1. **Resources → Projects → Add**
2. Configure:
   - **Name**: `RHEL DISA STIG`
   - **Organization**: Select your organization
   - **Execution Environment**: Select EE from Step 1
   - **Source Control Type**: `Git`
   - **Source Control URL**: `https://github.com/yourorg/disa-stig-rhel.git`
   - **Source Control Branch/Tag/Commit**: `main` (or your branch)
   - **Source Control Credential**: Select credential from Step 2.1 (if private)
   - **Options**:
     - ☑ Clean
     - ☑ Delete on Update
     - ☑ Update Revision on Launch (recommended)
3. **Save**
4. Click **Sync** button to verify project pulls successfully

---

## Step 3: Create Inventory

You can create inventory in AAP two ways:
- **Option A**: Add hosts manually (simple, good for small deployments)
- **Option B**: Source from project inventory file (recommended for larger deployments)

### Option A: Manual Inventory (Simple)

#### Step A.1: Create Inventory

1. **Resources → Inventories → Add → Inventory**
2. **Name**: `RHEL Servers`
3. **Organization**: Your organization
4. **Save**

#### Step A.2: Add Hosts Manually

1. **Hosts → Add**
2. For each RHEL server:
   - **Name**: `rhel8-server-01`
   - **Variables** (optional):
     ```yaml
     ---
     ansible_host: 192.168.1.100
     ```
3. **Save**
4. Repeat for all hosts

#### Step A.3: Add Groups (Optional)

Create groups for different RHEL versions:

1. **Groups → Add**
2. **Name**: `rhel8_servers`
3. **Save**
4. **Hosts → Add existing host** to assign hosts to group

### Option B: Source from Project (Recommended)

This option automatically imports inventory from your Git repository, keeping AAP in sync with your version-controlled inventory.

#### Step B.1: Create Inventory File in Project

First, add an inventory file to your Git repository:

```bash
# On your workstation where you have the repo cloned
cd /path/to/disa-stig-rhel

# Create inventory directory (if not exists)
mkdir -p inventories

# Create inventory file for RHEL servers
cat > inventories/rhel_servers.yml <<'EOF'
---
all:
  children:
    rhel_servers:
      children:
        rhel8_servers:
          hosts:
            rhel8-server-01:
              ansible_host: 192.168.1.101
            rhel8-server-02:
              ansible_host: 192.168.1.102
        rhel9_servers:
          hosts:
            rhel9-server-01:
              ansible_host: 192.168.1.201
            rhel9-server-02:
              ansible_host: 192.168.1.202
      vars:
        # Common variables for all RHEL servers
        ansible_user: ansible
        ansible_become: true
EOF

# Commit and push
git add inventories/rhel_servers.yml
git commit -m "Add AAP inventory file for RHEL servers"
git push
```

**Alternative: INI Format**

If you prefer INI format:

```ini
# inventories/rhel_servers.ini
[rhel8_servers]
rhel8-server-01 ansible_host=192.168.1.101
rhel8-server-02 ansible_host=192.168.1.102

[rhel9_servers]
rhel9-server-01 ansible_host=192.168.1.201
rhel9-server-02 ansible_host=192.168.1.202

[rhel_servers:children]
rhel8_servers
rhel9_servers

[rhel_servers:vars]
ansible_user=ansible
ansible_become=true
```

#### Step B.2: Create Inventory in AAP

1. **Resources → Inventories → Add → Inventory**
2. Configure:
   - **Name**: `RHEL Servers (Sourced)`
   - **Organization**: Your organization
   - **Variables** (optional - can override source vars):
     ```yaml
     ---
     # Optional: Override variables from source
     # ansible_user: different_user
     ```
3. **Save**

#### Step B.3: Add Inventory Source

1. In the inventory you just created, click **Sources** tab
2. **Add**
3. Configure the source:
   - **Name**: `RHEL Servers from Git`
   - **Source**: `Sourced from a Project`
   - **Execution Environment**: Select your RHEL STIG EE
   - **Project**: `RHEL DISA STIG`
   - **Inventory file**: `inventories/rhel_servers.yml` (or `.ini`)
   - **Update options**:
     - ☑ Overwrite (replace hosts/groups on sync)
     - ☑ Overwrite variables (replace variables on sync)
     - ☑ Update on project update (auto-sync when project syncs)
   - **Source variables** (optional):
     ```yaml
     ---
     # Optional: Pass variables to inventory script
     ```
4. **Save**

#### Step B.4: Sync Inventory Source

1. Click the **Sync** button (circular arrow) next to your source
2. Watch the sync job run
3. When complete, click **Hosts** tab to verify hosts were imported
4. Click **Groups** tab to verify groups were created

#### Step B.5: Schedule Regular Syncs (Optional)

Keep inventory up-to-date automatically:

1. In inventory source, click **Schedules** tab
2. **Add**
3. Configure:
   - **Name**: `Sync RHEL inventory daily`
   - **Start date/time**: Select start time
   - **Frequency**: `Daily`
   - **Run every**: `1 day`
   - **Run at**: `02:00:00` (2 AM)
4. **Save**

### Comparing Options

| Feature | Manual (Option A) | Sourced (Option B) |
|---------|-------------------|-------------------|
| Setup complexity | Simple | Requires inventory file in Git |
| Maintenance | Manual updates in AAP GUI | Update Git, auto-sync to AAP |
| Version control | ❌ No | ✅ Yes |
| Audit trail | AAP logs only | Git history + AAP logs |
| Scale | Good for <20 hosts | Good for any size |
| Team collaboration | GUI only | Git workflow |
| Automation | Manual | Automatic sync |
| Best for | Small/test environments | Production environments |

**Recommendation**: Use **Option B (Sourced)** for production. It provides:
- Version control of inventory
- Automatic sync from Git
- Better collaboration (PR reviews for inventory changes)
- Audit trail via Git history
- Easier to manage at scale

---

## Step 4: Create Job Templates

### Template 1: STIG Hardening (Primary - with Survey)

This is the main production template with GUI survey for easy configuration.

**IMPORTANT**: Use `site.yml` (role-based approach) instead of `rhel_stig_with_rollback.yml`:
- ✅ `site.yml` - Clean role invocation (recommended)
- ❌ `rhel_stig_with_rollback.yml` - Legacy playbook with duplicate post_tasks

See [PLAYBOOK_USAGE.md](../PLAYBOOK_USAGE.md) for details.

1. **Resources → Templates → Add → Add job template**
2. Configure **Details**:
   - **Name**: `STIG - Full Hardening`
   - **Job Type**: `Run`
   - **Inventory**: `RHEL Servers`
   - **Project**: `RHEL DISA STIG`
   - **Execution Environment**: Select your EE
   - **Playbook**: `playbooks/site.yml` ⭐ **Use this, not rhel_stig_with_rollback.yml**
   - **Credentials**: 
     - **Type**: Machine
     - Select credential with sudo access
   - **Variables**:
     ```yaml
     ---
     # AAP controller backup configuration
     rhel_stig_with_rollback_controller_backup_dir: /var/lib/awx/projects/stig_backups
     rhel_stig_with_rollback_fetch_to_controller: true
     
     # Native parsing (enabled by default in role)
     rhel_stig_with_rollback_use_native_parsing: true
     rhel_stig_with_rollback_auto_install_deps: true
     
     # Enable auto-detect for RHEL 8 compatibility
     rhel_stig_with_rollback_auto_detect_python: true
     ```
   - **Options**:
     - ☑ Privilege Escalation
     - ☑ Enable Fact Storage
3. **Save**

**Do NOT configure survey yet - we'll do that in Step 5**

### Template 2: Audit Only (No Remediation)

Quick compliance check without making changes.

1. **Resources → Templates → Add → Add job template**
2. Configure:
   - **Name**: `STIG - Audit Only`
   - **Job Type**: `Run`
   - **Inventory**: `RHEL Servers`
   - **Project**: `RHEL DISA STIG`
   - **Execution Environment**: Select your EE
   - **Playbook**: `playbooks/rhel_stig_audit_only.yml`
   - **Credentials**: Machine credential with sudo
   - **Options**: ☑ Privilege Escalation
3. **Save**

### Template 3: Rollback

Restore system from backup after failed hardening.

1. **Resources → Templates → Add → Add job template**
2. Configure:
   - **Name**: `STIG - Rollback`
   - **Job Type**: `Run`
   - **Inventory**: `RHEL Servers`
   - **Project**: `RHEL DISA STIG`
   - **Execution Environment**: Select your EE
   - **Playbook**: `playbooks/perform_rollback.yml`
   - **Credentials**: Machine credential with sudo
   - **Options**: 
     - ☑ Privilege Escalation
     - ☑ Prompt on launch → Variables
   - **Variables** (example - will be overridden at launch):
     ```yaml
     ---
     # Specify backup name at launch
     rhel_stig_with_rollback_backup_name: pre_stig_hostname_20261105T120000
     ```
3. **Save**

### Template 4: Final Audit Report

Detailed compliance report with CAT I/II/III breakdown.

1. **Resources → Templates → Add → Add job template**
2. Configure:
   - **Name**: `STIG - Final Audit Report`
   - **Job Type**: `Run`
   - **Inventory**: `RHEL Servers`
   - **Project**: `RHEL DISA STIG`
   - **Execution Environment**: Select your EE
   - **Playbook**: `playbooks/final_audit_report.yml`
   - **Credentials**: Machine credential with sudo
   - **Options**: ☑ Privilege Escalation
3. **Save**

---

## Step 5: Configure Surveys

**IMPORTANT**: AAP 2.7 does NOT support importing JSON survey files. You must create surveys manually through the GUI.

### Configure Survey for "STIG - Full Hardening" Template

1. Go to **Resources → Templates**
2. Click **STIG - Full Hardening**
3. Click **Survey** tab
4. Click **Add**
5. Add each question below:

#### Question 1: STIG Audit Mode

- **Question**: `STIG Audit Mode`
- **Description**: `Choose full audit (all rules) or selective (specific rules only)`
- **Answer variable name**: `stig_audit_mode`
- **Answer type**: `Multiple Choice (single select)`
- **Multiple Choice Options**:
  ```
  full
  selective
  ```
- **Default answer**: `full`
- **Required**: ☑ (checked)
- Click **Save**

#### Question 2: STIG Rules to Audit

- **Question**: `STIG Rules (comma-separated, for selective mode)`
- **Description**: `List specific STIG rules to audit. Only used when Audit Mode is 'selective'. Example: sysctl_crypto_fips_enabled,audit_rules_login_events,sshd_set_idle_timeout`
- **Answer variable name**: `stig_rules_input`
- **Answer type**: `Textarea`
- **Default answer**: ` ` (leave blank)
- **Required**: ☐ (unchecked)
- Click **Save**

#### Question 3: Apply Remediations

- **Question**: `Apply Remediations?`
- **Description**: `Apply fixes to failed STIG rules? If false, performs audit only.`
- **Answer variable name**: `rhel_stig_with_rollback_apply_remediations`
- **Answer type**: `Multiple Choice (single select)`
- **Multiple Choice Options**:
  ```
  true
  false
  ```
- **Default answer**: `true`
- **Required**: ☑ (checked)
- Click **Save**

#### Question 4: Auto Rollback on Failure

- **Question**: `Auto Rollback on Failure?`
- **Description**: `Automatically restore from backup if system verification fails after remediation?`
- **Answer variable name**: `rhel_stig_with_rollback_auto_rollback_on_failure`
- **Answer type**: `Multiple Choice (single select)`
- **Multiple Choice Options**:
  ```
  true
  false
  ```
- **Default answer**: `true`
- **Required**: ☑ (checked)
- Click **Save**

#### Question 5: Organization Tailoring Profile (Optional)

- **Question**: `Tailoring Profile (optional)`
- **Description**: `Organization-specific tailoring profile name. Leave blank for DISA defaults. Example: myorg`
- **Answer variable name**: `rhel_stig_with_rollback_tailoring_profile`
- **Answer type**: `Text`
- **Default answer**: ` ` (leave blank)
- **Required**: ☐ (unchecked)
- Click **Save**

### Enable the Survey

1. After adding all questions, toggle **Survey Enabled** to ON
2. Click **Save**

---

## Running Jobs

### Scenario 1: Full STIG Hardening

Audit all STIG rules and apply all remediations.

1. **Resources → Templates → STIG - Full Hardening**
2. Click **Launch**
3. Fill survey:
   - **STIG Audit Mode**: `full`
   - **STIG Rules**: (leave blank)
   - **Apply Remediations**: `true`
   - **Auto Rollback on Failure**: `true`
   - **Tailoring Profile**: (leave blank or specify)
4. **Select hosts** to run against
5. Click **Next** → **Launch**

### Scenario 2: Selective STIG Hardening

Audit and remediate only specific rules.

1. **Resources → Templates → STIG - Full Hardening**
2. Click **Launch**
3. Fill survey:
   - **STIG Audit Mode**: `selective`
   - **STIG Rules**: `sysctl_crypto_fips_enabled,audit_rules_login_events,sshd_set_idle_timeout`
   - **Apply Remediations**: `true`
   - **Auto Rollback on Failure**: `true`
   - **Tailoring Profile**: (leave blank)
4. **Select hosts**
5. Click **Next** → **Launch**

### Scenario 3: Audit Only (No Changes)

Check compliance without making any changes.

1. **Resources → Templates → STIG - Audit Only**
2. Click **Launch**
3. **Select hosts**
4. Click **Next** → **Launch**

### Scenario 4: Perform Rollback

Restore a system from backup.

1. **Resources → Templates → STIG - Rollback**
2. Click **Launch**
3. **Variables** prompt appears - enter:
   ```yaml
   ---
   rhel_stig_with_rollback_backup_name: pre_stig_rhel8-server-01_20261105T120000
   ```
4. **Select hosts** (must match the backup hostname)
5. Click **Next** → **Launch**

**Finding backup names:**
- Check AAP controller: `/var/lib/awx/projects/stig_backups/{hostname}/`
- Check target host: `/opt/stig_backups/`
- From previous job output (Phase 6 summary)

---

## Monitoring and Results

### Job Execution Phases

Monitor the job output for these phases:

1. **Phase 1: Validation**
   - RHEL version detection
   - SCAP content verification
   - Python compatibility check
   - Dependency installation (python3-lxml if needed)

2. **Phase 2: Backup**
   - Create pre-hardening backup
   - Archive critical files
   - Copy backup to AAP controller

3. **Phase 3: Baseline Audit**
   - Run OpenSCAP scan
   - Parse results (native Ansible or Python fallback)
   - Categorize failures (CAT I/II/III)

4. **Phase 4: Remediation** (if Apply Remediations = true)
   - Generate Ansible remediation playbook
   - Apply fixes to failed rules
   - Create post-hardening audit

5. **Phase 5: Verification**
   - Test SSH connectivity
   - Verify critical services
   - Check system responsiveness
   - **Auto-rollback triggers here if checks fail**

6. **Phase 6: Summary**
   - Display compliance scores
   - Show before/after comparison
   - Provide rollback instructions

### Viewing Artifacts

**On AAP Controller:**
- Backups: `/var/lib/awx/projects/stig_backups/{hostname}/`

**On Target Host:**
- Audit results: `/opt/stig_audit/`
  - `baseline_*.xml` - OpenSCAP XML results
  - `baseline_*.html` - Human-readable HTML report
  - `post_hardening_*.xml` - After remediation
- Remediation logs: `/opt/stig_work/`
  - `ssg-rhel*-ds-*.yml` - Generated remediation playbook
- Backups: `/opt/stig_backups/`
  - `pre_stig_*.tar.gz` - Compressed backup archives

### Compliance Scoring

The role reports compliance as a percentage:

```
Baseline:         45.2% (452 pass, 548 fail, 100 N/A)
Post-Hardening:   98.7% (987 pass, 13 fail, 100 N/A)
Improvement:      +53.5%
```

---

## Emergency Recovery

### If SSH Access is Lost

If a host becomes unreachable after hardening:

#### Method 1: Console/BMC Access

1. Access via console (iDRAC, iLO, vCenter, etc.)
2. Login as root
3. Find latest backup:
   ```bash
   ls -lah /opt/stig_backups/
   ```
4. Restore manually:
   ```bash
   cd /
   tar xzf /opt/stig_backups/pre_stig_hostname_20261105T120000.tar.gz
   systemctl restart sshd
   ```

#### Method 2: Restore from AAP Controller

If you have out-of-band management or the system is still accessible:

1. **Resources → Templates → Add → Add job template**
2. Create emergency restore template:
   - **Playbook**: `playbooks/emergency_restore_from_controller.yml`
   - **Prompt on launch**: Variables
3. Launch with:
   ```yaml
   ---
   target_host: rhel8-server-01
   backup_name: pre_stig_rhel8-server-01_20261105T120000
   ```

---

## Troubleshooting

### Issue: Project Sync Fails

**Symptom**: Project shows "Failed" status

**Solutions**:
1. Check Git URL is correct
2. Verify credential has repo access
3. Check execution environment has git
4. Review project sync log for details

### Issue: Survey Not Appearing

**Symptom**: Launch button doesn't show survey

**Solutions**:
1. Verify **Survey Enabled** toggle is ON
2. Check at least one question is defined
3. Save the template after enabling survey

### Issue: python3-lxml Not Available

**Symptom**: Native parsing fails, falls back to Python scripts

**Solutions**:
1. Ensure RHEL subscription is active
2. Enable required repositories
3. Or disable native parsing:
   ```yaml
   rhel_stig_with_rollback_use_native_parsing: false
   ```

### Issue: SCAP Content Missing

**Symptom**: Phase 1 fails - "SCAP content not found"

**Solutions**:
1. Role automatically installs `scap-security-guide`
2. Verify RHEL subscription is active
3. Manually install:
   ```bash
   dnf install -y openscap-scanner scap-security-guide
   ```

### Issue: Backup Fetch to Controller Fails

**Symptom**: Phase 2 warning - "Failed to fetch backup to controller"

**Solutions**:
1. Create backup directory on AAP controller:
   ```bash
   mkdir -p /var/lib/awx/projects/stig_backups
   chown awx:awx /var/lib/awx/projects/stig_backups
   ```
2. Or disable controller backup:
   ```yaml
   rhel_stig_with_rollback_fetch_to_controller: false
   ```

### Issue: Selective Mode Not Working

**Symptom**: Full audit runs even with `stig_audit_mode: selective`

**Solutions**:
1. Verify survey variable name is exactly: `stig_audit_mode`
2. Verify rules variable name is exactly: `stig_rules_input`
3. Check playbook is `rhel_stig_with_rollback.yml` (not `site.yml`)
4. Ensure rules are comma-separated with no spaces

---

## Finding STIG Rule IDs

To identify rule IDs for selective mode:

### Method 1: Run Audit-Only First

1. Run **STIG - Audit Only** template
2. Download HTML report from `/opt/stig_audit/baseline_*.html`
3. Rule IDs are in the format: `xccdf_org.ssgproject.content_rule_RULE_ID`
4. Use the `RULE_ID` part only

### Method 2: Run Final Audit Report

1. Run **STIG - Final Audit Report** template
2. Check job output for rule categorization
3. Copy rule IDs from output

### Common Rule IDs

**CAT I (High Severity):**
- `sysctl_crypto_fips_enabled` - Enable FIPS mode
- `no_empty_passwords` - No empty passwords
- `sshd_disable_empty_passwords` - SSH disable empty passwords
- `accounts_password_pam_unix_remember` - Password history

**CAT II (Medium Severity):**
- `audit_rules_login_events` - Audit login events
- `sshd_set_idle_timeout` - SSH idle timeout
- `accounts_password_minlen_login_defs` - Password minimum length
- `file_permissions_var_log_audit` - Audit log permissions
- `package_aide_installed` - AIDE installed
- `service_auditd_enabled` - Auditd enabled

**CAT III (Low Severity):**
- `banner_etc_issue` - Login banner
- `sshd_print_last_log` - Display last login
- `file_owner_etc_passwd` - /etc/passwd ownership

---

## Best Practices

### 1. Always Audit First

Before applying remediations, run an audit-only job to:
- Establish baseline compliance
- Identify what will change
- Plan remediation strategy

### 2. Test in Non-Production

- Use selective mode to test specific rules first
- Validate in dev/test environment before production
- Monitor for 24-48 hours post-hardening

### 3. Backup Retention

- Controller backups: `/var/lib/awx/projects/stig_backups/`
- Implement backup rotation policy
- Test restore procedures regularly

### 4. Use Tailoring for Organizations

Create organization-specific profiles:
```bash
# On workstation
mkdir -p tailoring/myorg
cp tailoring/example_tailoring.yml tailoring/myorg/common.yml
# Edit with your values, commit to Git
```

Then specify in survey: `myorg`

### 5. Monitor Job Logs

- Save job output for audit trail
- Review Phase 5 verification results
- Document any manual post-remediation steps

### 6. Schedule Regular Audits

Create scheduled jobs to:
- Run weekly compliance audits
- Track compliance drift
- Alert on new failures

---

## Additional Resources

- [TAILORING_GUIDE.md](TAILORING_GUIDE.md) - Customize STIG variables
- [RHEL8_COMPATIBILITY.md](RHEL8_COMPATIBILITY.md) - RHEL 8 specific notes
- [DISASTER_RECOVERY.md](DISASTER_RECOVERY.md) - Emergency procedures
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues
- [PLAYBOOK_USAGE.md](PLAYBOOK_USAGE.md) - Which playbook to use when

---

## Summary Checklist

- [ ] Create/verify execution environment with community.general >= 8.0.0
- [ ] Create project pointing to Git repository
- [ ] Create inventory with RHEL hosts
- [ ] Create 4 job templates (Hardening, Audit, Rollback, Report)
- [ ] Configure survey on Hardening template (5 questions)
- [ ] Enable survey
- [ ] Create backup directory on AAP controller
- [ ] Test audit-only job first
- [ ] Review baseline compliance
- [ ] Run hardening job with survey
- [ ] Monitor all 6 phases
- [ ] Review final compliance report
- [ ] Document backup names for rollback

**Setup time**: ~30-45 minutes  
**First execution**: ~15-30 minutes per host (depending on remediation count)

---

## Appendix: Quick Reference Commands

### Custom Execution Environment - Complete Workflow

```bash
# 1. Install ansible-builder
sudo dnf install -y ansible-builder podman

# 2. Create EE directory and files
mkdir -p ~/rhel-stig-ee && cd ~/rhel-stig-ee

cat > execution-environment.yml <<'EOF'
---
version: 3
images:
  base_image:
    name: registry.redhat.io/ansible-automation-platform-24/ee-minimal-rhel9:latest
dependencies:
  galaxy: requirements.yml
  python:
    - python3-lxml
additional_build_steps:
  append_final:
    - RUN microdnf install -y python3-lxml && microdnf clean all
EOF

cat > requirements.yml <<'EOF'
---
collections:
  - name: community.general
    version: ">=8.0.0"
  - name: ansible.posix
    version: ">=1.3.0"
EOF

# 3. Login to Red Hat registry
podman login registry.redhat.io

# 4. Build the image
ansible-builder build --tag rhel-stig-ee:1.0.0 --container-runtime podman

# 5. Verify image
podman images | grep rhel-stig-ee

# 6. Tag for your registry (Quay.io example)
podman login quay.io
podman tag rhel-stig-ee:1.0.0 quay.io/YOUR-ORG/rhel-stig-ee:1.0.0
podman tag rhel-stig-ee:1.0.0 quay.io/YOUR-ORG/rhel-stig-ee:latest

# 7. Push to registry
podman push quay.io/YOUR-ORG/rhel-stig-ee:1.0.0
podman push quay.io/YOUR-ORG/rhel-stig-ee:latest

# 8. Add to AAP via GUI
# Administration → Execution Environments → Add
# Image: quay.io/YOUR-ORG/rhel-stig-ee:latest
```

### AAP Controller Backup Directory Setup

```bash
# On AAP controller as root
mkdir -p /var/lib/awx/projects/stig_backups
chown awx:awx /var/lib/awx/projects/stig_backups
chmod 755 /var/lib/awx/projects/stig_backups

# Verify
ls -ld /var/lib/awx/projects/stig_backups
```

### Testing Collections in Execution Environment

```bash
# Test pull and run the EE locally
podman pull quay.io/YOUR-ORG/rhel-stig-ee:latest

# Run and check collections
podman run -it --rm quay.io/YOUR-ORG/rhel-stig-ee:latest \
  ansible-galaxy collection list | grep -E "community.general|ansible.posix"

# Expected output:
# community.general   8.0.0
# ansible.posix       1.3.0
```

### Survey Variables Quick Reference

```yaml
# These exact variable names must be used in AAP survey questions:
stig_audit_mode: full                                    # or 'selective'
stig_rules_input: "rule1,rule2,rule3"                   # comma-separated, no spaces
rhel_stig_with_rollback_apply_remediations: true        # or 'false'
rhel_stig_with_rollback_auto_rollback_on_failure: true  # or 'false'
rhel_stig_with_rollback_tailoring_profile: ""           # optional org name
```

### Common STIG Rule ID Examples

```yaml
# Selective mode example - paste this in survey textarea
sysctl_crypto_fips_enabled,audit_rules_login_events,sshd_set_idle_timeout,accounts_password_minlen_login_defs,package_aide_installed
```

### Inventory Sourced from Project - Quick Setup

```bash
# On your workstation - add inventory file to Git repo
cd /path/to/disa-stig-rhel
mkdir -p inventories

# Create YAML inventory
cat > inventories/rhel_servers.yml <<'EOF'
---
all:
  children:
    rhel_servers:
      children:
        rhel8_servers:
          hosts:
            rhel8-server-01:
              ansible_host: 192.168.1.101
            rhel8-server-02:
              ansible_host: 192.168.1.102
        rhel9_servers:
          hosts:
            rhel9-server-01:
              ansible_host: 192.168.1.201
      vars:
        ansible_user: ansible
        ansible_become: true
EOF

# Commit and push
git add inventories/rhel_servers.yml
git commit -m "Add AAP inventory for RHEL servers"
git push

# Then in AAP GUI:
# 1. Resources → Inventories → Add → Inventory
#    Name: RHEL Servers (Sourced)
# 2. Sources → Add
#    Source: Sourced from a Project
#    Project: RHEL DISA STIG
#    Inventory file: inventories/rhel_servers.yml
#    ☑ Overwrite
#    ☑ Update on project update
# 3. Click Sync button
# 4. Verify: Hosts tab shows imported hosts
```

**Inventory INI format alternative:**

```ini
# inventories/rhel_servers.ini
[rhel8_servers]
rhel8-server-01 ansible_host=192.168.1.101
rhel8-server-02 ansible_host=192.168.1.102

[rhel9_servers]
rhel9-server-01 ansible_host=192.168.1.201

[rhel_servers:children]
rhel8_servers
rhel9_servers

[rhel_servers:vars]
ansible_user=ansible
ansible_become=true
```

---

*For support, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or open an issue in the repository.*
