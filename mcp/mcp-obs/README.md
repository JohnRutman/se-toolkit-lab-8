# MCP Observability Server

MCP server providing tools for querying VictoriaLogs and VictoriaTraces.

## Tools

- `logs_search` — Search logs using LogsQL query
- `logs_error_count` — Count errors per service over time window
- `traces_list` — List recent traces for a service
- `traces_get` — Fetch specific trace by ID

## Usage

```bash
uv run python -m mcp_obs
```

## Environment Variables

- `VICTORIALOGS_URL` — VictoriaLogs base URL (default: http://localhost:42010)
- `VICTORIATRACES_URL` — VictoriaTraces base URL (default: http://localhost:42011)
