#!/usr/bin/env python3
"""
ODCS Contract Validator - Validates ODCS contracts against JSON schema

Usage:
    validate_contract.py <contract.yaml> [--schema <schema.json>]

Examples:
    validate_contract.py my-contract.odcs.yaml
    validate_contract.py my-contract.odcs.yaml --schema schema/odcs-json-schema-v3.1.0.json
"""

import sys
import json
import argparse
import tempfile
import urllib.request
import urllib.error
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: PyYAML not installed. Run: pip install pyyaml")
    sys.exit(1)

try:
    import jsonschema
    from jsonschema import Draft201909Validator, ValidationError
except ImportError:
    print("Error: jsonschema not installed. Run: pip install jsonschema")
    sys.exit(1)


SCHEMA_URL = "https://raw.githubusercontent.com/bitol-io/open-data-contract-standard/main/schema/odcs-json-schema-v3.1.0.json"


def find_schema_file():
    """Find the ODCS JSON schema file locally or download from GitHub."""
    # Check local schema/ directory (if user has the spec repo checked out)
    local_paths = [
        Path("schema/odcs-json-schema-v3.1.0.json"),
        Path("schema/odcs-json-schema-latest.json"),
    ]

    for path in local_paths:
        resolved = path.resolve()
        if resolved.exists():
            return resolved

    # Download from GitHub
    try:
        print(f"Downloading schema from GitHub...")
        tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        urllib.request.urlretrieve(SCHEMA_URL, tmp.name)
        return Path(tmp.name)
    except urllib.error.URLError as e:
        print(f"Warning: Could not download schema: {e}")
        return None


def validate_contract(contract_path, schema_path=None):
    """
    Validate an ODCS contract against the JSON schema.

    Args:
        contract_path: Path to the ODCS YAML contract
        schema_path: Optional path to JSON schema (auto-detected if not provided)

    Returns:
        Tuple of (is_valid, errors_list)
    """
    contract_path = Path(contract_path)

    # Validate contract file exists
    if not contract_path.exists():
        return False, [f"Contract file not found: {contract_path}"]

    # Find or validate schema path
    schema_is_url = False
    if schema_path:
        if str(schema_path).startswith(("http://", "https://")):
            schema_is_url = True
        else:
            schema_path = Path(schema_path)
            if not schema_path.exists():
                return False, [f"Schema file not found: {schema_path}"]
    else:
        schema_path = find_schema_file()
        if not schema_path:
            return False, [f"Could not find ODCS JSON schema. Use --schema <path-or-url> or download from:\n  {SCHEMA_URL}"]

    # Load contract
    try:
        with open(contract_path, 'r') as f:
            contract = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return False, [f"Invalid YAML: {e}"]

    # Load schema
    try:
        if schema_is_url:
            with urllib.request.urlopen(schema_path) as resp:
                schema = json.loads(resp.read())
        else:
            with open(schema_path, 'r') as f:
                schema = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON schema: {e}"]
    except urllib.error.URLError as e:
        return False, [f"Could not download schema from {schema_path}: {e}"]

    # Validate
    validator = Draft201909Validator(schema)
    errors = list(validator.iter_errors(contract))

    if not errors:
        return True, []

    # Format errors
    error_messages = []
    for error in errors:
        path = " -> ".join(str(p) for p in error.absolute_path) if error.absolute_path else "root"
        error_messages.append(f"  [{path}] {error.message}")

    return False, error_messages


def main():
    parser = argparse.ArgumentParser(
        description="Validate ODCS contracts against JSON schema"
    )
    parser.add_argument(
        "contract",
        help="Path to ODCS contract YAML file"
    )
    parser.add_argument(
        "--schema", "-s",
        help="Path or URL to JSON schema (auto-detected if not provided)"
    )

    args = parser.parse_args()

    print(f"Validating: {args.contract}")

    is_valid, errors = validate_contract(args.contract, args.schema)

    if is_valid:
        print("✅ Contract is valid!")
        sys.exit(0)
    else:
        print("❌ Validation failed:")
        for error in errors:
            print(error)
        sys.exit(1)


if __name__ == "__main__":
    main()
