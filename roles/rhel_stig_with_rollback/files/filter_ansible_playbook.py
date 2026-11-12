#!/usr/bin/env python3
"""
Filter OSCAP-generated Ansible playbook to include only specific STIG rules.

Usage: filter_ansible_playbook.py <input_playbook.yml> <output_playbook.yml> <comma_separated_rule_ids>

Example:
  filter_ansible_playbook.py full.yml filtered.yml sysctl_crypto_fips_enabled,audit_rules_login_events
"""

import sys
import re
import yaml


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


def extract_rule_id_from_task(task):
    """
    Extract rule ID from an OSCAP-generated task.
    Looks in task name or tags.
    """
    # Check task name for pattern like "xccdf_org.ssgproject.content_rule_..."
    if 'name' in task:
        name = task['name']
        if 'xccdf_' in name and '_rule_' in name:
            # Extract the ID from the name
            match = re.search(r'(xccdf_org\.ssgproject\.content_rule_\w+)', name)
            if match:
                return shorten_rule_id(match.group(1))

    # Check tags
    if 'tags' in task:
        for tag in task['tags']:
            if isinstance(tag, str):
                if 'xccdf_' in tag and '_rule_' in tag:
                    return shorten_rule_id(tag)
                # Sometimes tags are already shortened
                if not tag.startswith('xccdf_') and not tag.startswith('CCE-'):
                    return tag

    return None


def filter_playbook(input_file, output_file, rule_ids_to_include):
    """
    Filter an Ansible playbook to only include tasks for specific rule IDs.
    """
    # Read input playbook
    try:
        with open(input_file, 'r') as f:
            playbook_data = yaml.safe_load(f)
    except Exception as e:
        print(f"ERROR: Failed to parse input playbook: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(playbook_data, list) or len(playbook_data) == 0:
        print("ERROR: Invalid playbook format - expected a list with at least one play", file=sys.stderr)
        sys.exit(1)

    # Get the play (should be a single play)
    play = playbook_data[0]

    if 'tasks' not in play:
        print("ERROR: No tasks found in playbook", file=sys.stderr)
        sys.exit(1)

    # Normalize requested rule IDs
    normalized_requests = set(shorten_rule_id(rid.strip()) for rid in rule_ids_to_include)

    # Filter tasks
    original_task_count = len(play['tasks'])
    filtered_tasks = []
    matched_rules = set()

    for task in play['tasks']:
        rule_id = extract_rule_id_from_task(task)

        if rule_id and rule_id in normalized_requests:
            filtered_tasks.append(task)
            matched_rules.add(rule_id)

    # Report results
    print(f"Original tasks: {original_task_count}", file=sys.stderr)
    print(f"Requested rules: {len(rule_ids_to_include)}", file=sys.stderr)
    print(f"Matched tasks: {len(filtered_tasks)}", file=sys.stderr)
    print(f"Matched rules: {len(matched_rules)}", file=sys.stderr)

    # Check for rules not found
    not_found = normalized_requests - matched_rules
    if not_found:
        print("", file=sys.stderr)
        print("⚠️  WARNING: Some requested rules were not found:", file=sys.stderr)
        for rule_id in sorted(not_found):
            print(f"  - {rule_id}", file=sys.stderr)

    if not filtered_tasks:
        print("", file=sys.stderr)
        print("❌ ERROR: No matching tasks found!", file=sys.stderr)
        print("This likely means the rule IDs don't match the playbook.", file=sys.stderr)
        sys.exit(1)

    # Update play with filtered tasks
    play['tasks'] = filtered_tasks

    # Add comment to play name
    if 'name' in play:
        play['name'] = f"{play['name']} (FILTERED: {len(filtered_tasks)} tasks)"
    else:
        play['name'] = f"STIG Remediation (FILTERED: {len(filtered_tasks)} tasks)"

    # Write filtered playbook
    with open(output_file, 'w') as f:
        # Add header comment
        f.write("---\n")
        f.write("# FILTERED REMEDIATION PLAYBOOK\n")
        f.write(f"# Original tasks: {original_task_count}\n")
        f.write(f"# Filtered tasks: {len(filtered_tasks)}\n")
        f.write("#\n")
        f.write("# Selected rules:\n")
        for rule_id in sorted(rule_ids_to_include):
            f.write(f"#   - {rule_id}\n")
        f.write("#\n")
        f.write("\n")

        # Write playbook
        yaml.dump(playbook_data, f, default_flow_style=False, sort_keys=False)

    print("", file=sys.stderr)
    print(f"✅ Filtered playbook created: {output_file}", file=sys.stderr)
    print(f"   Included {len(filtered_tasks)} tasks for {len(matched_rules)} rules", file=sys.stderr)

    # Return stats for Ansible
    print(f"FILTERED: {len(filtered_tasks)} tasks")
    print(f"RULES: {len(matched_rules)} rules")


def main():
    if len(sys.argv) != 4:
        print("Usage: filter_ansible_playbook.py <input_playbook.yml> <output_playbook.yml> <comma_separated_rule_ids>", file=sys.stderr)
        print("", file=sys.stderr)
        print("Example:", file=sys.stderr)
        print("  filter_ansible_playbook.py full.yml filtered.yml sysctl_crypto_fips_enabled,audit_rules_login_events", file=sys.stderr)
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
        filter_playbook(input_file, output_file, rule_ids)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
