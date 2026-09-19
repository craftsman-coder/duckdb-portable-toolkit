# Data Engineering Connectors

Lightweight Python clients for Kafka, Flink SQL, and Trino.
No Docker, no local cluster, no PySpark.

## Prerequisites

The client packages are installed with the `standard` or `full`
profile. To install them manually:

```bash
runtime/python/python.exe -m pip install ^
    kafka-python confluent-kafka trino py-flink-sql-gateway
```

## Kafka

```python
from toolkit.connections import (
    kafka_topics, kafka_consumer, kafka_producer, kafka_consume_once,
)

# List topics
print(kafka_topics('kafka-broker:9092'))

# Consume (streaming)
consumer = kafka_consumer('kafka-broker:9092', topics=['events'])
for msg in consumer:
    print(msg.topic, msg.partition, msg.offset, msg.value)

# Consume N messages, then stop
rows = kafka_consume_once('kafka-broker:9092', 'events', max_messages=50)

# Produce
producer = kafka_producer('kafka-broker:9092')
producer.send('events', {'user': 'ali', 'action': 'login'})
producer.flush()
```

### Kafka via DuckDB (no Python client)

DuckDB has a community `kafka` extension that reads topics as tables.

```python
import duckdb
from toolkit.connections import read_kafka_topic_via_duckdb

con = duckdb.connect()
df = read_kafka_topic_via_duckdb(con, 'kafka-broker:9092', 'events')
print(df.head())
```

## Flink SQL Gateway

Flink SQL Gateway exposes SQL over a REST API. The
`py-flink-sql-gateway` package is a small DBAPI 2.0 driver.

### Start the gateway on the cluster

```bash
$FLINK_HOME/bin/sql-gateway.sh start \
    --port 8083 \
    -D sql-gateway.endpoint.rest.address=0.0.0.0
```

### Query from Python

```python
from toolkit.connections import flink_sql_query, flink_sql_connect

# One-off query
rows = flink_sql_query(
    'http://flink-sql-gateway:8083',
    '''
        SELECT user_id, COUNT(*) AS events
        FROM kafka_events
        GROUP BY user_id
    ''',
)
for r in rows:
    print(r)

# Or use the DBAPI connection directly
conn = flink_sql_connect('http://flink-sql-gateway:8083')
cur = conn.cursor()
cur.execute('SHOW TABLES')
for row in cur.fetchall():
    print(row)
conn.close()
```

### Flink REST API (no package)

For cluster monitoring, use the REST API directly.

```python
from toolkit.connections import flink_jobs, flink_job_status, flink_cluster_info

for job in flink_jobs('http://flink-jobmanager:8081'):
    print(job['name'], job['state'])
```

## Trino

```python
from toolkit.connections import trino_query, trino_catalogs

print(trino_catalogs('trino-coordinator'))

df = trino_query(
    host='trino-coordinator',
    sql='SELECT region, count(*) FROM hive.default.sales GROUP BY region',
    catalog='hive',
    schema='default',
)
print(df)
```

## Generic SQLAlchemy

```python
from toolkit.connections import sqlalchemy_engine
import pandas as pd

engine = sqlalchemy_engine('postgresql://user:pass@host:5432/db')
df = pd.read_sql('SELECT * FROM orders LIMIT 100', engine)
```

## Windows limitations

Some servers cannot run on Windows (Doris, ClickHouse, Polaris,
Debezium Connect, Trino server). The toolkit provides only
**clients**; point them at any reachable remote server.

## Why no PySpark?

PySpark is the full Spark distribution (~300 MB). If you need the
Spark DataFrame API, install it manually:

```bash
runtime/python/python.exe -m pip install pyspark
```

Java (JRE) 11 or 17 is required.
