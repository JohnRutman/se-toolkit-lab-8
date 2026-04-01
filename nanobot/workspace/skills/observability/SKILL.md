---
name: observability
description: Use observability tools to investigate errors and traces
always: true
---

# Observability Skill

Use VictoriaLogs and VictoriaTraces MCP tools to investigate system errors and trace request flows.

## Available Tools

- `logs_search` — Search logs using LogsQL query
- `logs_error_count` — Count errors per service over time window
- `traces_list` — List recent traces for a service
- `traces_get` — Fetch specific trace by ID
- `cron` — Schedule recurring jobs

## Strategy

### When the user asks "What went wrong?" or "Check system health":

1. **Start with `logs_error_count`** — Check if there are recent errors:
   - Use `service="Learning Management Service"` and `minutes=10` for recent errors
   - If error_count > 0, proceed to step 2

2. **Use `logs_search`** — Find specific error details:
   - Query: `_time:10m service.name:"Learning Management Service" severity:ERROR`
   - Look for `trace_id` in the error log entries
   - Note the `event` field (e.g., `db_query`, `request_completed`)
   - Check `status` code (404, 500, etc.)

3. **If you find a `trace_id`, use `traces_get`** — Fetch the full trace:
   - Inspect the span hierarchy
   - Find where the error occurred (which span has the failure)
   - Note the operation that failed

4. **Summarize findings concisely**:
   - State whether errors were found
   - Describe the error type and affected component
   - Mention both log evidence AND trace evidence
   - Name the failing operation (e.g., "PostgreSQL connection failed in db.items")
   - Do NOT dump raw JSON — provide a human-readable summary

### When the user asks about a specific request:

1. Ask for the `trace_id` if not provided
2. Use `traces_get` to fetch the trace
3. Explain the span hierarchy and timing

### Query tips:

- For recent LMS errors: `_time:10m service.name:"Learning Management Service" severity:ERROR`
- For a specific event: `_time:1h event:"db_query" severity:ERROR`
- For a specific trace: Use `traces_get` with the `trace_id` from logs

## Response style

- Keep responses concise and focused on the user's question
- Highlight key findings (error type, affected service, trace outcome)
- Use bullet points or short paragraphs
- Only include raw data (like trace IDs) when relevant for debugging
- **Always cite both log evidence and trace evidence** when investigating failures
