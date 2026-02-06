# Data Quality Rules Reference

## Table of Contents
1. [Library Metrics](#library-metrics)
2. [SQL-Based Checks](#sql-based-checks)
3. [Custom Engine Checks](#custom-engine-checks)
4. [Common Patterns](#common-patterns)

## Library Metrics

Pre-defined metrics that work out of the box:

### nullValues
Check for null/missing values in a column.

```yaml
quality:
  - type: library
    metric: nullValues
    mustBe: 0
    unit: percent
    dimension: completeness
    severity: error
    description: Column must not contain null values
```

### missingValues
Check for missing/empty values (nulls, empty strings, whitespace).

```yaml
quality:
  - type: library
    metric: missingValues
    mustBeLessThan: 5
    unit: percent
    dimension: completeness
    severity: warning
```

### invalidValues
Check for values that don't match expected patterns.

```yaml
quality:
  - type: library
    metric: invalidValues
    mustBe: 0
    unit: rows
    dimension: validity
    severity: error
    arguments:
      validValues: ["active", "inactive", "pending"]
```

### duplicateValues
Check for duplicate values.

```yaml
quality:
  - type: library
    metric: duplicateValues
    mustBe: 0
    unit: rows
    dimension: uniqueness
    severity: error
```

### rowCount
Validate expected row counts.

```yaml
quality:
  - type: library
    metric: rowCount
    mustBeBetween: [1000000, 10000000]
    dimension: completeness
    severity: error
    description: Row count must be within expected range
```

> **Note:** Only one comparison operator is allowed per quality rule (the JSON schema enforces `oneOf`). To check both a lower and upper bound, use `mustBeBetween` with a two-element array.

### Numeric Range / Non-Negative Validation

The library metrics (`nullValues`, `missingValues`, `invalidValues`, `duplicateValues`, `rowCount`) do not include a numeric range metric. Use `type: sql` for numeric range and non-negative checks:

```yaml
quality:
  - type: sql
    query: "SELECT COUNT(*) FROM {object} WHERE {property} < 0"
    mustBe: 0
    dimension: validity
    severity: error
    description: Amount must be non-negative
```

## Comparison Operators

Only one comparison operator is allowed per quality rule.

| Operator | Usage |
|----------|-------|
| mustBe | Exact match (`=`) |
| mustNotBe | Not equal to (`!=`) |
| mustBeGreaterThan | Strictly greater than (`>`) |
| mustBeGreaterOrEqualTo | Greater than or equal to (`>=`) |
| mustBeLessThan | Strictly less than (`<`) |
| mustBeLessOrEqualTo | Less than or equal to (`<=`) |
| mustBeBetween | Within range, inclusive (two-element array) |
| mustNotBeBetween | Outside range (two-element array) |

```yaml
# mustBeBetween example
quality:
  - type: library
    metric: rowCount
    mustBeBetween: [1000000, 5000000]

# mustBeGreaterOrEqualTo example
quality:
  - type: library
    metric: rowCount
    mustBeGreaterOrEqualTo: 1000
```

## SQL-Based Checks

Use SQL for custom validation logic. Placeholders:
- `{object}` - table/object name
- `{property}` - column/property name

### Negative Values Check
```yaml
quality:
  - type: sql
    query: "SELECT COUNT(*) FROM {object} WHERE {property} < 0"
    mustBe: 0
    dimension: validity
    severity: error
    description: Amount cannot be negative
```

### Range Validation
```yaml
quality:
  - type: sql
    query: |
      SELECT COUNT(*) FROM {object}
      WHERE {property} NOT BETWEEN 0 AND 100
    mustBe: 0
    dimension: validity
    severity: error
```

### Referential Integrity
```yaml
quality:
  - type: sql
    query: |
      SELECT COUNT(*) FROM {object} o
      LEFT JOIN reference_table r ON o.{property} = r.id
      WHERE r.id IS NULL AND o.{property} IS NOT NULL
    mustBe: 0
    dimension: consistency
    severity: error
    description: All values must exist in reference table
```

### Freshness Check
```yaml
quality:
  - type: sql
    query: |
      SELECT CASE
        WHEN MAX({property}) >= CURRENT_DATE - INTERVAL '1 day'
        THEN 0 ELSE 1 END
      FROM {object}
    mustBe: 0
    dimension: timeliness
    severity: error
    description: Data must be updated within last 24 hours
```

### Cross-Column Validation
```yaml
quality:
  - type: sql
    query: |
      SELECT COUNT(*) FROM {object}
      WHERE end_date < start_date
    mustBe: 0
    dimension: consistency
    severity: error
    description: End date must be after start date
```

## Custom Engine Checks

Vendor-specific implementations for data quality tools.

### Great Expectations
```yaml
quality:
  - type: custom
    engine: great_expectations
    implementation: |
      expect_column_values_to_be_between:
        column: amount
        min_value: 0
        max_value: 1000000
        mostly: 0.99
```

### Soda
```yaml
quality:
  - type: custom
    engine: soda
    implementation: |
      checks for orders:
        - row_count > 0
        - missing_count(customer_id) = 0
        - invalid_percent(status) < 1%:
            valid values: ['pending', 'completed', 'cancelled']
```

### Monte Carlo
```yaml
quality:
  - type: custom
    engine: montecarlo
    implementation: |
      monitors:
        - type: freshness
          threshold_hours: 24
        - type: volume
          threshold_percent: 20
```

### dbt
```yaml
quality:
  - type: custom
    engine: dbt
    implementation: |
      tests:
        - unique
        - not_null
        - accepted_values:
            values: ['pending', 'completed', 'cancelled']
```

## Common Patterns

### Required Field Pattern
```yaml
- name: customer_id
  logicalType: string
  required: true
  quality:
    - type: library
      metric: nullValues
      mustBe: 0
      dimension: completeness
      severity: error
```

### Email Validation Pattern
```yaml
- name: email
  logicalType: string
  logicalTypeOptions:
    pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
  quality:
    - type: library
      metric: invalidValues
      mustBe: 0
      dimension: validity
      severity: error
```

### Primary Key Pattern
```yaml
- name: id
  logicalType: integer
  primaryKey: true
  unique: true
  required: true
  quality:
    - type: library
      metric: nullValues
      mustBe: 0
      dimension: completeness
      severity: error
    - type: library
      metric: duplicateValues
      mustBe: 0
      dimension: uniqueness
      severity: error
```

### Date Range Pattern
```yaml
- name: transaction_date
  logicalType: date
  quality:
    - type: sql
      query: |
        SELECT COUNT(*) FROM {object}
        WHERE {property} > CURRENT_DATE
          OR {property} < '2020-01-01'
      mustBe: 0
      dimension: validity
      severity: error
      description: Date must be between 2020-01-01 and today
```

## Quality Dimensions

| Dimension | Description | Common Metrics |
|-----------|-------------|----------------|
| completeness | Data is not missing | nullValues, missingValues, rowCount |
| accuracy | Data reflects reality | custom validation |
| consistency | Data agrees across sources | referential checks |
| validity | Data conforms to rules | invalidValues, pattern checks |
| uniqueness | No unwanted duplicates | duplicateValues |
| timeliness | Data is current | freshness checks |
| conformity | Data matches standards | format validation |

## Scheduling

```yaml
quality:
  - type: library
    metric: nullValues
    mustBe: 0
    scheduler: cron
    schedule: "0 20 * * *"    # Daily at 8 PM
```

Common cron patterns:
- `0 * * * *` - Every hour
- `0 0 * * *` - Daily at midnight
- `0 0 * * 0` - Weekly on Sunday
- `0 0 1 * *` - Monthly on the 1st
