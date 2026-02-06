# ODCS Contract Skill - Test Suite

These tests define success criteria for the `odcs-contract` skill. Each test verifies that an agent WITH the skill loaded produces correct ODCS v3.1.0 contracts and avoids common mistakes.

Tests are grouped by category:
- **A**: Contract Creation (new contracts from scratch)
- **B**: Schema Definition (tables, columns, types, nested structures)
- **C**: Data Quality Rules (library, SQL, custom)
- **D**: Server Configuration (platform-specific)
- **E**: SLA Properties
- **F**: Relationships & References (foreign keys, cross-contract)
- **G**: Validation & Error Detection (catching invalid contracts)
- **H**: Maintenance & Updates (modifying existing contracts)
- **I**: Edge Cases & Common Mistakes

---

## A: Contract Creation

### Test A1: Minimal Valid Contract

**Scenario:** User wants the simplest possible valid contract.

**Prompt:**
Create a minimal ODCS data contract for a users table with just an id column.

**Expected Behavior:**
- Include ALL required fundamentals: `apiVersion: v3.1.0`, `kind: DataContract`, `id` (valid UUID), `version` (semver), `status`
- Include a schema with at least one object and one property
- Use correct YAML structure (arrays for schema and properties)
- Do NOT include optional sections (servers, SLA, team, etc.) unless asked

**Pass Criteria:**
Contract validates against the [ODCS JSON schema](https://github.com/bitol-io/open-data-contract-standard/blob/main/schema/odcs-json-schema-v3.1.0.json). All 5 required fundamentals present. No extraneous sections.

---

### Test A2: Full Contract with All Sections

**Scenario:** User wants a comprehensive contract covering every ODCS section.

**Prompt:**
Create a complete ODCS data contract for an e-commerce orders system. Include every available section: schema, quality, servers, SLA, team, roles, support, pricing, and custom properties.

**Expected Behavior:**
- All fundamentals present with valid values
- Schema with meaningful tables and columns
- Quality rules at both schema and property level
- At least one server configuration
- SLA properties with correct `property`/`value`/`unit` structure
- Team using v3.1.0 structure (object with `name` and `members` array, NOT deprecated array)
- Roles with `role`, `access`, and approvers
- Support channels with valid `tool` values (slack, teams, email, ticket, etc.)
- Price with `priceAmount`, `priceCurrency`, `priceUnit`
- Custom properties at root level
- `description` object with `purpose`, `limitations`, `usage`

**Pass Criteria:**
Contract validates against JSON schema. Team section uses v3.1.0 object structure (not deprecated array). Support tools use spec-valid values.

---

### Test A3: Contract with Description Block

**Scenario:** User wants to document their data product thoroughly.

**Prompt:**
Create an ODCS contract for a customer analytics dataset. Include a full description with purpose, limitations, usage, and authoritative definitions including a privacy statement.

**Expected Behavior:**
- `description` as an object (NOT a string) with `purpose`, `limitations`, `usage` sub-fields
- `description.authoritativeDefinitions` array with entries containing `type` and `url`
- Root-level `authoritativeDefinitions` for canonical URL
- Valid `type` values: `businessDefinition`, `transformationImplementation`, `videoTutorial`, `tutorial`, `implementation`, `canonicalUrl` (root only), `privacy-statement`

**Pass Criteria:**
Description is an object with all three sub-fields. Authoritative definitions use valid type values from the spec. `privacy-statement` is hyphenated (not camelCase).

---

## B: Schema Definition

### Test B1: Logical Types with Options

**Scenario:** User needs columns with type constraints.

**Prompt:**
Create an ODCS schema for a user_profiles table with: email (validated with regex pattern), age (between 0 and 150), score (decimal with 2 decimal places), bio (max 500 characters), and registration_date (with timezone).

**Expected Behavior:**
- `email`: logicalType `string` with `logicalTypeOptions.pattern` for regex
- `age`: logicalType `integer` with `logicalTypeOptions.minimum: 0` and `logicalTypeOptions.maximum: 150`
- `score`: logicalType `number` with appropriate physicalType
- `bio`: logicalType `string` with `logicalTypeOptions.maxLength: 500`
- `registration_date`: logicalType `timestamp` with `logicalTypeOptions.timezone` or `logicalTypeOptions.defaultTimezone`
- All `logicalTypeOptions` nested under the correct field name

**Pass Criteria:**
Each column uses `logicalTypeOptions` (not inline type constraints). Options match the correct logicalType (e.g., `pattern` only on strings, `minimum`/`maximum` on numbers/integers).

---

### Test B2: Array and Nested Object Types

**Scenario:** User has a semi-structured dataset with arrays and nested objects.

**Prompt:**
Create an ODCS schema for a Kafka events topic with: event_id (string), payload (object with nested address containing street, city, zip), and tags (array of strings, max 10 items, unique).

**Expected Behavior:**
- `payload`: logicalType `object` with nested `properties` array containing `address` as another object
- `address`: logicalType `object` with its own `properties` for street, city, zip
- `tags`: logicalType `array` with `logicalTypeOptions` containing `maxItems: 10` and `uniqueItems: true`
- `tags` should use `items` to define the array element type
- Proper nesting depth for nested objects

**Pass Criteria:**
Nested objects use `properties` arrays (not inline). Array type uses `items` for element definition and `logicalTypeOptions` for constraints. Structure validates against JSON schema.

---

### Test B3: Transform Lineage Properties

**Scenario:** User wants to document data lineage for a derived column.

**Prompt:**
Create an ODCS schema for a sales_summary table. The total_revenue column is derived from joining orders and payments tables using SQL transformation logic. Document the lineage.

**Expected Behavior:**
- Column includes `transformSourceObjects` as an array of source table names
- Column includes `transformLogic` with the actual SQL/logic
- Column includes `transformDescription` with business-friendly explanation
- These are property-level fields (not custom properties)

**Pass Criteria:**
All three transform fields present on the derived column. `transformSourceObjects` is an array. `transformLogic` contains actual logic (not placeholder). `transformDescription` is in business terms.

---

### Test B4: Composite Primary and Partition Keys

**Scenario:** User has a table with multi-column primary key and partitioning.

**Prompt:**
Create an ODCS schema for an order_items table with a composite primary key on (order_id, line_number) and partitioned by (order_date, region).

**Expected Behavior:**
- `order_id`: `primaryKey: true`, `primaryKeyPosition: 1`
- `line_number`: `primaryKey: true`, `primaryKeyPosition: 2`
- `order_date`: `partitioned: true`, `partitionKeyPosition: 1`
- `region`: `partitioned: true`, `partitionKeyPosition: 2`
- Position values start at 1 (not 0)

**Pass Criteria:**
Both primary key columns have `primaryKey: true` with sequential `primaryKeyPosition` starting at 1. Both partition columns have `partitioned: true` with sequential `partitionKeyPosition` starting at 1.

---

### Test B5: Classification and Encryption

**Scenario:** User needs to mark sensitive columns with classification and encryption.

**Prompt:**
Create an ODCS schema for a customers table with: id (public), email (restricted), ssn (confidential with encrypted version), and name (restricted, critical data element).

**Expected Behavior:**
- `classification` values from: `public`, `restricted`, `confidential`
- `ssn` includes `encryptedName` field pointing to encrypted column name
- `name` includes `criticalDataElement: true`
- Classification is a property-level field

**Pass Criteria:**
Valid classification values used. `encryptedName` is a string (not boolean). `criticalDataElement` is a boolean. No classification values outside the spec.

---

### Test B6: Schema Element Metadata

**Scenario:** User wants a well-documented table with all metadata.

**Prompt:**
Create an ODCS schema for a transactions table with physical name mapping, business name, data granularity, authoritative definitions, and tags.

**Expected Behavior:**
- Object level: `name`, `id`, `physicalName`, `physicalType`, `businessName`, `description`, `dataGranularityDescription`, `tags`, `authoritativeDefinitions`
- `logicalType: object` for the table-level element
- `physicalType` reflects actual database type (e.g., `table`, `view`)
- `authoritativeDefinitions` as array with `type` and `url`
- `id` field for stable referencing

**Pass Criteria:**
Object has both logical and physical naming. `dataGranularityDescription` is present. `authoritativeDefinitions` uses valid types. `id` is present for referenceability.

---

## C: Data Quality Rules

### Test C1: Library Metrics at Property Level

**Scenario:** User wants standard quality checks on specific columns.

**Prompt:**
Add quality rules to an orders schema: order_id must have no nulls and no duplicates, amount must be non-negative, and status must be one of [pending, completed, cancelled].

**Expected Behavior:**
- `nullValues` metric with `mustBe: 0`, dimension `completeness`
- `duplicateValues` metric with `mustBe: 0`, dimension `uniqueness`
- `invalidValues` metric with `arguments.validValues` array for status
- Quality rules placed at property level (inside the property definition)
- Each rule has `type: library`, appropriate `severity`, and `dimension`

**Pass Criteria:**
Each quality rule uses correct metric name, comparison operator, and dimension. `invalidValues` uses `arguments` for valid values list. Rules are at property level, not schema level.

---

### Test C2: All Comparison Operators

**Scenario:** User needs various threshold-based quality checks.

**Prompt:**
Create quality rules demonstrating all ODCS comparison operators: exact match, not equal, greater than, greater or equal, less than, less or equal, between, and not between.

**Expected Behavior:**
- Uses all 8 operators: `mustBe`, `mustNotBe`, `mustBeGreaterThan`, `mustBeGreaterOrEqualTo`, `mustBeLessThan`, `mustBeLessOrEqualTo`, `mustBeBetween`, `mustNotBeBetween`
- `mustBeBetween` and `mustNotBeBetween` use arrays with exactly 2 values
- Only one comparison operator per rule

**Pass Criteria:**
All 8 operators demonstrated correctly. Between operators use 2-element arrays. No rules with multiple comparison operators.

---

### Test C3: SQL-Based Quality Rules

**Scenario:** User needs custom SQL quality checks.

**Prompt:**
Add SQL quality rules for: referential integrity check, date range validation, and cross-column consistency (end_date must be after start_date).

**Expected Behavior:**
- `type: sql` with `query` field containing SQL
- Uses `{object}` and `{property}` placeholders correctly
- Each rule has `mustBe` (or other operator) for the expected result
- Appropriate `dimension` values (consistency, validity, timeliness)
- `severity` specified

**Pass Criteria:**
SQL queries use `{object}` and `{property}` placeholders (not hardcoded table/column names). Rules have both a comparison operator and dimension.

---

### Test C4: Custom Engine Quality Rules

**Scenario:** User uses Great Expectations and wants to define quality rules with it.

**Prompt:**
Add custom quality rules for Great Expectations: column values between 0-1000, column values not null, and column values matching a regex pattern.

**Expected Behavior:**
- `type: custom` with `engine: great_expectations`
- `implementation` field with valid Great Expectations expectation YAML
- Proper indentation of the implementation block
- Still includes `dimension` and `severity`

**Pass Criteria:**
Uses `type: custom`, not `type: library`. `engine` field matches the actual tool name. `implementation` contains valid tool-specific syntax.

---

### Test C5: Quality with Scheduling and Business Impact

**Scenario:** User wants quality checks that run on a schedule with documented business impact.

**Prompt:**
Create a quality rule for row count that runs daily at 8 PM, has error severity, and documents the business impact of failure.

**Expected Behavior:**
- `scheduler: cron` with `schedule: "0 20 * * *"`
- `businessImpact` field with meaningful description
- `method` field if applicable (e.g., `reconciliation`)
- All standard quality fields (type, metric, operator, dimension, severity)

**Pass Criteria:**
Schedule uses valid cron expression. `businessImpact` is present (not just `severity`). `scheduler` field accompanies `schedule`.

---

### Test C6: Text-Type Quality Description

**Scenario:** User wants to document a data quality expectation as prose rather than an automated check.

**Prompt:**
Add a quality entry that describes a manual review process for data accuracy - it's not automated, just documented.

**Expected Behavior:**
- `type: text` (not library, sql, or custom)
- `description` field with the prose explanation
- No `metric`, `query`, or `implementation` fields
- May still include `dimension` and `severity`

**Pass Criteria:**
Uses `type: text`. Does NOT include automated check fields (metric, query). Description contains the manual process documentation.

---

## D: Server Configuration

### Test D1: Common Database Servers

**Scenario:** User wants PostgreSQL and Snowflake server configurations.

**Prompt:**
Add server configurations for a PostgreSQL production database and a Snowflake analytics warehouse.

**Expected Behavior:**
- PostgreSQL: `type: postgres`, `host`, `port: 5432`, `database`, `schema`
- Snowflake: `type: snowflake`, `account`, `database`, `schema`, `warehouse`
- Both have `server` name and `environment`
- No credentials/passwords in the contract

**Pass Criteria:**
Correct type values. PostgreSQL uses default port 5432. Snowflake includes `account` and `warehouse`. No secrets exposed.

---

### Test D2: Cloud Storage and Streaming

**Scenario:** User needs S3 data lake and Kafka streaming server configs.

**Prompt:**
Configure servers for: an S3 data lake with Parquet files and a Kafka cluster with Avro format and schema registry.

**Expected Behavior:**
- S3: `type: s3`, `location` with s3:// URI, `format: parquet`
- Kafka: `type: kafka`, `host` with port, `format: avro`, `schemaRegistryUrl`
- Optional: `endpointUrl` for S3-compatible storage
- Optional: `delimiter` for CSV format

**Pass Criteria:**
S3 uses `location` (not `host`). Kafka includes both `host` and `format`. Schema registry URL included for Avro format.

---

### Test D3: Uncommon Server Types

**Scenario:** User asks for a less common platform.

**Prompt:**
Configure servers for Databricks Unity Catalog and AWS Glue.

**Expected Behavior:**
- Databricks: `type: databricks`, `host`, `catalog`, `schema`
- Glue: `type: glue`, `account`, `database`, `location`, `format`
- If the skill doesn't cover these types, agent should reference the spec or server-types.md rather than guessing field names

**Pass Criteria:**
Correct type values and platform-specific fields. Agent does NOT invent field names that don't exist in the spec. If unsure, agent checks the reference docs.

---

### Test D4: Server with Roles

**Scenario:** User wants server-level access roles.

**Prompt:**
Configure a BigQuery server with read and write roles defined at the server level.

**Expected Behavior:**
- Server includes `roles` array with role definitions
- Each role has `role` name and `access` (read/write)
- Roles at server level are separate from top-level `roles` section

**Pass Criteria:**
Roles are nested inside the server definition. Both `role` and `access` fields present.

---

## E: SLA Properties

### Test E1: Core SLA Properties

**Scenario:** User wants to define basic SLAs for their data product.

**Prompt:**
Add SLA properties for: data must be available within 4 hours (latency), 99.9% availability, and 7-year retention.

**Expected Behavior:**
- `slaProperties` as an array of objects
- Each with `property`, `value`, and `unit`
- Latency: `property: latency`, `value: 4`, `unit: d` (or hours)
- Availability: `property: availability`, `value: 99.9`, `unit: percent`
- Retention: `property: retention`, `value: 7`, `unit: y`
- Valid property names from the spec

**Pass Criteria:**
All SLA entries have `property` + `value`. Units use valid abbreviations (d, y, percent). Property names match the spec's Data QoS list.

---

### Test E2: Scheduling and Time-Based SLAs

**Scenario:** User needs SLAs for incident response and data freshness timing.

**Prompt:**
Add SLA properties for: data available at 9 AM EST daily, time to detect issues within 30 minutes, time to notify within 1 hour, and time to repair within 4 hours. The availability SLA is driven by regulatory requirements.

**Expected Behavior:**
- `timeOfAvailability` with time value and timezone
- `timeToDetect` with value and unit
- `timeToNotify` with value and unit
- `timeToRepair` with value and unit
- `driver: regulatory` on the availability property
- All are valid SLA property names

**Pass Criteria:**
All four time-based properties use correct names from spec (camelCase). `driver` field present with valid value (regulatory, analytics, operational). Agent does NOT invent SLA property names.

---

### Test E3: SLA with Element Targeting

**Scenario:** User wants different SLAs for different schema elements.

**Prompt:**
Add SLA properties where latency applies specifically to the orders.order_date column, not the whole contract.

**Expected Behavior:**
- SLA entry includes `element` field pointing to the specific schema element
- Element uses dot notation (e.g., `orders.order_date`)
- Other SLA entries without `element` apply to the whole contract

**Pass Criteria:**
`element` field present and uses correct notation. Agent explains that SLAs without `element` apply globally.

---

### Test E4: Frequency with Extended Value

**Scenario:** User wants a frequency SLA.

**Prompt:**
Add a frequency SLA: data is updated every 1 to 2 days.

**Expected Behavior:**
- `property: frequency` with `value: 1`, `valueExt: 2`, `unit: d`
- `valueExt` is used for the upper bound of a range
- Both `value` and `valueExt` are present

**Pass Criteria:**
`valueExt` is used correctly as the range upper bound. `value` is the lower bound. Both are numbers, not strings.

---

## F: Relationships & References

### Test F1: Property-Level Simple Foreign Key

**Scenario:** User wants a simple foreign key on a column.

**Prompt:**
Create a schema where orders.customer_id references customers.id as a foreign key.

**Expected Behavior:**
- Relationship defined at property level (inside `customer_id` property)
- Uses `relationships` array with `to: customers.id` (shorthand) or fully qualified
- `type: foreignKey` (can be omitted as it's the default)
- Does NOT include `from` field (implicit at property level)

**Pass Criteria:**
Relationship is at property level. No `from` field present. `to` uses valid notation.

---

### Test F2: Schema-Level Composite Foreign Key

**Scenario:** User has a multi-column foreign key.

**Prompt:**
Create a schema where order_items has a composite foreign key: (order_id, line_number) references (orders.order_id, orders.line_id).

**Expected Behavior:**
- Relationship defined at schema level (on the `order_items` object, not a property)
- Both `from` and `to` are arrays with matching lengths
- `from` includes full dot-notation paths
- `type: foreignKey` specified

**Pass Criteria:**
Relationship is at schema level. Both `from` and `to` are arrays with equal length. `from` is present (required at schema level).

---

### Test F3: External Contract Reference

**Scenario:** User wants a foreign key that references a column in another contract file.

**Prompt:**
Create a relationship where orders.product_id references the products.id column defined in product-catalog.odcs.yaml.

**Expected Behavior:**
- Uses external reference syntax: `product-catalog.odcs.yaml#products.id` or with fully qualified path
- File reference uses `#` separator between file path and element path
- Supports relative paths, absolute paths, or URLs

**Pass Criteria:**
External reference uses `#` separator. File path and element path are both present. Agent explains this is cross-contract referencing.

---

### Test F4: Fully Qualified vs Shorthand Notation

**Scenario:** User asks about the difference between reference notations.

**Prompt:**
Show me both notation styles for a foreign key from orders.customer_id to customers.id, using both fully qualified and shorthand syntax. When should I use each?

**Expected Behavior:**
- Shorthand: `to: customers.id` (name-based, dot-separated)
- Fully qualified: `to: schema/customers_tbl/properties/cust_id_pk` (id-based, slash-separated)
- Explain: fully qualified is stable across renames, shorthand is more readable
- Recommend fully qualified for production, shorthand for prototyping

**Pass Criteria:**
Both notations shown correctly. Fully qualified uses `id` fields (not names). Agent explains trade-offs and when to use each.

---

### Test F5: Invalid Relationship Detection

**Scenario:** User writes an invalid relationship.

**Prompt:**
Is this relationship correct?
```yaml
properties:
  - name: customer_id
    relationships:
      - from: orders.customer_id
        to: customers.id
```

**Expected Behavior:**
- Identify that `from` is NOT allowed at property level
- Explain that `from` is implicit at property level (it's the property itself)
- Show the corrected version (remove `from`)
- Explain that `from` is only required at schema level

**Pass Criteria:**
Agent catches the `from` field error. Agent explains why it's wrong. Corrected version removes `from`.

---

## G: Validation & Error Detection

### Test G1: Missing Required Fields

**Scenario:** User provides a contract missing required fundamentals.

**Prompt:**
Is this contract valid?
```yaml
apiVersion: v3.1.0
kind: DataContract
schema:
  - name: users
    logicalType: object
```

**Expected Behavior:**
- Identify missing `id`, `version`, and `status` fields
- All three are required by the spec
- Provide corrected version with all 5 required fields

**Pass Criteria:**
Agent identifies ALL missing required fields (not just one). Agent does not say the contract is valid.

---

### Test G2: Invalid Status Value

**Scenario:** User uses a non-standard status.

**Prompt:**
Is `status: published` a valid ODCS status?

**Expected Behavior:**
- Explain that `published` is NOT a valid status value
- List valid values: `proposed`, `draft`, `active`, `deprecated`, `retired`
- Suggest the closest valid alternative (likely `active`)

**Pass Criteria:**
Agent rejects `published` as invalid. Lists all 5 valid status values.

---

### Test G3: Schema Validation Script

**Scenario:** User wants to validate their contract file.

**Prompt:**
How do I validate my contract against the ODCS JSON schema?

**Expected Behavior:**
- Reference the validation script at `scripts/validate_contract.py`
- Mention the JSON schema at [`schema/odcs-json-schema-v3.1.0.json`](https://github.com/bitol-io/open-data-contract-standard/blob/main/schema/odcs-json-schema-v3.1.0.json)
- Provide the command: `python3 scripts/validate_contract.py my-contract.odcs.yaml`
- Mention prerequisites: `pip install pyyaml jsonschema`
- Optionally mention alternative tools (ajv for Node.js)

**Pass Criteria:**
Agent points to the correct script path and schema path. Command is runnable. Prerequisites mentioned.

---

### Test G4: Type Mismatch in Relationships

**Scenario:** User has a relationship with mismatched from/to types.

**Prompt:**
Is this schema-level relationship valid?
```yaml
relationships:
  - type: foreignKey
    from: orders.customer_id
    to:
      - customers.id
      - customers.country
```

**Expected Behavior:**
- Identify type mismatch: `from` is a string, `to` is an array
- Both must be the same type (both strings OR both arrays)
- Show corrected version (either both strings or both arrays)

**Pass Criteria:**
Agent catches the type mismatch. Explains both must be consistent. Shows correction.

---

## H: Maintenance & Updates

### Test H1: Adding Quality Rules to Existing Contract

**Scenario:** User has an existing contract and wants to add quality rules.

**Prompt:**
Here's my contract (provide a valid contract). Add null checks to all required columns and a row count check at the table level.

**Expected Behavior:**
- Add property-level quality rules to each column marked `required: true`
- Add schema-level quality rule for `rowCount`
- Preserve all existing contract content unchanged
- Quality rules at correct nesting level (property vs schema)

**Pass Criteria:**
Existing content preserved. New rules at correct levels. Required columns get null checks. Table gets row count check.

---

### Test H2: Upgrading Team Structure to v3.1.0

**Scenario:** User has a contract with deprecated team array structure.

**Prompt:**
My contract uses this team structure:
```yaml
team:
  - username: owner@company.com
    role: Owner
    dateIn: "2024-01-01"
```
Update it to the v3.1.0 format.

**Expected Behavior:**
- Convert from array to object with `members` sub-array
- Add `name` field to team object
- Preserve all member data
- Mention this is the v3.1.0 recommended structure
- Note the array format is deprecated

**Pass Criteria:**
Team becomes an object with `name` and `members`. All member data preserved. Agent mentions deprecation.

---

### Test H3: Adding a New Schema Element

**Scenario:** User wants to add a new table to an existing contract.

**Prompt:**
Add a new customer_addresses table to my contract with columns: address_id, customer_id (FK to customers.id), street, city, state, zip, and country.

**Expected Behavior:**
- New schema element appended to existing `schema` array
- Includes `id` field for referenceability
- `customer_id` has a property-level relationship to `customers.id`
- All columns have `logicalType`
- Table-level `logicalType: object`

**Pass Criteria:**
New table added without modifying existing tables. Foreign key relationship correctly defined. All columns have types.

---

## I: Edge Cases & Common Mistakes

### Test I1: Credentials in Server Config

**Scenario:** User asks to include database credentials.

**Prompt:**
Configure a PostgreSQL server with host, port, database, username admin, and password secret123.

**Expected Behavior:**
- Do NOT include password/credentials in the contract
- Warn that ODCS contracts should not contain secrets
- Include only connection metadata (host, port, database, schema)
- Suggest using environment variables or secrets management

**Pass Criteria:**
No password or credentials in the output. Agent warns about security. Connection metadata is correct.

---

### Test I2: Wrong Support Tool Values

**Scenario:** User wants Jira as a support channel.

**Prompt:**
Add Jira as a support channel for issue tracking.

**Expected Behavior:**
- Use `tool: ticket` (NOT `tool: jira`)
- Valid tool values: email, slack, teams, discord, ticket, googlechat, other
- Include `url` pointing to the Jira instance
- Use `scope: issues`
- `jira` is NOT a valid tool value in the spec

**Pass Criteria:**
Uses `tool: ticket` (not `jira`). Includes URL to the Jira board. Scope is `issues`.

---

### Test I3: Quality Rule vs logicalTypeOptions

**Scenario:** User wants to constrain an integer column to 0-100.

**Prompt:**
I need to ensure my percentage column only has values between 0 and 100. What's the best way to do this?

**Expected Behavior:**
- Explain TWO approaches: `logicalTypeOptions` (schema constraint) vs `quality` rule (runtime check)
- `logicalTypeOptions.minimum: 0` and `logicalTypeOptions.maximum: 100` for schema-level constraint
- Quality rule with `type: library` or `type: sql` for runtime validation
- Recommend both for defense in depth
- Explain the difference: schema defines the contract, quality enforces it

**Pass Criteria:**
Agent mentions both approaches. Explains when to use each. Shows correct syntax for both.

---

### Test I4: Deprecated Fields Awareness

**Scenario:** User uses deprecated ODCS fields.

**Prompt:**
My contract has `slaDefaultElement: orders.order_date` and uses `rule` instead of `metric` in quality checks. Is this correct for v3.1.0?

**Expected Behavior:**
- Identify `slaDefaultElement` as deprecated in v3.1.0 (removed in v4.0.0)
- Identify `rule` as deprecated, should use `metric` instead
- Suggest migration: use `element` field on individual SLA properties
- Suggest migration: rename `rule` to `metric`

**Pass Criteria:**
Both deprecated fields identified. Migration paths provided. Agent warns about v4.0.0 removal.

---

### Test I5: String Format Options

**Scenario:** User needs a string column with email format validation.

**Prompt:**
Create a schema property for an email column that should be validated as an email format.

**Expected Behavior:**
- `logicalType: string`
- `logicalTypeOptions.format: email`
- Valid string formats: `password`, `byte`, `binary`, `email`, `uuid`, `uri`, `hostname`, `ipv4`, `ipv6`
- Optionally also add `logicalTypeOptions.pattern` for a custom regex
- Optionally add a quality rule for runtime enforcement

**Pass Criteria:**
Uses `logicalTypeOptions.format` (not a custom property or quality-only approach). Format value is from the spec's valid list.

---

### Test I6: Contract File Naming

**Scenario:** User creates a new contract file.

**Prompt:**
What should I name my ODCS contract file?

**Expected Behavior:**
- Recommend `.odcs.yaml` extension
- Use descriptive name: `my-data-product.odcs.yaml`
- Mention the convention used in the examples directory

**Pass Criteria:**
Agent recommends `.odcs.yaml` extension. Provides naming example.

---

### Test I7: Custom Properties Value Types

**Scenario:** User wants custom properties with complex values.

**Prompt:**
Add custom properties: one with a simple string value, one with an array value, and one with an object value.

**Expected Behavior:**
- Custom properties support string, array, and object values
- Each entry has `property` (camelCase) and `value`
- Optional `description` field
- Array values: `value: [item1, item2]`
- Object values: `value: { key1: val1, key2: val2 }`

**Pass Criteria:**
All three value types demonstrated. Property names in camelCase. Structure matches spec.

---

### Test I8: Mixing Property-Level and Schema-Level Quality

**Scenario:** User needs quality rules at different levels.

**Prompt:**
Add quality rules: rowCount at the table level, and nullValues/duplicateValues at the column level for order_id.

**Expected Behavior:**
- `rowCount` placed in the schema-level `quality` array (on the object, not a property)
- `nullValues` and `duplicateValues` placed in the property-level `quality` array (on order_id)
- Both levels use the same quality rule structure
- `rowCount` is a schema-level metric, `nullValues` is a property-level metric

**Pass Criteria:**
Rules at correct levels. Schema-level rowCount not accidentally placed on a property. Property-level rules not accidentally placed on schema.

---

## Test Execution Notes

### How to Run Tests

Each test should be run as a separate conversation with a fresh agent:

1. **Baseline (RED):** Run prompt WITHOUT the odcs-contract skill loaded. Document agent behavior.
2. **With Skill (GREEN):** Run same prompt WITH the odcs-contract skill loaded. Verify expected behavior.
3. **Record Results:** Update Baseline Result and Verified Result with dates.

### Severity Levels

- **Critical:** Tests A1, A2, B1, C1, F1, F5, G1, I1, I2 - Core functionality that MUST work
- **Important:** Tests B2-B6, C2-C5, D1-D2, E1-E2, F2-F4, G2-G4, H1-H3, I3-I5 - Comprehensive coverage
- **Nice-to-have:** Tests D3-D4, E3-E4, C6, I6-I8 - Edge cases and advanced features
