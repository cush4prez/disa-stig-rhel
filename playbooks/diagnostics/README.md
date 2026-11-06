# Diagnostic Playbooks

These playbooks help troubleshoot issues with security benchmark hardening, scoring, and remediation.

## When to Use Diagnostic Playbooks

- **Unexpected compliance scores** - Use score diagnostics
- **Remediation not working** - Use remediation diagnostics
- **General troubleshooting** - Use full diagnostic

## Available Diagnostics

### Score Diagnostics

**check_score_calculation.yml**
- Quick check of OSCAP score calculation
- Validates XML parsing logic
- Shows pass/fail/notapplicable counts
- **Use when**: Scores look wrong or inconsistent

**debug_oscap_score.yml**
- Detailed OSCAP score debugging
- Shows native vs Python parsing comparison
- Displays raw XML analysis
- **Use when**: Need deep score investigation

**diagnose_score_issue.yml**
- Comprehensive score issue diagnostic
- Analyzes compliance calculation methods
- Compares different parsing approaches
- **Use when**: Scores differ between runs

### Remediation Diagnostics

**benchmark_remediation_diagnostic.yml**
- Tests remediation script generation for any benchmark
- Validates SCAP data stream processing
- Shows which rules would be remediated
- **Use when**: Remediations aren't being generated

### Comprehensive Diagnostic

**full_diagnostic.yml**
- Complete system diagnostic
- Checks all components (SCAP content, parsing, scripts, variables)
- Validates role configuration
- Tests all hardening phases
- **Use when**: Multiple issues or unknown root cause

## How to Run

### Basic Usage

```bash
# Run score diagnostic
ansible-playbook -i inventory playbooks/diagnostics/check_score_calculation.yml

# Run remediation diagnostic
ansible-playbook -i inventory playbooks/diagnostics/benchmark_remediation_diagnostic.yml

# Run full diagnostic
ansible-playbook -i inventory playbooks/diagnostics/full_diagnostic.yml
```

### With Specific Benchmark

```bash
# Diagnose CIS Server L1 issues
ansible-playbook -i inventory playbooks/diagnostics/benchmark_remediation_diagnostic.yml \
  -e rhel_stig_with_rollback_benchmark_profile=cis_server_l1

# Debug DISA STIG scores
ansible-playbook -i inventory playbooks/diagnostics/debug_oscap_score.yml \
  -e rhel_stig_with_rollback_benchmark_profile=stig
```

## Interpreting Results

### Score Diagnostics

Look for:
- **Pass/Fail counts** - Should match expected rule counts
- **Parsing method** - Native vs Python (native is preferred)
- **XML validation** - File exists and is readable
- **Score calculation** - Pass / (Pass + Fail) * 100

### Remediation Diagnostics

Look for:
- **SCAP content** - `/usr/share/xml/scap/ssg/content/ssg-rhel*.xml` exists
- **Profile ID** - Correct XCCDF profile being used
- **Rule selection** - Expected rules being targeted
- **Script generation** - Remediation script created successfully

### Full Diagnostic

Provides:
- System information (RHEL version, packages)
- SCAP content validation
- Role variable status
- Native parsing capability
- All diagnostic test results

## Common Issues

### Issue: Score shows 0% but rules passed
**Diagnostic**: `debug_oscap_score.yml`
**Likely cause**: XML file not found or parsing failed
**Solution**: Check audit directory and file permissions

### Issue: Remediation script empty
**Diagnostic**: `benchmark_remediation_diagnostic.yml`
**Likely cause**: Wrong profile ID or SCAP content missing
**Solution**: Verify SCAP content installed and profile ID correct

### Issue: Different scores on each run
**Diagnostic**: `diagnose_score_issue.yml`
**Likely cause**: Rule results changing or caching issue
**Solution**: Compare XML files between runs

## Output Locations

Diagnostic playbooks create output in:
- `/opt/stig_audit/` - Audit XML and HTML reports
- `/opt/stig_work/` - Working files and scripts
- `/tmp/diagnostic_*` - Temporary diagnostic files

## Need More Help?

See:
- `docs/operations/TROUBLESHOOTING.md` - Complete troubleshooting guide
- `docs/guides/BENCHMARK_GUIDE.md` - Benchmark-specific issues
- `docs/reference/ROLE_DOCUMENTATION.md` - Role internals
