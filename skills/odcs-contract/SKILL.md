---
name: odcs-contract
description: Create, validate, and maintain Open Data Contract Standard (ODCS) v3.1 contracts. Use when users want to write data contracts, define schemas, add data quality rules, configure servers, set up SLAs, or work with ODCS YAML files. Triggers on requests involving data contracts, ODCS, schema definitions, data quality checks, or data product documentation.
---

# ODCS Contract Writer

Create and maintain Open Data Contract Standard (ODCS) v3.1.0 contracts.

## Quick Start

Generate a minimal valid contract:

```yaml
apiVersion: v3.1.0
kind: DataContract
id: <uuid>
version: 1.0.0
status: draft
schema:
  - name: my_table
    logicalType: object
    properties:
      - name: id
        logicalType: integer
        primaryKey: true
```

## Contract Structure Overview

ODCS contracts have these sections (all optional except fundamentals):

1. **Fundamentals** - Required metadata (apiVersion, kind, id, version, status)
2. **Schema** - Tables, columns, data types, relationships
3. **Quality** - Data quality rules and checks
4. **Servers** - Database/platform connection info
5. **SLA** - Service level agreements
6. **Team** - Team members and roles
7. **Roles** - Access control definitions
8. **Support** - Communication channels
9. **Price** - Pricing information

## Workflow Decision Tree

**Creating new contract?**
1. Start with fundamentals (apiVersion, kind, id, version, status)
2. Add schema with tables and columns
3. Add quality rules as needed
4. Configure servers if deployment known
5. Add SLA, team, roles, support as applicable

**Updating existing contract?**
1. Read the existing contract file
2. Validate current structure
3. Make targeted changes
4. Run validation

**Adding quality rules?**
- See references/quality-rules.md for library metrics and SQL patterns

**Configuring servers?**
- See references/server-types.md for platform-specific configuration

**Defining relationships (foreign keys)?**
- See references/relationships.md for notation and composite key patterns

## Fundamentals (Required)

```yaml
apiVersion: v3.1.0          # Standard version (required)
kind: DataContract          # Fixed value (required)
id: <uuid>                  # Unique identifier (required)
version: 1.0.0              # Contract version, semver (required)
status: draft               # proposed|draft|active|deprecated|retired (required)

# Optional fundamentals
name: my_data_product       # Human-readable name
domain: sales               # Business domain
dataProduct: orders         # Data product name
tenant: MyCompany           # Organization/tenant
tags: [finance, reporting]  # Classification tags
contractCreatedTs: "2024-01-15T10:00:00Z"  # ISO 8601 timestamp

description:
  purpose: Describe intended use
  limitations: Usage constraints
  usage: Recommended usage patterns
```

## Schema Section

Define tables/objects and their columns/properties:

```yaml
schema:
  - name: orders                    # Required: element name
    id: orders_tbl                  # Unique identifier
    logicalType: object             # object|array|string|number|integer|boolean|date|timestamp|time
    physicalType: table             # Physical type (table, view, topic, etc.)
    physicalName: ord_transactions  # Physical database name
    businessName: Customer Orders   # Business-friendly name
    description: All customer orders
    dataGranularityDescription: One row per order
    tags: [sales, transactions]

    properties:                     # Columns/fields
      - name: order_id
        id: order_id_col
        logicalType: integer
        physicalType: bigint
        primaryKey: true
        primaryKeyPosition: 1
        required: true
        unique: true
        description: Unique order identifier
        classification: public     # public|restricted|confidential

      - name: customer_id
        logicalType: string
        physicalType: varchar(50)
        required: true
        classification: restricted

      - name: order_date
        logicalType: date
        physicalType: date
        partitioned: true
        partitionKeyPosition: 1

      - name: amount
        logicalType: number
        physicalType: decimal(10,2)
        criticalDataElement: true
```

### Logical Types and Options

| Logical Type | Physical Examples | logicalTypeOptions |
|--------------|-------------------|-------------------|
| string | varchar, text, char | minLength, maxLength, pattern, format |
| number | decimal, float, double | minimum, maximum, exclusiveMinimum, exclusiveMaximum, format |
| integer | int, bigint, smallint | minimum, maximum, format (i32, i64) |
| date | date | format, minimum, maximum |
| timestamp | timestamp, datetime | format, minimum, maximum, timezone, defaultTimezone |
| time | time | format, minimum, maximum |
| boolean | bool, boolean | - |
| object | json, struct | required, minProperties, maxProperties |
| array | list, array | minItems, maxItems, uniqueItems |

Example with options:
```yaml
- name: email
  logicalType: string
  logicalTypeOptions:
    pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
    maxLength: 255

- name: age
  logicalType: integer
  logicalTypeOptions:
    minimum: 0
    maximum: 150
```

## Relationships (Foreign Keys)

Define at property level (simple) or schema level (composite):

```yaml
# Property-level (simple FK)
properties:
  - name: customer_id
    logicalType: string
    relationships:
      - type: foreignKey
        to: customers.id

# Schema-level (composite FK)
schema:
  - name: order_items
    relationships:
      - type: foreignKey
        from:
          - order_items.order_id
          - order_items.line_number
        to:
          - orders.order_id
          - orders.line_id
```

## Data Quality Rules

Add quality checks at schema or property level:

```yaml
quality:
  # Library metric (predefined)
  - type: library
    metric: nullValues          # nullValues|missingValues|invalidValues|duplicateValues|rowCount
    mustBe: 0                   # mustBe|mustNotBe|mustBeGreaterThan|mustBeGreaterOrEqualTo|mustBeLessThan|mustBeLessOrEqualTo|mustBeBetween|mustNotBeBetween (one per rule)
    unit: percent               # rows|percent
    dimension: completeness     # accuracy|completeness|conformity|consistency|coverage|timeliness|uniqueness
    severity: error             # error|warning
    description: No null values allowed
    schedule: "0 20 * * *"      # Cron expression
    scheduler: cron

  # SQL-based check
  - type: sql
    query: "SELECT COUNT(*) FROM {object} WHERE {property} < 0"
    mustBe: 0
    dimension: validity
    severity: error

  # Custom (vendor-specific)
  - type: custom
    engine: great_expectations
    implementation: |
      expect_column_values_to_be_between:
        column: amount
        min_value: 0
```

See references/quality-rules.md for complete patterns.

## Servers Section

Configure data platform connections:

```yaml
servers:
  # PostgreSQL
  - server: prod-postgres
    type: postgres
    host: db.example.com
    port: 5432
    database: analytics
    schema: public
    environment: prod

  # Snowflake
  - server: snowflake-prod
    type: snowflake
    account: xy12345.us-east-1
    database: ANALYTICS
    schema: PUBLIC
    warehouse: COMPUTE_WH

  # BigQuery
  - server: bigquery-prod
    type: bigquery
    project: my-project-id
    dataset: analytics

  # Kafka
  - server: kafka-prod
    type: kafka
    host: kafka.example.com:9092
    format: avro

  # S3
  - server: s3-data-lake
    type: s3
    location: s3://my-bucket/data/
    format: parquet
```

See references/server-types.md for all supported platforms.

## SLA Properties

```yaml
slaProperties:
  - property: latency
    value: 4
    unit: d                     # d|day|days|y|yr|years

  - property: availability
    value: 99.9
    unit: percent

  - property: retention
    value: 7
    unit: y

  - property: frequency
    value: 1
    valueExt: 1
    unit: d

  - property: generalAvailability
    value: "2024-01-01T00:00:00Z"

  - property: endOfSupport
    value: "2030-01-01T00:00:00Z"
```

Properties: latency, availability, throughput, errorRate, retention, frequency, generalAvailability, endOfSupport, endOfLife, timeOfAvailability, timeToDetect, timeToNotify, timeToRepair

## Team Section

```yaml
team:
  name: data-platform-team
  description: Owns customer data products
  members:
    - username: jsmith@company.com
      name: John Smith
      role: Owner
      dateIn: "2024-01-01"
    - username: mjones@company.com
      role: Data Steward
      dateIn: "2024-01-01"
```

## Roles Section

```yaml
roles:
  - role: analytics_read
    access: read
    description: Read access for analytics team
    firstLevelApprovers: Data Steward
    secondLevelApprovers: Data Owner

  - role: etl_write
    access: write
    description: Write access for ETL processes
```

## Support Section

```yaml
support:
  - channel: "#data-help"
    tool: slack
    scope: interactive

  - channel: data-announcements
    tool: email
    url: mailto:data-ann@company.com
    scope: announcements

  - channel: Data Issues
    tool: ticket
    url: https://jira.company.com/data
    scope: issues
```

Tools: email, slack, teams, discord, ticket, googlechat, other

## Pricing Section

```yaml
price:
  priceAmount: 0.10
  priceCurrency: USD
  priceUnit: gigabyte
```

## Custom Properties

Add custom properties at any level:

```yaml
customProperties:
  - property: dataClassification
    value: internal
    description: Internal data classification
  - property: retentionPolicy
    value:
      hot: 30
      warm: 90
      cold: 365
```

## Scripts

### Generate New Contract

```bash
# Full template with all sections
python3 scripts/new_contract.py my-contract.odcs.yaml --name "My Data Product" --domain sales

# Minimal contract
python3 scripts/new_contract.py my-contract.odcs.yaml --minimal
```

### Validate Contract

```bash
# Auto-detects schema location
python3 scripts/validate_contract.py my-contract.odcs.yaml

# Specify schema explicitly
python3 scripts/validate_contract.py my-contract.odcs.yaml --schema https://raw.githubusercontent.com/bitol-io/open-data-contract-standard/main/schema/odcs-json-schema-v3.1.0.json
```

Requirements: `pip install pyyaml jsonschema`

## Validation

Validate contracts against JSON schema at: [`schema/odcs-json-schema-v3.1.0.json`](https://github.com/bitol-io/open-data-contract-standard/blob/main/schema/odcs-json-schema-v3.1.0.json)

```bash
# Using skill script (Python)
python3 scripts/validate_contract.py my-contract.odcs.yaml

# Using AJV (Node.js)
ajv validate -s https://raw.githubusercontent.com/bitol-io/open-data-contract-standard/main/schema/odcs-json-schema-v3.1.0.json -d my-contract.odcs.yaml
```

## References

- **Quality rules patterns**: See references/quality-rules.md
- **Server configurations**: See references/server-types.md
- **Relationships & foreign keys**: See references/relationships.md
- **Full examples**: See [docs/examples/](https://github.com/bitol-io/open-data-contract-standard/tree/main/docs/examples/) directory
