# CIS Benchmark Configuration Guide

## Overview

This role supports **multiple security benchmarks** including:
- ✅ **DISA STIG** (default)
- ✅ **CIS Benchmarks** (multiple levels)
- ✅ **Custom profiles** (any SCAP profile)

All using the same SCAP Security Guide (SSG) content from Red Hat.

## Quick Start

### Using CIS Server Level 1

```bash
ansible-playbook -i inventory playbooks/site.yml \
  -e rhel_stig_with_rollback_benchmark_profile=cis_server_l1
```

### Using CIS Server Level 2

```bash
ansible-playbook -i inventory playbooks/site.yml \
  -e rhel_stig_with_rollback_benchmark_profile=cis_server_l2
```

## Available Benchmark Profiles

| Profile Name | Description | Typical Use Case |
|--------------|-------------|------------------|
| `stig` | DISA STIG (default) | DoD/Federal compliance |
| `cis` | CIS Red Hat Enterprise Linux Benchmark | General CIS compliance |
| `cis_server_l1` | CIS Server Level 1 | Basic server hardening |
| `cis_server_l2` | CIS Server Level 2 | Enhanced server hardening |
| `cis_workstation_l1` | CIS Workstation Level 1 | Basic workstation hardening |
| `cis_workstation_l2` | CIS Workstation Level 2 | Enhanced workstation hardening |
| `custom` | Custom profile | Use `rhel_stig_with_rollback_stig_profile_id` directly |

## Configuration Methods

### Method 1: Command Line Override

```bash
ansible-playbook -i inventory playbooks/site.yml \
  -e rhel_stig_with_rollback_benchmark_profile=cis_server_l1
```

### Method 2: Inventory Variables

```yaml
# inventory/group_vars/rhel_servers.yml
rhel_stig_with_rollback_benchmark_profile: cis_server_l1
rhel_stig_with_rollback_apply_remediations: true
rhel_stig_with_rollback_auto_rollback_on_failure: true
```

### Method 3: Role Defaults

```yaml
# roles/rhel_stig_with_rollback/defaults/main.yml
rhel_stig_with_rollback_benchmark_profile: "cis_server_l1"
```

### Method 4: Playbook Variables

```yaml
---
- hosts: all
  roles:
    - role: rhel_stig_with_rollback
      rhel_stig_with_rollback_benchmark_profile: cis_server_l1
      rhel_stig_with_rollback_apply_remediations: true
```

## AAP (Ansible Automation Platform) Configuration

### Add to Survey

Add a new survey question:

**Question 6: Benchmark Profile**
- **Prompt**: Select security benchmark
- **Answer Variable Name**: `rhel_stig_with_rollback_benchmark_profile`
- **Answer Type**: Multiple Choice (single select)
- **Multiple Choice Options**:
  - `stig` ⭐ (default)
  - `cis`
  - `cis_server_l1`
  - `cis_server_l2`
  - `cis_workstation_l1`
  - `cis_workstation_l2`
- **Default Answer**: `stig`

The survey will automatically pass the selected profile to the role.

## Understanding CIS Levels

### Level 1 (L1)
- **Focus**: Basic security hardening
- **Impact**: Minimal impact on functionality
- **Difficulty**: Easy to implement
- **Recommended for**: All systems

### Level 2 (L2)
- **Focus**: Enhanced security
- **Impact**: May impact some functionality
- **Difficulty**: Requires planning
- **Recommended for**: High-security environments
- **Note**: L2 includes all L1 controls PLUS additional controls

### Server vs Workstation
- **Server**: For headless servers, no GUI considerations
- **Workstation**: Includes GUI/desktop-specific controls

## Verification

### Check Available Profiles

To see all available profiles on your system:

```bash
oscap info /usr/share/xml/scap/ssg/content/ssg-rhel9-ds.xml | grep Profile
```

**RHEL 9 Example Output**:
```
Profile: xccdf_org.ssgproject.content_profile_stig
Profile: xccdf_org.ssgproject.content_profile_cis
Profile: xccdf_org.ssgproject.content_profile_cis_server_l1
Profile: xccdf_org.ssgproject.content_profile_cis_server_l2
Profile: xccdf_org.ssgproject.content_profile_cis_workstation_l1
Profile: xccdf_org.ssgproject.content_profile_cis_workstation_l2
```

### Verify Selected Profile During Run

The playbook displays the selected profile at startup:

```
TASK [rhel_stig_with_rollback : Display selected benchmark profile]
ok: [rhel9] =>
  msg:
  - 'Benchmark Profile: cis_server_l1'
  - 'SCAP Profile ID: xccdf_org.ssgproject.content_profile_cis_server_l1'
```

## Custom Profiles

For profiles not in the predefined list:

```bash
ansible-playbook -i inventory playbooks/site.yml \
  -e rhel_stig_with_rollback_benchmark_profile=custom \
  -e rhel_stig_with_rollback_stig_profile_id="xccdf_org.ssgproject.content_profile_ospp"
```

**Example Custom Profiles**:
- `xccdf_org.ssgproject.content_profile_ospp` - OS Protection Profile
- `xccdf_org.ssgproject.content_profile_pci-dss` - PCI-DSS v3.2.1
- `xccdf_org.ssgproject.content_profile_hipaa` - HIPAA
- `xccdf_org.ssgproject.content_profile_cui` - NIST 800-171

## Comparison: STIG vs CIS

| Aspect | DISA STIG | CIS Benchmark |
|--------|-----------|---------------|
| **Origin** | Defense Information Systems Agency | Center for Internet Security |
| **Primary Use** | DoD/Federal government | General industry |
| **Strictness** | Very strict | L1=moderate, L2=strict |
| **Documentation** | Military/government focused | Industry best practices |
| **Updates** | Quarterly | Community-driven |
| **Compliance** | Required for DoD systems | Industry standard |

## Example Workflows

### CIS L1 Audit Only

```bash
ansible-playbook -i inventory playbooks/site.yml \
  -e rhel_stig_with_rollback_benchmark_profile=cis_server_l1 \
  -e rhel_stig_with_rollback_apply_remediations=false
```

### CIS L2 Full Hardening

```bash
ansible-playbook -i inventory playbooks/site.yml \
  -e rhel_stig_with_rollback_benchmark_profile=cis_server_l2 \
  -e rhel_stig_with_rollback_apply_remediations=true
```

### CIS Selective Hardening

```bash
ansible-playbook -i inventory playbooks/site.yml \
  -e rhel_stig_with_rollback_benchmark_profile=cis_server_l1 \
  -e "rhel_stig_with_rollback_stig_rules_to_apply=['service_auditd_enabled','package_aide_installed']"
```

## Troubleshooting

### Profile Not Found

**Error**: `Profile 'xccdf_org.ssgproject.content_profile_cis_server_l1' not found`

**Solution**: Install/update SCAP Security Guide:
```bash
dnf install -y scap-security-guide
```

### Different RHEL Versions

Profile availability varies by RHEL version:
- **RHEL 8**: Most CIS profiles available
- **RHEL 9**: Full CIS profile suite
- **RHEL 10**: Profiles evolving (check with `oscap info`)

### Unknown Rules in Selective Mode

CIS rule IDs differ from STIG rule IDs. To find CIS rule IDs:

```bash
oscap info --profile cis_server_l1 \
  /usr/share/xml/scap/ssg/content/ssg-rhel9-ds.xml | grep "Rule"
```

## Best Practices

1. **Start with Audit**: Run audit-only first to understand impact
   ```bash
   -e rhel_stig_with_rollback_apply_remediations=false
   ```

2. **Test in Dev**: Test CIS profiles in dev/test environments first

3. **Understand Levels**: Know the difference between L1 and L2 before deploying

4. **Review Tailoring**: Create organization-specific tailoring for CIS just like STIG
   ```bash
   -e rhel_stig_with_rollback_tailoring_profile=myorg
   -e rhel_stig_with_rollback_benchmark_profile=cis_server_l1
   ```

5. **Monitor Impact**: CIS L2 may affect functionality - validate critical services

## Migration from STIG to CIS

### Step 1: Audit Current State

```bash
# STIG baseline
ansible-playbook -i inventory playbooks/site.yml \
  -e rhel_stig_with_rollback_benchmark_profile=stig \
  -e rhel_stig_with_rollback_apply_remediations=false

# CIS L1 audit
ansible-playbook -i inventory playbooks/site.yml \
  -e rhel_stig_with_rollback_benchmark_profile=cis_server_l1 \
  -e rhel_stig_with_rollback_apply_remediations=false
```

### Step 2: Compare Results

Review audit reports from both runs to understand differences.

### Step 3: Apply CIS

```bash
ansible-playbook -i inventory playbooks/site.yml \
  -e rhel_stig_with_rollback_benchmark_profile=cis_server_l1 \
  -e rhel_stig_with_rollback_apply_remediations=true
```

### Step 4: Verify

```bash
ansible-playbook playbooks/final_audit_report.yml \
  -e rhel_stig_with_rollback_benchmark_profile=cis_server_l1
```

## Summary

- ✅ Use `rhel_stig_with_rollback_benchmark_profile` to switch profiles
- ✅ Six predefined profiles: `stig`, `cis`, `cis_server_l1`, `cis_server_l2`, `cis_workstation_l1`, `cis_workstation_l2`
- ✅ All role features work with CIS (backup, rollback, selective mode, tailoring)
- ✅ Easy AAP integration via survey
- ✅ Same SCAP content, different compliance frameworks
