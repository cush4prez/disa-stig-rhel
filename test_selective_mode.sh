#!/bin/bash
# Test script for selective mode

echo "=========================================="
echo "Testing Selective Mode Variable Processing"
echo "=========================================="
echo ""

# Test 1: With stig_audit_mode and stig_rules_input (AAP survey style)
echo "TEST 1: AAP Survey Style (stig_audit_mode='selective', stig_rules_input='rule1,rule2')"
echo "---"
ansible-playbook -i inventory playbooks/diagnostics/debug_selective_mode.yml \
  -e "stig_audit_mode=selective" \
  -e "stig_rules_input='sysctl_crypto_fips_enabled,audit_rules_login_events'" \
  --limit rhel9-base.myhome.lab

echo ""
echo "=========================================="
echo ""

# Test 2: Direct variable setting (bypassing site.yml conversion)
echo "TEST 2: Direct Variable (rhel_stig_with_rollback_stig_rules_to_apply=['rule1','rule2'])"
echo "---"
ansible-playbook -i inventory playbooks/diagnostics/debug_selective_mode.yml \
  -e "rhel_stig_with_rollback_stig_rules_to_apply=['sysctl_crypto_fips_enabled','audit_rules_login_events']" \
  --limit rhel9-base.myhome.lab

echo ""
echo "=========================================="
echo ""

# Test 3: Full mode (no rules)
echo "TEST 3: Full Mode (stig_audit_mode='full')"
echo "---"
ansible-playbook -i inventory playbooks/diagnostics/debug_selective_mode.yml \
  -e "stig_audit_mode=full" \
  --limit rhel9-base.myhome.lab

echo ""
echo "=========================================="
echo "DONE - Check outputs above"
echo "=========================================="
