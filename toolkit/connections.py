"""
Lightweight connectors for Kafka, Flink SQL, and Trino.

All functions use small, pure-Python packages; no full Spark or
Flink installation is required. Point them at any reachable remote
server on your network.
"""

from __future__ import annotations

import json
from typing import Any


# ------------------------------------------------------------------
# Kafka (kafka-python, pure Python)
# ------------------------------------------------------------------
def kafka_consumer(bootstrap_servers: str | list[str],
                   group_id: str = "duckdb-toolkit",
                   topics: list[str] | None = None,
                   auto_offset_reset: str = "latest",
                   timeout_ms: int = 10000):
    """Create a KafkaConsumer (kafka-python)."""
    from kafka import KafkaConsumer

    consumer = KafkaConsumer(
        bootstrap_servers=bootstrap_servers,
        group_id=group_id,
        auto_offset_reset=auto_offset_reset,
        enable_auto_commit=True,
        consumer_timeout_ms=timeout_ms,
        value_deserializer=_safe_json,
        key_deserializer=lambda x: x.decode("utf-8") if x else None,
    )
    if topics:
        consumer.subscribe(topics)
    return consumer


def kafka_producer(bootstrap_servers: str | list[str]):
    """Create a KafkaProducer (kafka-python)."""
    from kafka import KafkaProducer

    return KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )


def kafka_topics(bootstrap_servers: str | list[str],
                 timeout_ms: int = 5000) -> list[str]:
    """List all topics in a Kafka cluster."""
    from kafka import KafkaConsumer

    consumer = KafkaConsumer(
        bootstrap_servers=bootstrap_servers,
        consumer_timeout_ms=timeout_ms,
    )
    topics = sorted(consumer.topics())
    consumer.close()
    return topics


def kafka_consume_once(bootstrap_servers: str | list[str],
                       topic: str,
                       group_id: str = "duckdb-toolkit",
                       max_messages: int = 100,
                       timeout_ms: int = 5000) -> list[dict]:
    """
    Consume up to `max_messages` from a topic, then stop.

    Returns a list of dicts with keys: topic, partition, offset, key, value.
    """
    consumer = kafka_consumer(
        bootstrap_servers,
        group_id=group_id,
        topics=[topic],
        timeout_ms=timeout_ms,
    )
    messages = []
    for msg in consumer:
        messages.append({
            "topic": msg.topic,
            "partition": msg.partition,
            "offset": msg.offset,
            "key": msg.key,
            "value": msg.value,
        })
        if len(messages) >= max_messages:
            break
    consumer.close()
    return messages


def read_kafka_topic_via_duckdb(con,
                                 bootstrap_servers: str,
                                 topic: str,
                                 group_id: str = "duckdb-toolkit",
                                 limit: int = 1000):
    """
    Read a Kafka topic using DuckDB's community `kafka` extension.

    This does not require the Python kafka client. It loads the
    `kafka` extension and queries the topic as a regular table.
    """
    con.execute("INSTALL kafka FROM community;")
    con.execute("LOAD kafka;")
    sql = (
        "SELECT * FROM kafka_scan("
        f"brokers='{bootstrap_servers}', "
        f"topic='{topic}', "
        f"group_id='{group_id}'"
        ") "
        f"LIMIT {limit}"
    )
    return con.execute(sql).fetchdf()


def _safe_json(b: bytes):
    try:
        return json.loads(b.decode("utf-8"))
    except Exception:
        return b.decode("utf-8", errors="replace")


# ------------------------------------------------------------------
# Flink SQL Gateway (py-flink-sql-gateway)
# ------------------------------------------------------------------
def flink_sql_connect(gateway_url: str,
                      session_name: str | None = None):
    """
    Connect to a remote Flink SQL Gateway.

    Parameters
    ----------
    gateway_url : str
        Base URL of the Flink SQL Gateway, e.g.
        "http://flink-sql-gateway:8083".
    session_name : str, optional
        Reuse an existing session by name.
    """
    from flink_sql_gateway import connect

    return connect(uri=gateway_url, session_name=session_name)


def flink_sql_query(gateway_url: str, sql: str) -> list[dict]:
    """
    Run SQL on a Flink SQL Gateway and return rows as a list of dicts.

    If `py-flink-sql-gateway` is not installed, falls back to a direct
    HTTP call to the Flink SQL Gateway REST API (no extra package).
    """
    try:
        from flink_sql_gateway import connect as _connect
    except ImportError:
        # REST API fallback
        return _flink_sql_query_rest(gateway_url, sql)

    conn = _connect(uri=gateway_url)
    try:
        cur = conn.cursor()
        cur.execute(sql)
        cols = [d[0] for d in cur.description] if cur.description else []
        rows = cur.fetchall()
        return [dict(zip(cols, row)) for row in rows]
    finally:
        conn.close()


def _flink_sql_query_rest(gateway_url: str, sql: str) -> list[dict]:
    """
    Direct REST call to a Flink SQL Gateway (no Python client needed).

    Flow:
      1. POST   /v1/sessions           -> session_handle
      2. POST   /v1/sessions/{id}/statements -> operation_handle
      3. GET    /v1/sessions/{id}/operations/{op}/result/0
      4. DELETE /v1/sessions/{id}
    """
    import time
    import requests

    base = gateway_url.rstrip("/")

    # 1. Open a session
    r = requests.post(f"{base}/v1/sessions", json={"properties": {}}, timeout=10)
    r.raise_for_status()
    session = r.json()["sessionHandle"]

    try:
        # 2. Submit the statement
        r = requests.post(
            f"{base}/v1/sessions/{session}/statements",
            json={"statement": sql},
            timeout=30,
        )
        r.raise_for_status()
        operation = r.json()["operationHandle"]

        # 3. Poll for the result
        for _ in range(120):
            r = requests.get(
                f"{base}/v1/sessions/{session}/operations/{operation}/result/0",
                timeout=30,
            )
            if r.status_code == 200:
                data = r.json()
                rows = data.get("results", {}).get("data", [])
                cols = data.get("results", {}).get("columns")
                if cols:
                    names = [c.get("name") for c in cols]
                    return [dict(zip(names, row)) for row in rows]
                return rows
            if r.status_code == 404:
                # Result not ready yet
                time.sleep(1)
                continue
            r.raise_for_status()
        raise TimeoutError("Flink SQL Gateway did not return a result in time")
    finally:
        # 4. Close the session
        try:
            requests.delete(f"{base}/v1/sessions/{session}", timeout=5)
        except Exception:
            pass


def flink_jobs(jobmanager_url: str = "http://flink-jobmanager:8081") -> list:
    """List all jobs on a remote Flink cluster (REST API)."""
    import requests
    r = requests.get(f"{jobmanager_url}/jobs/overview", timeout=10)
    r.raise_for_status()
    return r.json().get("jobs", [])


def flink_job_status(job_id: str,
                     jobmanager_url: str = "http://flink-jobmanager:8081") -> dict:
    """Get the status of a specific Flink job."""
    import requests
    r = requests.get(f"{jobmanager_url}/jobs/{job_id}", timeout=10)
    r.raise_for_status()
    return r.json()


def flink_cluster_info(jobmanager_url: str = "http://flink-jobmanager:8081") -> dict:
    """Get basic info about a Flink cluster."""
    import requests
    r = requests.get(f"{jobmanager_url}/config", timeout=10)
    r.raise_for_status()
    return r.json()


# ------------------------------------------------------------------
# Trino (official DBAPI client)
# ------------------------------------------------------------------
def trino_connect(host: str, port: int = 8080,
                  user: str = "admin",
                  catalog: str = "hive",
                  schema: str = "default",
                  http_scheme: str = "http"):
    """Connect to a Trino cluster (DBAPI 2.0)."""
    from trino.dbapi import connect

    return connect(
        host=host, port=port, user=user,
        catalog=catalog, schema=schema,
        http_scheme=http_scheme,
    )


def trino_query(host: str, sql: str,
                port: int = 8080, user: str = "admin",
                catalog: str = "hive", schema: str = "default"):
    """Run SQL on Trino and return a pandas DataFrame."""
    import pandas as pd

    conn = trino_connect(host, port=port, user=user,
                         catalog=catalog, schema=schema)
    cur = conn.cursor()
    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    return pd.DataFrame(rows, columns=cols)


def trino_catalogs(host: str, port: int = 8080,
                   user: str = "admin") -> list[str]:
    """List catalogs on a Trino cluster."""
    conn = trino_connect(host, port=port, user=user,
                         catalog="system", schema="metadata")
    cur = conn.cursor()
    cur.execute("SHOW CATALOGS")
    return [row[0] for row in cur.fetchall()]


# ------------------------------------------------------------------
# Generic SQLAlchemy (any DB with a URI)
# ------------------------------------------------------------------
def sqlalchemy_engine(uri: str):
    """
    Create a SQLAlchemy engine for any database.

    Examples
    --------
    sqlalchemy_engine("postgresql://user:pass@host:5432/db")
    sqlalchemy_engine("mysql+pymysql://user:pass@host:3306/db")
    sqlalchemy_engine("mssql+pyodbc://user:pass@dsn")
    """
    from sqlalchemy import create_engine

    return create_engine(uri)
