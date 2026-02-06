#!/usr/bin/env python3
"""
ODCS Contract Generator - Creates new ODCS contract scaffolds

Usage:
    new_contract.py <output.yaml> [--name NAME] [--domain DOMAIN] [--minimal]

Examples:
    new_contract.py my-contract.odcs.yaml
    new_contract.py orders.odcs.yaml --name "Orders Data" --domain sales
    new_contract.py minimal.odcs.yaml --minimal
"""

import sys
import uuid
import argparse
from datetime import datetime, timezone
from pathlib import Path


MINIMAL_TEMPLATE = """apiVersion: v3.1.0
kind: DataContract
id: {id}
version: 1.0.0
status: draft
schema:
  - name: {table_name}
    logicalType: object
    description: TODO - Add table description
    properties:
      - name: id
        logicalType: integer
        primaryKey: true
        required: true
        description: Primary key
"""

FULL_TEMPLATE = """# ODCS v3.1.0 Data Contract
# Generated: {timestamp}

apiVersion: v3.1.0
kind: DataContract
id: {id}
version: 1.0.0
status: draft

# Metadata
name: {name}
domain: {domain}
dataProduct: {data_product}
tenant: {tenant}
tags: []

description:
  purpose: TODO - Describe the intended use of this data
  limitations: TODO - Document any constraints or limitations
  usage: TODO - Describe recommended usage patterns

# Schema Definition
schema:
  - name: {table_name}
    id: {table_name}_tbl
    logicalType: object
    physicalType: table
    businessName: TODO - Business friendly name
    description: TODO - Add table description
    dataGranularityDescription: TODO - e.g., One row per transaction

    properties:
      - name: id
        id: id_col
        logicalType: integer
        physicalType: bigint
        primaryKey: true
        primaryKeyPosition: 1
        required: true
        unique: true
        description: Unique identifier
        classification: public

      # TODO: Add more columns
      # - name: column_name
      #   logicalType: string|number|integer|date|timestamp|boolean
      #   physicalType: varchar(255)
      #   required: true|false
      #   description: Column description

# Data Quality Rules (optional)
# quality:
#   - type: library
#     metric: rowCount
#     mustBeGreaterThan: 0
#     dimension: completeness
#     severity: error

# Server Configuration (optional)
# servers:
#   - server: my-database
#     type: postgres
#     host: localhost
#     port: 5432
#     database: mydb
#     schema: public
#     environment: dev

# SLA Properties (optional)
# slaProperties:
#   - property: latency
#     value: 24
#     unit: d
#   - property: retention
#     value: 7
#     unit: y

# Team (optional)
# team:
#   name: data-team
#   members:
#     - username: owner@company.com
#       role: Owner
#       dateIn: "{date}"

# Roles (optional)
# roles:
#   - role: read_access
#     access: read
#     description: Read access for analytics

# Support Channels (optional)
# support:
#   - channel: "#data-help"
#     tool: slack
#     scope: interactive

contractCreatedTs: "{timestamp}"
"""


def generate_contract(output_path, name=None, domain=None, minimal=False):
    """
    Generate a new ODCS contract scaffold.

    Args:
        output_path: Path for the output YAML file
        name: Optional data product name
        domain: Optional business domain
        minimal: If True, generate minimal contract

    Returns:
        Path to created file
    """
    output_path = Path(output_path)

    # Check if file exists
    if output_path.exists():
        print(f"❌ Error: File already exists: {output_path}")
        return None

    # Generate values
    contract_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Derive names from filename if not provided
    base_name = output_path.stem.replace('.odcs', '').replace('-', '_').replace(' ', '_')
    table_name = base_name if base_name else "my_table"
    name = name or base_name.replace('_', ' ').title()
    domain = domain or "TODO"
    data_product = base_name
    tenant = "TODO"

    # Select template
    if minimal:
        content = MINIMAL_TEMPLATE.format(
            id=contract_id,
            table_name=table_name
        )
    else:
        content = FULL_TEMPLATE.format(
            id=contract_id,
            timestamp=timestamp,
            date=date,
            name=name,
            domain=domain,
            data_product=data_product,
            tenant=tenant,
            table_name=table_name
        )

    # Write file
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content)
        print(f"✅ Created contract: {output_path}")
        return output_path
    except Exception as e:
        print(f"❌ Error writing file: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Generate new ODCS contract scaffolds"
    )
    parser.add_argument(
        "output",
        help="Output path for the YAML contract file"
    )
    parser.add_argument(
        "--name", "-n",
        help="Data product name"
    )
    parser.add_argument(
        "--domain", "-d",
        help="Business domain"
    )
    parser.add_argument(
        "--minimal", "-m",
        action="store_true",
        help="Generate minimal contract (fewer fields)"
    )

    args = parser.parse_args()

    result = generate_contract(
        args.output,
        name=args.name,
        domain=args.domain,
        minimal=args.minimal
    )

    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
