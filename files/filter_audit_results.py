#!/usr/bin/env python3
"""
Filter OSCAP audit results to show only specific STIG rules.

Usage: filter_audit_results.py <audit_xml> <comma_separated_rule_ids>

Returns JSON:
{
  "found": ["rule1", "rule2"],
  "not_found": ["rule3"],
  "pass": ["rule1"],
  "fail": ["rule2"],
  "notapplicable": [],
  "notchecked": []
}
"""

import sys
import os
import xml.etree.ElementTree as ET
import json


def get_tag(element):
    """Extract tag name from namespaced XML elements"""
    return element.tag.split('}')[-1] if '}' in element.tag else element.tag


def shorten_rule_id(full_id):
    """
    Shorten OSCAP rule ID to just the meaningful part.
    xccdf_org.ssgproject.content_rule_sysctl_crypto_fips_enabled -> sysctl_crypto_fips_enabled
    """
    if 'xccdf_' in full_id and '_rule_' in full_id:
        parts = full_id.split('_rule_')
        if len(parts) == 2:
            return parts[1]
    return full_id


def filter_audit_results(xml_file, rule_ids_to_find):
    """
    Parse OSCAP XML and filter for specific rule IDs.
    """
    if not os.path.exists(xml_file):
        print(f"Error: File not found: {xml_file}", file=sys.stderr)
        return None

    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        results = {
            'found': [],
            'not_found': [],
            'pass': [],
            'fail': [],
            'notapplicable': [],
            'notchecked': []
        }

        # Normalize requested rule IDs (strip xccdf prefix if present)
        normalized_requests = set()
        for rid in rule_ids_to_find:
            normalized_requests.add(shorten_rule_id(rid))

        # Track what we've found
        found_rules = {}

        # Find TestResult section and parse rule-result elements
        for test_result in root.iter():
            if get_tag(test_result) == 'TestResult':
                for rule_result in test_result:
                    if get_tag(rule_result) == 'rule-result':
                        rule_id = rule_result.get('idref', '')
                        short_id = shorten_rule_id(rule_id)

                        # Only care about requested rules
                        if short_id not in normalized_requests:
                            continue

                        # Get result
                        result = None
                        for elem in rule_result:
                            if get_tag(elem) == 'result':
                                result = elem.text.strip().lower() if elem.text else ''
                                break

                        # Record the finding
                        if result and short_id not in found_rules:
                            found_rules[short_id] = result
                            results['found'].append(short_id)

                            if result == 'pass':
                                results['pass'].append(short_id)
                            elif result == 'fail':
                                results['fail'].append(short_id)
                            elif result == 'notapplicable':
                                results['notapplicable'].append(short_id)
                            elif result == 'notchecked':
                                results['notchecked'].append(short_id)

        # Determine which rules were not found
        for requested_id in normalized_requests:
            if requested_id not in found_rules:
                results['not_found'].append(requested_id)

        return results

    except Exception as e:
        print(f"Error parsing XML: {e}", file=sys.stderr)
        return None


def main():
    if len(sys.argv) != 3:
        print("Usage: filter_audit_results.py <audit_xml> <comma_separated_rule_ids>", file=sys.stderr)
        print("", file=sys.stderr)
        print("Example:", file=sys.stderr)
        print("  filter_audit_results.py baseline.xml sysctl_crypto_fips_enabled,audit_rules_login_events", file=sys.stderr)
        sys.exit(1)

    xml_file = sys.argv[1]
    rule_ids_str = sys.argv[2]

    # Parse comma-separated rule IDs
    rule_ids = [rid.strip() for rid in rule_ids_str.split(',') if rid.strip()]

    if not rule_ids:
        print("ERROR: No rule IDs provided", file=sys.stderr)
        sys.exit(1)

    results = filter_audit_results(xml_file, rule_ids)

    if results is None:
        sys.exit(1)

    # Output JSON for Ansible
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
