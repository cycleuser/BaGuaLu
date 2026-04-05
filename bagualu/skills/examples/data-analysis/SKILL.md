---
name: data-analysis
description: Analyze data files (Excel, CSV, JSON) using DuckDB SQL queries. Use when users upload data files and want insights, statistics, aggregations, filtering, or cross-file joins. Supports multi-sheet Excel workbooks and exports to CSV/JSON/Markdown.
version: "1.0.0"
allowed-tools:
  - bash
  - read
  - write
---

# Data Analysis Skill

## Overview

Comprehensive data analysis skill for BaGuaLu agents. Supports Excel, CSV, and JSON files with DuckDB-powered SQL queries.

## Capabilities

- Inspect file schemas (sheets, columns, types, row counts)
- Execute SQL queries with full SQL support (joins, aggregations, window functions)
- Generate statistical summaries
- Export results to multiple formats
- Handle large files efficiently

## Workflow

### Step 1: Inspect File

```bash
python ~/.bagualu/skills/data-analysis/scripts/analyze.py \
  --files /path/to/data.xlsx \
  --action inspect
```

### Step 2: Execute Query

```bash
python ~/.bagualu/skills/data-analysis/scripts/analyze.py \
  --files /path/to/data.xlsx \
  --action query \
  --sql "SELECT category, COUNT(*) as count, AVG(amount) as avg_amount FROM Sheet1 GROUP BY category"
```

### Step 3: Export Results

```bash
python ~/.bagualu/skills/data-analysis/scripts/analyze.py \
  --files /path/to/data.xlsx \
  --action query \
  --sql "SELECT * FROM Sheet1 WHERE amount > 1000" \
  --output-file /path/to/output.csv
```

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--files` | Yes | Space-separated paths to data files |
| `--action` | Yes | One of: `inspect`, `query`, `summary` |
| `--sql` | For query | SQL query to execute |
| `--table` | For summary | Table/sheet name to summarize |
| `--output-file` | No | Export path (CSV/JSON/MD) |

## Table Naming

- Excel sheets → table names (Sheet1, Sales, etc.)
- CSV files → filename without extension
- Use double quotes for special characters: `"2024_Sales"`

## Examples

### Basic Analysis

```sql
-- Row count
SELECT COUNT(*) FROM Sheet1

-- Top categories
SELECT category, COUNT(*) as cnt 
FROM Sheet1 
GROUP BY category 
ORDER BY cnt DESC 
LIMIT 10

-- Cross-file join
SELECT s.order_id, s.amount, c.customer_name
FROM sales s
JOIN customers c ON s.customer_id = c.id
```

### Statistical Summary

```bash
python ~/.bagualu/skills/data-analysis/scripts/analyze.py \
  --files sales.xlsx \
  --action summary \
  --table Orders
```

Returns: count, mean, std, min, max, percentiles, null counts.

## Notes

- DuckDB supports full SQL (CTEs, window functions, subqueries)
- Large files (100MB+) handled efficiently
- Automatic caching for repeated queries
- Multi-file joins supported