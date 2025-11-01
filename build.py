#!/usr/bin/env python3
import os
import ruamel.yaml

def merge_dicts(a, b):
    """
    Recursively merge dictionary b into dictionary a.
    If both have the same key and both are dicts, merge recursively.
    If both are lists, extend the list.
    Otherwise, b's value overwrites a's.
    """
    for key, value in b.items():
        if key in a:
            if isinstance(a[key], dict) and isinstance(value, dict):
                merge_dicts(a[key], value)
            elif isinstance(a[key], list) and isinstance(value, list):
                a[key].extend(value)
            else:
                a[key] = value
        else:
            a[key] = value
    return a

def replace_secrets(data, secrets):
    """
    Recursively replace {{TAG}} placeholders with secret values.
    """
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, str):
                for tag, value in secrets.items():
                    placeholder = "{{" + tag + "}}"
                    if placeholder in v:
                        data[k] = v.replace(placeholder, value)
            else:
                replace_secrets(v, secrets)
    elif isinstance(data, list):
        for item in data:
            replace_secrets(item, secrets)

def main():
    src_dir = 'src'
    bin_dir = 'bin'
    output_file = os.path.join(bin_dir, 'ipixel-esphome.yaml')
    secrets_file = 'secrets.txt'

    # Ensure bin directory exists
    os.makedirs(bin_dir, exist_ok=True)

    yaml = ruamel.yaml.YAML()
    yaml.preserve_quotes = False  # Do not preserve quotes
    yaml.indent(mapping=2, sequence=4, offset=2)  # Nice indentation

    # Parse secrets.txt
    secrets = {}
    if os.path.exists(secrets_file):
        with open(secrets_file, 'r') as f:
            for line in f:
                line = line.strip()
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    secrets[key] = value
        print(f"📁 Loaded secrets from {secrets_file}")

    merged_data = {}

    # List all YAML files in src root
    root_yaml_files = [f for f in os.listdir(src_dir) if f.endswith('.yaml') or f.endswith('.yml') and os.path.isfile(os.path.join(src_dir, f))]
    root_yaml_files.sort()  # Sort for consistent order

    # List all YAML files in src/commands
    commands_dir = os.path.join(src_dir, 'commands')
    commands_yaml_files = []
    if os.path.exists(commands_dir):
        commands_yaml_files = [f for f in os.listdir(commands_dir) if f.endswith('.yaml') or f.endswith('.yml') and os.path.isfile(os.path.join(commands_dir, f))]
        commands_yaml_files.sort()  # Sort for consistent order

    # Combine: root files first, then commands
    yaml_files = root_yaml_files + commands_yaml_files

    for filename in yaml_files:
        if filename in root_yaml_files:
            filepath = os.path.join(src_dir, filename)
        else:
            filepath = os.path.join(commands_dir, filename)
        print(f"📁 Loading {filepath}")
        with open(filepath, 'r') as f:
            data = yaml.load(f)
            if data:
                merge_dicts(merged_data, data)

    # Replace {{TAG}} placeholders with secret values
    replace_secrets(merged_data, secrets)

    # Write the merged data to output file
    with open(output_file, 'w') as f:
        yaml.dump(merged_data, f)

    print(f"✅ Merged YAML written to {output_file}")

if __name__ == '__main__':
    main()
