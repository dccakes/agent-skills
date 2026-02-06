# Server Types Reference

## Table of Contents
1. [Relational Databases](#relational-databases)
2. [Cloud Data Warehouses](#cloud-data-warehouses)
3. [Streaming Platforms](#streaming-platforms)
4. [Object Storage](#object-storage)
5. [NoSQL Databases](#nosql-databases)
6. [Other Platforms](#other-platforms)

## Common Properties

All server types support these properties:

```yaml
servers:
  - server: my-server          # Required: server identifier
    type: <type>               # Required: server type
    id: srv-001                # Optional: unique ID
    description: Production DB # Optional: description
    environment: prod          # Optional: prod|staging|dev|uat
    roles:                     # Optional: access roles
      - role: read_role
        access: read
    customProperties:          # Optional: custom metadata
      - property: region
        value: us-east-1
```

## Relational Databases

### PostgreSQL
```yaml
servers:
  - server: postgres-prod
    type: postgres
    host: db.example.com
    port: 5432
    database: analytics
    schema: public
```

### MySQL
```yaml
servers:
  - server: mysql-prod
    type: mysql
    host: mysql.example.com
    port: 3306
    database: orders
```

### SQL Server
```yaml
servers:
  - server: sqlserver-prod
    type: sqlserver
    host: sqlserver.example.com
    port: 1433
    database: warehouse
    schema: dbo
```

### Oracle
```yaml
servers:
  - server: oracle-prod
    type: oracle
    host: oracle.example.com
    port: 1521
    database: ORCL
    schema: SALES
```

## Cloud Data Warehouses

### Snowflake
```yaml
servers:
  - server: snowflake-prod
    type: snowflake
    account: xy12345.us-east-1
    database: ANALYTICS
    schema: PUBLIC
    warehouse: COMPUTE_WH
    role: ANALYST_ROLE
```

### BigQuery
```yaml
servers:
  - server: bigquery-prod
    type: bigquery
    project: my-gcp-project
    dataset: analytics
```

### Databricks
```yaml
servers:
  - server: databricks-prod
    type: databricks
    host: dbc-abc123.cloud.databricks.com
    catalog: main
    schema: analytics
```

### Redshift
```yaml
servers:
  - server: redshift-prod
    type: redshift
    host: my-cluster.abc123.us-east-1.redshift.amazonaws.com
    port: 5439
    database: analytics
    schema: public
```

### Synapse
```yaml
servers:
  - server: synapse-prod
    type: synapse
    host: myworkspace.sql.azuresynapse.net
    database: analytics_pool
    schema: dbo
```

### Trino / Presto
```yaml
servers:
  - server: trino-prod
    type: trino
    host: trino.example.com
    port: 8080
    catalog: hive
    schema: analytics
```

## Streaming Platforms

### Kafka
```yaml
servers:
  - server: kafka-prod
    type: kafka
    host: kafka.example.com:9092
    format: avro
    schemaRegistryUrl: https://schema-registry.example.com
```

### Kafka (Confluent Cloud)
```yaml
servers:
  - server: confluent-cloud
    type: kafka
    host: pkc-abc123.us-east-1.aws.confluent.cloud:9092
    format: avro
    schemaRegistryUrl: https://psrc-abc123.us-east-1.aws.confluent.cloud
```

### Kinesis
```yaml
servers:
  - server: kinesis-prod
    type: kinesis
    streamName: orders-stream
    region: us-east-1
```

### Pub/Sub
```yaml
servers:
  - server: pubsub-prod
    type: pubsub
    project: my-gcp-project
    topic: orders-topic
```

## Object Storage

### S3
```yaml
servers:
  - server: s3-data-lake
    type: s3
    location: s3://my-bucket/data/orders/
    format: parquet
    delimiter: ","
    endpointUrl: https://s3.us-east-1.amazonaws.com
```

### Azure Blob / ADLS
```yaml
servers:
  - server: azure-data-lake
    type: azure
    location: abfss://container@account.dfs.core.windows.net/data/
    format: parquet
```

### GCS
```yaml
servers:
  - server: gcs-data-lake
    type: gcs
    location: gs://my-bucket/data/orders/
    format: parquet
```

### MinIO
```yaml
servers:
  - server: minio-local
    type: s3
    location: s3://my-bucket/data/
    endpointUrl: http://minio.local:9000
    format: parquet
```

## NoSQL Databases

### MongoDB
```yaml
servers:
  - server: mongodb-prod
    type: mongodb
    host: mongodb.example.com
    port: 27017
    database: orders
    collection: transactions
```

### Cassandra
```yaml
servers:
  - server: cassandra-prod
    type: cassandra
    host: cassandra.example.com
    port: 9042
    keyspace: analytics
```

### DynamoDB
```yaml
servers:
  - server: dynamodb-prod
    type: dynamodb
    region: us-east-1
    table: orders
```

### Elasticsearch
```yaml
servers:
  - server: elasticsearch-prod
    type: elasticsearch
    host: elasticsearch.example.com
    port: 9200
    index: orders
```

## Other Platforms

### Delta Lake
```yaml
servers:
  - server: delta-lake
    type: delta
    location: s3://my-bucket/delta/orders/
```

### Iceberg
```yaml
servers:
  - server: iceberg-catalog
    type: iceberg
    catalog: my_catalog
    warehouse: s3://my-bucket/iceberg/
```

### Hudi
```yaml
servers:
  - server: hudi-tables
    type: hudi
    location: s3://my-bucket/hudi/orders/
```

### dbt
```yaml
servers:
  - server: dbt-project
    type: dbt
    project: my_dbt_project
    target: prod
```

### API
```yaml
servers:
  - server: orders-api
    type: api
    url: https://api.example.com/v1/orders
    format: json
```

### Local File
```yaml
servers:
  - server: local-files
    type: local
    location: /data/exports/
    format: csv
    delimiter: ","
```

## File Formats

Common format values:
- `parquet` - Apache Parquet
- `avro` - Apache Avro
- `json` - JSON/NDJSON
- `csv` - Comma-separated values
- `orc` - Apache ORC
- `delta` - Delta Lake format
- `iceberg` - Apache Iceberg

## Environment Values

Standard environment identifiers:
- `prod` - Production
- `staging` - Staging/Pre-production
- `dev` - Development
- `uat` - User Acceptance Testing
- `qa` - Quality Assurance
