# Connecting BI Tools to DuckDB

DuckDB is an in-process database, but BI tools like Tableau,
Power BI, and Qlik Sense can connect to it through **ODBC** or
**JDBC** drivers.

This guide shows how to connect each tool.

## Setup

The toolkit automatically downloads both drivers during
`python setup.py`. They are stored in:

```text
runtime/duckdb/drivers/
├── duckdb_jdbc.jar          <- JDBC driver
├── duckdb_odbc.dll          <- ODBC driver (Windows)
├── odbc_install.exe         <- ODBC installer (Windows)
└── README.md
```

To verify they're installed:

```python
from toolkit.bi_drivers import print_drivers_status
print_drivers_status()
```

### Manual download

If you need to download them later:

```python
from toolkit.maintenance import install_duckdb_extension
# Drivers are installed by setup.py automatically
# Or run setup.py again:
#   python setup.py
```

---

## Tableau

Tableau connects via **JDBC**.

### 1. Copy the JDBC driver

The toolkit can do it for you:

```python
from toolkit.bi_drivers import copy_jdbc_to_tableau
copy_jdbc_to_tableau()
```

Or manually:

- **Windows:** Copy `duckdb_jdbc.jar` to
  `C:\Program Files\Tableau\<version>\Drivers\`
- **macOS:** Copy to `~/Library/Tableau/Drivers/`

### 2. Restart Tableau

JDBC drivers are loaded at startup.

### 3. Connect

1. Open Tableau
2. **Connect → To a Server → Other Databases (JDBC)**
3. Fill in:
   - **URL:** `jdbc:duckdb:/full/path/to/my_database.duckdb`
   - **Dialect:** `PostgreSQL`
   - **Username:** (leave empty)
   - **Password:** (leave empty)
4. Click **Sign In**

### 4. Known limitations

- Tableau writes limited operations through JDBC. For read-only
  analysis, this is fine.
- For best performance, export data to **Parquet** first:

  ```python
  import duckdb
  con = duckdb.connect()
  con.execute("COPY (SELECT * FROM sales) TO 'exports/sales.parquet' (FORMAT PARQUET)")
  ```

  Then connect Tableau to the Parquet file directly (no driver needed).

---

## Power BI

Power BI connects via **ODBC**.

### 1. Install the ODBC driver

Run this as **Administrator** in a Command Prompt:

```cmd
cd C:\projects\duckdb-toolkit\runtime\duckdb\drivers
odbc_install.exe
```

Or from Python (still needs admin):

```python
from toolkit.bi_drivers import install_odbc_driver
install_odbc_driver()
```

### 2. Create a System DSN

Open **ODBC Data Sources (64-bit)** from the Start Menu:

1. Go to the **System DSN** tab
2. Click **Add...**
3. Select **DuckDB Driver**
4. Fill in:
   - **Data Source Name:** `DuckDB_Data`
   - **Database:** `C:\full\path\to\my_database.duckdb`
5. Click **OK**

### 3. Connect Power BI

1. Open Power BI Desktop
2. **Get Data → ODBC**
3. Select the `DuckDB_Data` DSN
4. Load tables

### 4. Known limitations

- ODBC is **read-only** in DuckDB for Power BI
- DSN must be created manually (or via PowerShell with admin)
- For write operations, export to Parquet

### Automated DSN creation (PowerShell as Admin)

```powershell
Add-OdbcDsn -Name "DuckDB_Data" `
            -DriverName "DuckDB Driver" `
            -DsnType "System" `
            -Platform "64-bit" `
            -SetPropertyValue @("Database=C:\full\path\to\my_database.duckdb")
```

---

## Qlik Sense

Qlik Sense supports both **ODBC** and **JDBC**.

### Option A: ODBC (recommended)

1. Install the ODBC driver (see Power BI section above)
2. Create a System DSN
3. In Qlik Sense: **Create new connection → ODBC**
4. Select the DuckDB DSN
5. Use in the Data Load Editor:

   ```sql
   LOAD *;
   SQL SELECT * FROM sales WHERE status = 'active';
   ```

### Option B: JDBC

```python
from toolkit.bi_drivers import copy_jdbc_to_qlik
copy_jdbc_to_qlik()
```

Then in Qlik Sense:

- **Data load editor** → **Create new connection** → **Qlik JDBC**
- **URL:** `jdbc:duckdb:/full/path/to/my_database.duckdb`
- **Class name:** `org.duckdb.DuckDBDriver`

---

## Get connection info

Print connection strings for all tools:

```python
from toolkit.bi_drivers import print_connection_info
print_connection_info("runtime/my_database.duckdb")
```

Output:

```text
==================================================================
  BI Tool Connection Info
==================================================================

  DuckDB file: C:\projects\duckdb-toolkit\runtime\my_database.duckdb
  JDBC driver: C:\projects\duckdb-toolkit\runtime\duckdb\drivers\duckdb_jdbc.jar

  -- Tableau (JDBC) --------------------------------------------
     Driver path: C:\...\duckdb_jdbc.jar
     JDBC URL:    jdbc:duckdb:C:\...\my_database.duckdb
     Dialect:     PostgreSQL

  -- Power BI (ODBC) -------------------------------------------
     1. Run installer: C:\...\odbc_install.exe
     2. Create System DSN pointing to: C:\...\my_database.duckdb
     3. In Power BI: Get Data -> ODBC -> DSN

  -- Qlik Sense (ODBC or JDBC) ---------------------------------
     ODBC DSN or JDBC driver path
```

---

## Best practices

### 1. Use Parquet for analytics

For **fast** BI queries, export data to Parquet and connect the
BI tool to the Parquet file:

```python
import duckdb
con = duckdb.connect("runtime/analytics.duckdb", read_only=True)
con.execute('''
    COPY (
        SELECT
            DATE_TRUNC('month', order_date) AS month,
            region,
            SUM(amount) AS revenue
        FROM orders
        WHERE status = 'active'
        GROUP BY 1, 2
    ) TO 'exports/monthly_revenue.parquet' (FORMAT PARQUET)
''')
```

Then in Tableau / Power BI, connect to `monthly_revenue.parquet`
directly. No driver needed, much faster.

### 2. Refresh strategy

- **Small tables:** connect live to DuckDB via ODBC/JDBC
- **Large tables:** export to Parquet on schedule, connect BI tool
  to Parquet
- **Aggregated dashboards:** pre-compute with DuckDB SQL, save
  to Parquet

### 3. Avoid write conflicts

DuckDB allows only **one writer** at a time. If BI tools connect
in read-only mode while you're also running DuckDB queries:

- Use `read_only=True` in DuckDB connections
- Or use separate `.duckdb` files (one for writes, one for BI)

---

## Troubleshooting

### "Driver not found" in Tableau

- Verify `duckdb_jdbc.jar` is in Tableau's `Drivers` folder
- Restart Tableau completely
- Check Tableau's logs at `%APPDATA%\Tableau\`

### Power BI cannot see the DSN

- Make sure you created a **System DSN** (not User)
- Verify it's a **64-bit** DSN (Power BI Desktop is 64-bit)
- Restart Power BI Desktop

### Qlik Sense JDBC error

- Ensure Java 8+ is installed
- Place the JAR in `/opt/qlik/customdata` (Linux)
- Restart Qlik Sense services

### "Database is locked"

- DuckDB only allows one writer at a time
- Close other connections (Jupyter, Python scripts)
- Or connect in read-only mode:

  ```python
  import duckdb
  con = duckdb.connect("my_database.duckdb", read_only=True)
  ```

### Slow queries from BI tools

- Check if the tool is using ODBC or JDBC
- For big tables, use Parquet export (see best practices above)
- Add indexes on the DuckDB tables you query most

---

## Summary

| Tool | Driver | Read | Write | Setup |
|---|---|---|---|---|
| **Tableau** | JDBC | Yes | No | Copy JAR |
| **Power BI** | ODBC | Yes | No | Install + DSN |
| **Qlik Sense** | ODBC or JDBC | Yes | No | Either |

For all tools: **Parquet is fastest** for large analytics.

## Next Steps

- [Offline installation](OFFLINE_INSTALL.md)
- [AI Models](AI_MODELS.md)
- [RAG](RAG.md)
