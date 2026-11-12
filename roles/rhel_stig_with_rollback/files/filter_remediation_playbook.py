#!/usr/bin/env python3
"""Filter OpenSCAP bash remediation script to include only specified STIG rules."""

import re
import sys


def normalize_rule_id(rule_id: str) -> str:
    """Strip standard XCCDF rule prefix so short and full IDs match identically."""
    rule_id = rule_id.strip().strip("'\"")
    return re.sub(r"^.*_rule_", "", rule_id)


def main() -> int:
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <input_script> <output_script> <comma_separated_rules>", file=sys.stderr)
        return 1

    input_path, output_path, rules_arg = sys.argv[1], sys.argv[2], sys.argv[3]
    requested_rules = {
        normalize_rule_id(r)
        for r in rules_arg.split(",")
        if r.strip()
    }

    if not requested_rules:
        print("ERROR: No valid rule IDs provided for filtering.", file=sys.stderr)
        return 1

    with open(input_path, "r", encoding="utf-8", errors="replace") as infile:
        lines = infile.readlines()

    # Matches quoted, unquoted, and numbered OpenSCAP bash headers:
    #   # BEGIN fix for 'xccdf_org.ssgproject.content_rule_banner_etc_issue'
    #   # BEGIN fix (1 / 342) for 'xccdf_org.ssgproject.content_rule_banner_etc_issue'
    #   # BEGIN fix (1 / 342) for xccdf_org.ssgproject.content_rule_banner_etc_issue
    begin_pattern = re.compile(r"^#\s*BEGIN fix(?:\s*\(\d+\s*/\s*\d+\))?\s+for\s+['\"]?([^\s'\"]+)['\"]?")
    end_pattern = re.compile(r"^#\s*END fix(?:\s*\(\d+\s*/\s*\d+\))?\s+for\s+['\"]?([^\s'\"]+)['\"]?")

    header_lines = []
    matched_blocks = []
    matched_rule_names = set()

    in_header = True
    in_block = False
    keep_current_block = False
    current_block = []

    for line in lines:
        begin_match = begin_pattern.match(line)
        end_match = end_pattern.match(line)

        if begin_match:
            in_header = False
            in_block = True
            raw_rule = begin_match.group(1)
            short_rule = normalize_rule_id(raw_rule)
            keep_current_block = short_rule in requested_rules
            current_block = [line]
            if keep_current_block:
                matched_rule_names.add(short_rule)
            continue

        if in_block:
            current_block.append(line)
            if end_match:
                if keep_current_block:
                    matched_blocks.extend(current_block)
                    matched_blocks.append("\n")
                in_block = False
                keep_current_block = False
                current_block = []
            continue

        if in_header:
            header_lines.append(line)

    with open(output_path, "w", encoding="utf-8") as outfile:
        if not header_lines or not header_lines[0].startswith("#!"):
            outfile.write("#!/bin/bash\n")
        outfile.writelines(header_lines)
        outfile.write("\n")
        outfile.writelines(matched_blocks)

    missing = requested_rules - matched_rule_names
    print(f"Requested rules: {len(requested_rules)}")
    print(f"Matched rules in remediation script: {len(matched_rule_names)}")
    if matched_rule_names:
        print("Included:", ", ".join(sorted(matched_rule_names)))
    if missing:
        print("Not found in remediation script:", ", ".join(sorted(missing)))

    return 0 if matched_rule_names else 2


if __name__ == "__main__":
    sys.exit(main())
