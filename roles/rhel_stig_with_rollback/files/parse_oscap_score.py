#!/usr/bin/env python3
"""
OSCAP STIG Compliance Score Parser
Correctly calculates compliance based on pass/fail rule counts
The <score> element in OSCAP XML can be misleading - it may include
notapplicable and notchecked rules which inflates the score artificially.

Correct calculation: (pass_count / (pass_count + fail_count)) * 100
"""

import sys
import os
import xml.etree.ElementTree as ET


def get_tag(element):
    """Extract tag name from namespaced XML elements"""
    return element.tag.split('}')[-1] if '}' in element.tag else element.tag


def parse_oscap_compliance(xml_file):
    """
    Parse OSCAP XML results file and calculate TRUE compliance score
    based on actual pass/fail counts, not the <score> element

    Args:
        xml_file (str): Path to OSCAP XML results file

    Returns:
        float: Compliance score (0.0-100.0) based on pass/(pass+fail)
    """
    # Validation checks
    if not os.path.exists(xml_file):
        print(f"Warning: XML file not found: {xml_file}", file=sys.stderr)
        return 0.0

    if not os.access(xml_file, os.R_OK):
        print(f"Warning: XML file not readable: {xml_file}", file=sys.stderr)
        return 0.0

    if os.path.getsize(xml_file) == 0:
        print(f"Warning: XML file is empty: {xml_file}", file=sys.stderr)
        return 0.0

    try:
        # Parse XML
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Count rule results
        pass_count = 0
        fail_count = 0
        notapplicable_count = 0
        notchecked_count = 0
        error_count = 0

        for elem in root.iter():
            if get_tag(elem) == 'result':
                result_text = elem.text.strip().lower() if elem.text else ''

                if result_text == 'pass':
                    pass_count += 1
                elif result_text == 'fail':
                    fail_count += 1
                elif result_text == 'notapplicable':
                    notapplicable_count += 1
                elif result_text == 'notchecked':
                    notchecked_count += 1
                elif result_text == 'error':
                    error_count += 1

        # Calculate compliance based on checked rules only (pass + fail)
        checked_rules = pass_count + fail_count

        if checked_rules == 0:
            print(f"Warning: No rules were checked (pass=0, fail=0)", file=sys.stderr)
            return 0.0

        # True compliance = pass / (pass + fail) * 100
        compliance = (pass_count / checked_rules) * 100

        # Debug output to stderr (won't interfere with stdout score)
        print(f"Debug: Pass={pass_count}, Fail={fail_count}, "
              f"NotApplicable={notapplicable_count}, NotChecked={notchecked_count}, "
              f"Error={error_count}", file=sys.stderr)
        print(f"Debug: Compliance = {pass_count}/{checked_rules} = {compliance:.2f}%",
              file=sys.stderr)

        return round(compliance, 2)

    except ET.ParseError as e:
        print(f"Warning: XML parsing error: {e}", file=sys.stderr)
        return 0.0
    except Exception as e:
        print(f"Warning: Unexpected error: {e}", file=sys.stderr)
        return 0.0


def main():
    """Main entry point"""
    if len(sys.argv) != 2:
        print("Usage: parse_oscap_score_fixed.py <xml_file>", file=sys.stderr)
        print("0.0")
        sys.exit(0)

    xml_file = sys.argv[1]
    score = parse_oscap_compliance(xml_file)

    # Output only the score to stdout (for Ansible to capture)
    print(f"{score}")


if __name__ == "__main__":
    main()
