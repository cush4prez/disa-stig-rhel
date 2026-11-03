#!/usr/bin/env python3
"""
OSCAP STIG Failures Parser
Extracts failed rules grouped by severity (CAT I, II, III)
Correctly maps DISA STIG V-IDs to Ansible playbook variables.
"""

import sys
import os
import xml.etree.ElementTree as ET
import json


def get_tag(element):
    """Extract tag name from namespaced XML elements"""
    return element.tag.split('}')[-1] if '}' in element.tag else element.tag


def get_namespace(element):
    """Extract namespace from element tag"""
    if '}' in element.tag:
        return element.tag.split('}')[0] + '}'
    return ''


def severity_to_category(severity):
    """Convert OSCAP severity to DISA CAT"""
    severity_map = {
        'high': 'CAT I',
        'medium': 'CAT II',
        'low': 'CAT III',
        'unknown': 'CAT III'
    }
    return severity_map.get(severity.lower() if severity else 'unknown', 'CAT III')


def extract_stig_id(rule_element):
    """
    Extract STIG ID from rule references.
    Prioritizes V-IDs and RHEL-IDs while explicitly ignoring OS-SRG and CCI values.
    """
    best_match = None
    
    for child in rule_element.iter():
        tag = get_tag(child)
        
        if tag in ['ident', 'reference']:
            text_val = child.text.strip() if child.text else ''
            
            # Explicitly ignore SRG and CCI references
            if text_val.startswith('SRG-') or text_val.startswith('CCI-'):
                continue
                
            # 1. Direct match for standard DISA V-IDs (e.g., V-230222) or SV-IDs
            if text_val.startswith('V-') or text_val.startswith('SV-'):
                return text_val
            
            # 2. Direct match for RHEL-specific STIG IDs (e.g., RHEL-09-232000)
            if text_val.startswith('RHEL-'):
                return text_val
                
            # 3. Fallback: If the tag explicitly has a stigRef role and isn't an SRG
            if child.get('role', '').lower() == 'stigref':
                best_match = text_val
                
    return best_match


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


def parse_oscap_failures(xml_file):
    """
    Parse OSCAP XML and extract failed rules grouped by severity category.
    """
    if not os.path.exists(xml_file):
        print(f"Error: File not found: {xml_file}", file=sys.stderr)
        return None

    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Storage for failures by category
        failures = {
            'cat1': [],
            'cat2': [],
            'cat3': [],
            'pass_count': 0,
            'fail_count': 0,
            'notapplicable_count': 0,
            'notchecked_count': 0
        }

        # Build rule metadata map (id -> severity, title, stig_id)
        rule_metadata = {}

        # Find all <Rule> elements in the Benchmark section
        for rule in root.iter():
            if get_tag(rule) == 'Rule':
                rule_id = rule.get('id', '')
                severity = rule.get('severity', 'unknown')

                # Get rule title
                title = ''
                for child in rule:
                    if get_tag(child) == 'title':
                        title = child.text or rule_id
                        break

                rule_metadata[rule_id] = {
                    'severity': severity,
                    'title': title,
                    'stig_id': extract_stig_id(rule),
                    'short_id': shorten_rule_id(rule_id),
                    'category': severity_to_category(severity)
                }

        # Find TestResult section and parse rule-result elements
        for test_result in root.iter():
            if get_tag(test_result) == 'TestResult':
                for rule_result in test_result:
                    if get_tag(rule_result) == 'rule-result':
                        rule_id = rule_result.get('idref', '')

                        # Get result
                        result = None
                        for elem in rule_result:
                            if get_tag(elem) == 'result':
                                result = elem.text.strip().lower() if elem.text else ''
                                break

                        # Count results
                        if result == 'pass':
                            failures['pass_count'] += 1
                        elif result == 'fail':
                            failures['fail_count'] += 1

                            # Get rule metadata
                            metadata = rule_metadata.get(rule_id, {
                                'severity': 'unknown',
                                'title': rule_id,
                                'stig_id': None,
                                'short_id': shorten_rule_id(rule_id),
                                'category': 'CAT III'
                            })

                            # Build payload matching the Ansible playbook's expectations
                            failure_info = {
                                'id': metadata['short_id'],
                                'stig_id': metadata['stig_id'] if metadata['stig_id'] else 'N/A',
                                'title': metadata['title'],
                                'severity': metadata['severity']
                            }

                            # Add to appropriate category
                            category = metadata['category']
                            if category == 'CAT I':
                                failures['cat1'].append(failure_info)
                            elif category == 'CAT II':
                                failures['cat2'].append(failure_info)
                            else:  # CAT III
                                failures['cat3'].append(failure_info)

                        elif result == 'notapplicable':
                            failures['notapplicable_count'] += 1
                        elif result == 'notchecked':
                            failures['notchecked_count'] += 1

        # Calculate compliance
        total_checked = failures['pass_count'] + failures['fail_count']
        if total_checked > 0:
            compliance = (failures['pass_count'] / total_checked) * 100
            failures['compliance'] = round(compliance, 2)
        else:
            failures['compliance'] = 0.0

        return failures

    except Exception as e:
        print(f"Error parsing XML: {e}", file=sys.stderr)
        return None


def main():
    if len(sys.argv) != 2:
        print("Usage: parse_oscap_failures.py <xml_file>", file=sys.stderr)
        sys.exit(1)

    xml_file = sys.argv[1]
    failures = parse_oscap_failures(xml_file)

    if failures is None:
        sys.exit(1)

    # Output as JSON for Ansible to parse
    print(json.dumps(failures, indent=2))


if __name__ == "__main__":
    main()