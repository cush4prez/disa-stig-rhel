# Test Playbooks

⚠️ **These playbooks are for development and testing purposes only. Do not use in production.**

## Purpose

These playbooks test specific functionality during development of the role. They are useful for:
- Validating new features
- Regression testing
- Performance comparison
- Integration testing

## Available Tests

### test_actual_remediation.yml
Tests the complete remediation workflow:
- Runs baseline audit
- Generates remediation script
- Applies remediations
- Runs post-hardening audit
- Compares before/after compliance scores

**Use for**: Validating that remediations actually work

### test_native_parsing.yml
Compares native Ansible XML parsing vs Python scripts:
- Creates sample OSCAP XML file
- Parses with native Ansible (`community.general.xml`)
- Parses with Python script
- Compares results for accuracy

**Use for**: Validating native parsing implementation

## How to Run

```bash
# Test remediation workflow
ansible-playbook -i inventory playbooks/tests/test_actual_remediation.yml

# Test native parsing
ansible-playbook -i inventory playbooks/tests/test_native_parsing.yml
```

## Requirements

- Test environment (not production!)
- RHEL 8, 9, or 10
- SCAP content installed (`scap-security-guide`)
- python39-lxml (for parsing comparison)

## Adding New Tests

When adding test playbooks:

1. Name them `test_<feature>.yml`
2. Add clear documentation at the top of the file
3. Make them safe to run (no destructive actions)
4. Update this README with test description
5. Include validation/assertion tasks

## Integration with Molecule

For more comprehensive testing, see:
- `/molecule/` - Molecule test scenarios
- `/molecule/README.md` - Molecule testing guide

## Production Testing

For production-safe validation, use:
- `playbooks/rhel_benchmark_audit_only.yml` - Audit without changes
- `playbooks/rhel_benchmark_verification.yml` - Verify compliance
- `playbooks/diagnostics/` - Diagnostic playbooks
