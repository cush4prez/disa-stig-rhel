#!/usr/bin/env python3
"""
OSCAP Score Parser - Simple Version
Uses the native <score> element from OSCAP XML
"""

import sys
import os
import xml.etree.ElementTree as ET


def get_tag(element):
    """Extract tag name from namespaced XML elements"""
    return element.tag.split('}')[-1] if '}' in element.tag else element.tag


def parse_oscap_score(xml_file):
    """
    Parse OSCAP XML and extract the native score element.
    This is what OSCAP itself calculates.
    """
    if not os.path.exists(xml_file):
        print(f"Error: File not found: {xml_file}", file=sys.stderr)
        return 0.0

    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Find the <score> element
        for elem in root.iter():
            if get_tag(elem) == 'score':
                score_text = elem.text.strip() if elem.text else '0'
                try:
                    # OSCAP scores are 0-100
                    score = float(score_text)
                    print(f"Debug: Found <score> element: {score}", file=sys.stderr)
                    return round(score, 2)
                except ValueError:
                    print(f"Debug: Invalid score value: {score_text}", file=sys.stderr)
                    continue

        print("Warning: No <score> element found", file=sys.stderr)
        return 0.0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 0.0


def main():
    if len(sys.argv) != 2:
        print("Usage: parse_oscap_score_simple.py <xml_file>", file=sys.stderr)
        print("0.0")
        sys.exit(0)

    score = parse_oscap_score(sys.argv[1])
    print(f"{score}")


if __name__ == "__main__":
    main()
