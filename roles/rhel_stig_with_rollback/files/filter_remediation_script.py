#!/usr/bin/env python3
"""
Filter OSCAP bash remediation script to include only specific STIG rules.

Usage: filter_remediation_script.py <input_script.sh> <output_script.sh> <comma_separated_rule_ids>

Example:
  filter_remediation_script.py full.sh filtered.sh sysctl_crypto_fips_enabled,audit_rules_login_events
"""

import sys
import re


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


def extract_rule_blocks(script_content):
    """
    Extract rule blocks from an OSCAP-generated bash script.
    Returns a dict mapping rule_id -> (start_line, end_line, block_text)
    """
    blocks = {}
    current_rule = None
    current_block_start = None
    current_block_lines = []

    lines = script_content.split('\n')

    for i, line in enumerate(lines):
        # Look for rule start markers like:
        # # BEGIN fix (3 / 294) for 'xccdf_org.ssgproject.content_rule_accounts_password_minlen_login_defs'
        # or comments with rule IDs
        match = re.search(r"xccdf_org\.ssgproject\.content_rule_(\w+)", line)

        if match and ('BEGIN' in line or 'Remediation for' in line):
            # Save previous block if exists
            if current_rule and current_block_lines:
                blocks[current_rule] = (current_block_start, i - 1, '\n'.join(current_block_lines))

            # Start new block
            current_rule = match.group(1)
            current_block_start = i
            current_block_lines = [line]

        elif current_rule:
            # Continue collecting lines for current block
            current_block_lines.append(line)

            # Look for block end markers
            if 'END fix' in line or (line.strip().startswith('#') and 'END' in line):
                blocks[current_rule] = (current_block_start, i, '\n'.join(current_block_lines))
                current_rule = None
                current_block_start = None
                current_block_lines = []

    # Save final block if exists
    if current_rule and current_block_lines:
        blocks[current_rule] = (current_block_start, len(lines) - 1, '\n'.join(current_block_lines))

    return blocks


def filter_script(input_file, output_file, rule_ids_to_include):
    """
    Filter a bash remediation script to only include specific rule IDs.
    """
    # Read input script
    with open(input_file, 'r') as f:
        script_content = f.read()

    # Normalize requested rule IDs
    normalized_requests = set(shorten_rule_id(rid.strip()) for rid in rule_ids_to_include)

    # Extract rule blocks
    blocks = extract_rule_blocks(script_content)

    print(f"Found {len(blocks)} rule blocks in script", file=sys.stderr)
    print(f"Requested {len(rule_ids_to_include)} rules", file=sys.stderr)

    # Find matching blocks
    matched_blocks = {}
    matched_rules = set()

    for rule_id in normalized_requests:
        if rule_id in blocks:
            matched_blocks[rule_id] = blocks[rule_id]
            matched_rules.add(rule_id)

    print(f"Matched {len(matched_blocks)} rules", file=sys.stderr)

    # Check for rules not found
    not_found = normalized_requests - matched_rules
    if not_found:
        print("", file=sys.stderr)
        print("⚠️  WARNING: Some requested rules were not found:", file=sys.stderr)
        for rule_id in sorted(not_found):
            print(f"  - {rule_id}", file=sys.stderr)

    if not matched_blocks:
        print("", file=sys.stderr)
        print("❌ ERROR: No matching rule blocks found!", file=sys.stderr)
        print("This likely means the rule IDs don't match the script.", file=sys.stderr)
        sys.exit(1)

    # Build filtered script
    # Start with shebang and header
    filtered_lines = [
        "#!/bin/bash",
        "# FILTERED REMEDIATION SCRIPT",
        f"# Original rules: {len(blocks)}",
        f"# Filtered rules: {len(matched_blocks)}",
        "#",
        "# Selected rules:"
    ]

    for rule_id in sorted(rule_ids_to_include):
        filtered_lines.append(f"#   - {rule_id}")

    filtered_lines.append("#")
    filtered_lines.append("")

    # Add matched blocks in order
    for rule_id in sorted(matched_rules):
        start, end, block_text = matched_blocks[rule_id]
        filtered_lines.append(block_text)
        filtered_lines.append("")  # Add blank line between blocks

    # Write filtered script
    with open(output_file, 'w') as f:
        f.write('\n'.join(filtered_lines))

    print("", file=sys.stderr)
    print(f"✅ Filtered script created: {output_file}", file=sys.stderr)
    print(f"   Included {len(matched_blocks)} rule blocks", file=sys.stderr)

    # Return stats for Ansible
    print(f"FILTERED: {len(matched_blocks)} rules")


def main():
    if len(sys.argv) != 4:
        print("Usage: filter_remediation_script.py <input_script.sh> <output_script.sh> <comma_separated_rule_ids>", file=sys.stderr)
        print("", file=sys.stderr)
        print("Example:", file=sys.stderr)
        print("  filter_remediation_script.py full.sh filtered.sh sysctl_crypto_fips_enabled,audit_rules_login_events", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    rule_ids_str = sys.argv[3]

    # Parse comma-separated rule IDs
    rule_ids = [rid.strip() for rid in rule_ids_str.split(',') if rid.strip()]

    if not rule_ids:
        print("ERROR: No rule IDs provided", file=sys.stderr)
        sys.exit(1)

    try:
        filter_script(input_file, output_file, rule_ids)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
