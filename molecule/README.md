## Molecule Testing for RHEL STIG Role

This directory contains Molecule test scenarios for validating the `rhel_stig_with_rollback` role.

### Test Scenarios

#### Default Scenario

Tests the role against RHEL 8 and RHEL 9 containers to validate:

- **RHEL 8 Compatibility**
  - Python 3.6 support with lxml
  - Try-fallback pattern for archive operations
  - Auto-detection and auto-installation of dependencies
  - Native Ansible parsing with lxml

- **Core Functionality**
  - Role tasks syntax and structure
  - Variable naming conventions
  - Task idempotency
  - Backup creation (without actual STIG remediation)
  - Python compatibility checking

### Running Tests

#### Prerequisites

```bash
# Install molecule and podman driver
pip install molecule molecule-plugins[podman]

# Ensure podman is installed
dnf install podman
```

#### Run Full Test Suite

```bash
# From repository root
molecule test
```

#### Run Individual Test Phases

```bash
# Syntax check only
molecule syntax

# Create test instances
molecule create

# Run converge (apply role)
molecule converge

# Run verification tests
molecule verify

# Test idempotency
molecule idempotence

# Cleanup
molecule destroy
```

### Test Configuration

The test configuration focuses on **non-destructive testing**:

```yaml
rhel_stig_with_rollback_apply_remediations: false  # Don't apply actual STIG fixes
rhel_stig_with_rollback_enable_auto_backup: true   # Test backup creation
rhel_stig_with_rollback_use_native_parsing: true   # Test native Ansible parsing
rhel_stig_with_rollback_auto_install_deps: true    # Test dependency installation
rhel_stig_with_rollback_fetch_to_controller: false # Don't fetch in container tests
```

### What is NOT Tested

Due to container limitations and security considerations:

- ❌ Actual STIG remediation (would modify container filesystem)
- ❌ OpenSCAP scanning (requires scap-security-guide and kernel features)
- ❌ SELinux modifications
- ❌ Kernel parameter changes
- ❌ Systemd service modifications

### What IS Tested

- ✅ Role syntax and structure
- ✅ Python version detection
- ✅ lxml availability check and installation
- ✅ Backup directory creation
- ✅ Archive module try-fallback pattern
- ✅ Task idempotency
- ✅ Variable prefixing and naming
- ✅ RHEL 8 and RHEL 9 compatibility

### Test Platforms

- **RHEL 8**: `registry.access.redhat.com/ubi8/ubi-init:latest`
- **RHEL 9**: `registry.access.redhat.com/ubi9/ubi-init:latest`

### Continuous Integration

To integrate with CI/CD:

```yaml
# Example GitHub Actions
- name: Run Molecule tests
  run: |
    pip install molecule molecule-plugins[podman]
    molecule test
```

### Troubleshooting

#### Podman Permission Issues

```bash
# Run rootless podman
export DOCKER_HOST=unix:///run/user/$(id -u)/podman/podman.sock
```

#### Container Image Pull Issues

```bash
# Login to Red Hat registry
podman login registry.access.redhat.com
```

#### Python Version Issues

The tests automatically install python39-lxml to ensure native parsing works on all platforms including RHEL 8 (Python 3.6).

### Test Results Interpretation

- **Syntax Check**: Validates YAML syntax and Ansible structure
- **Converge**: Applies the role to test containers
- **Idempotence**: Re-runs and ensures no changes (validates task idempotency)
- **Verify**: Runs verification playbook to check expected states

### Extending Tests

To add new test scenarios:

```bash
molecule init scenario <scenario_name>
```

Then customize the `molecule.yml`, `converge.yml`, and `verify.yml` files.
