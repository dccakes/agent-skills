# Relationships & References Guide

## Table of Contents
1. [Reference Notation](#reference-notation)
2. [Property-Level Relationships](#property-level-relationships)
3. [Schema-Level Relationships](#schema-level-relationships)
4. [Composite Keys](#composite-keys)
5. [External Contract References](#external-contract-references)
6. [Common Patterns](#common-patterns)
7. [Validation Rules](#validation-rules)

## Reference Notation

ODCS v3.1.0 supports two notation styles for foreign key references:

### Fully Qualified Notation (Recommended)
Uses `id` fields with slash-separated paths. Stable across renames.

```yaml
# Format: schema/<schema_id>/properties/<property_id>
to: schema/customers_tbl/properties/cust_id_pk

# Nested properties
to: schema/accounts_tbl/properties/address_field/properties/street_field
```

### Shorthand Notation
Uses `name` fields with dot-separated paths. More readable, less stable.

```yaml
# Format: <schema_name>.<property_name>
to: customers.id

# Nested properties
to: accounts.address.street
```

**When to use each:**

| Use Case | Recommendation |
|----------|---------------|
| Production contracts | Fully qualified |
| Cross-contract references | Fully qualified |
| Expected refactoring | Fully qualified |
| Simple/development contracts | Shorthand |
| Quick prototyping | Shorthand |

## Property-Level Relationships

Define relationships directly on a property. The `from` field is **implicit** and must NOT be specified.

### Simple Foreign Key

```yaml
schema:
  - name: orders
    properties:
      - name: customer_id
        logicalType: string
        relationships:
          # Shorthand (concise)
          - to: customers.id
            type: foreignKey

          # Fully qualified (stable)
          - to: schema/customers_tbl/properties/cust_id_pk
            type: foreignKey
```

### Multiple Relationships from One Property

```yaml
schema:
  - name: orders
    properties:
      - name: customer_id
        logicalType: string
        relationships:
          - to: customers.id
          - to: loyalty_members.customer_id
          - to: customer_profiles.user_id
```

### With Custom Properties

```yaml
schema:
  - name: orders
    properties:
      - name: customer_id
        logicalType: string
        relationships:
          - to: customers.id
            type: foreignKey
            customProperties:
              - property: cardinality
                value: "many-to-one"
              - property: onDelete
                value: "cascade"
              - property: description
                value: "Links order to customer master data"
```

## Schema-Level Relationships

Define relationships at the schema (table) level. Both `from` and `to` are **required**.

### Basic Schema-Level Foreign Key

```yaml
schema:
  - name: orders
    relationships:
      # Shorthand notation
      - type: foreignKey
        from: orders.customer_id
        to: customers.id

      # Fully qualified notation
      - type: foreignKey
        from: schema/orders_tbl/properties/customer_id_col
        to: schema/customers_tbl/properties/id_col
```

### When to Use Schema-Level

Use schema-level relationships when:
- Defining composite keys (multiple columns)
- The relationship isn't naturally associated with one property
- Documenting table-level constraints

## Composite Keys

For multi-column foreign keys, use arrays. Both `from` and `to` must be arrays with **matching lengths**.

### Basic Composite Key

```yaml
schema:
  - name: order_items
    relationships:
      - type: foreignKey
        from:
          - order_items.order_id
          - order_items.line_number
        to:
          - order_details.order_id
          - order_details.line_id
```

### Composite Key with Fully Qualified Notation

```yaml
schema:
  - name: order_items
    id: order_items_tbl
    relationships:
      - type: foreignKey
        from:
          - schema/order_items_tbl/properties/order_id_col
          - schema/order_items_tbl/properties/line_num_col
        to:
          - schema/order_details_tbl/properties/order_id_col
          - schema/order_details_tbl/properties/line_id_col
        customProperties:
          - property: description
            value: "Composite key linking to order line details"
```

### Three-Column Composite Key

```yaml
schema:
  - name: inventory_transactions
    relationships:
      - type: foreignKey
        from:
          - inventory_transactions.warehouse_id
          - inventory_transactions.product_id
          - inventory_transactions.bin_location
        to:
          - warehouse_inventory.warehouse_id
          - warehouse_inventory.product_id
          - warehouse_inventory.bin_location
```

## External Contract References

Reference elements in other contract files.

### Same Directory

```yaml
relationships:
  - to: customer-contract.yaml#customers.id
  - to: customer-contract.yaml#/schema/customers_tbl/properties/id_col
```

### Relative Path

```yaml
relationships:
  - to: ../shared/customer-contract.yaml#customers.id
  - to: ../../contracts/v2/customer-contract.yaml#/schema/customers_tbl/properties/id_col
```

### Full URL

```yaml
relationships:
  - to: https://contracts.example.com/customer-contract.yaml#customers.id
  - to: https://contracts.example.com/customer-contract.yaml#/schema/customers_tbl/properties/id_col
```

### File Path

```yaml
relationships:
  - to: file:///path/to/customer-contract.yaml#customers.id
```

## Common Patterns

### One-to-Many (Parent-Child)

```yaml
# Orders -> Order Items (one order has many items)
schema:
  - name: order_items
    properties:
      - name: order_id
        logicalType: integer
        required: true
        relationships:
          - to: orders.id
            customProperties:
              - property: cardinality
                value: "many-to-one"
```

### Many-to-Many (Junction Table)

```yaml
# Students <-> Courses via Enrollments
schema:
  - name: enrollments
    properties:
      - name: student_id
        logicalType: integer
        primaryKey: true
        primaryKeyPosition: 1
        relationships:
          - to: students.id
      - name: course_id
        logicalType: integer
        primaryKey: true
        primaryKeyPosition: 2
        relationships:
          - to: courses.id
```

### Self-Referencing

```yaml
# Employees -> Manager (same table)
schema:
  - name: employees
    properties:
      - name: id
        logicalType: integer
        primaryKey: true
      - name: manager_id
        logicalType: integer
        relationships:
          - to: employees.id
            customProperties:
              - property: description
                value: "Reports to this manager"
```

### Polymorphic Reference

```yaml
# Document can reference either Customer or Vendor
schema:
  - name: documents
    properties:
      - name: entity_type
        logicalType: string
        description: "Either 'customer' or 'vendor'"
      - name: entity_id
        logicalType: integer
        relationships:
          - to: customers.id
            customProperties:
              - property: condition
                value: "entity_type = 'customer'"
          - to: vendors.id
            customProperties:
              - property: condition
                value: "entity_type = 'vendor'"
```

### Nested Object Reference

```yaml
schema:
  - name: users
    properties:
      - name: id
        logicalType: integer
        relationships:
          # Reference nested property
          - to: schema/accounts_tbl/properties/billing_address/properties/postal_code
          # Shorthand
          - to: accounts.billing_address.postal_code
```

## Validation Rules

### Property-Level Rules

| Rule | Description |
|------|-------------|
| No `from` field | `from` is implicit at property level |
| `to` required | Must specify target reference |
| `type` defaults to `foreignKey` | Can be omitted |

### Schema-Level Rules

| Rule | Description |
|------|-------------|
| `from` required | Must specify source reference |
| `to` required | Must specify target reference |
| Type consistency | Both `from` and `to` must be same type (string or array) |
| Array length match | For composite keys, arrays must have same length |

### Invalid Examples

```yaml
# INVALID: 'from' at property level
properties:
  - name: customer_id
    relationships:
      - from: orders.customer_id  # ERROR!
        to: customers.id

# INVALID: Missing 'from' at schema level
schema:
  - name: orders
    relationships:
      - to: customers.id  # ERROR! Missing 'from'

# INVALID: Type mismatch
relationships:
  - from: orders.id           # String
    to:                       # Array - ERROR!
      - items.order_id
      - items.line_num

# INVALID: Array length mismatch
relationships:
  - from:
      - orders.id
      - orders.customer_id    # 2 elements
    to:
      - items.order_id        # 1 element - ERROR!
```

## Complete Example

```yaml
apiVersion: v3.1.0
kind: DataContract
id: 550e8400-e29b-41d4-a716-446655440000
version: 1.0.0
status: active

schema:
  # Customers table
  - name: customers
    id: customers_tbl
    logicalType: object
    properties:
      - name: id
        id: cust_id_pk
        logicalType: integer
        primaryKey: true
      - name: country_code
        id: cust_country
        logicalType: string

  # Orders table with various relationship patterns
  - name: orders
    id: orders_tbl
    logicalType: object
    properties:
      - name: id
        id: order_id_pk
        logicalType: integer
        primaryKey: true

      - name: customer_id
        id: order_cust_id
        logicalType: integer
        required: true
        # Property-level simple FK
        relationships:
          - to: customers.id
            customProperties:
              - property: cardinality
                value: "many-to-one"

      - name: customer_country
        id: order_cust_country
        logicalType: string

    # Schema-level composite FK
    relationships:
      - type: foreignKey
        from:
          - orders.customer_id
          - orders.customer_country
        to:
          - customers.id
          - customers.country_code
        customProperties:
          - property: description
            value: "Composite key ensuring customer and country match"

  # Order items with external reference
  - name: order_items
    id: order_items_tbl
    logicalType: object
    properties:
      - name: order_id
        logicalType: integer
        relationships:
          - to: orders.id
      - name: product_id
        logicalType: integer
        relationships:
          # External contract reference
          - to: product-catalog.yaml#products.id
```
