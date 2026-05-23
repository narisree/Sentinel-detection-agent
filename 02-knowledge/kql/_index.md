# KQL Reference — Index

Reference files for Kusto Query Language (KQL) as used in Microsoft Sentinel. Consult these files to look up correct syntax, operator behavior, and function signatures before writing queries.

| File | Purpose |
|------|---------|
| [syntax-reference.md](./syntax-reference.md) | Core KQL syntax: tabular operators, time filtering, string operators, type casting, null handling, conditionals, array/bag functions, common pitfalls |
| [operators-reference.md](./operators-reference.md) | Detailed operator reference: join kinds with text diagrams, union parameters, summarize patterns, make-series, parse/parse_json, extract/extract_all, split, bag_unpack, performance notes and materialize() guidance |
| [functions-reference.md](./functions-reference.md) | All built-in functions: datetime, string, math, type-checking, encoding, IP; aggregation functions; window functions (row_number, prev, next); user-defined functions; toscalar(); series_ functions; geo functions |

## Quick Lookup

- **Which join kind to use?** → operators-reference.md §2
- **Time filtering syntax?** → syntax-reference.md §2
- **String matching operators?** → syntax-reference.md §3
- **Aggregation functions (count, dcount, make_set)?** → functions-reference.md §2
- **Date arithmetic (datetime_diff, format_datetime)?** → functions-reference.md §1.1
- **parse vs parse_json?** → operators-reference.md §7–8
- **Anomaly detection (make-series, series_decompose_anomalies)?** → functions-reference.md §7, operators-reference.md §5
- **materialize() usage?** → operators-reference.md §12
- **User-defined tabular functions?** → functions-reference.md §4

Last updated: 2026-05-23
