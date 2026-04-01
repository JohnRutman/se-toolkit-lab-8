"""MCP server exposing VictoriaLogs and VictoriaTraces as typed tools."""

import asyncio
import json
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from pydantic import BaseModel, Field


class LogsSearchParams(BaseModel):
    """Search parameters for VictoriaLogs."""

    query: str = Field(description="LogsQL query string")
    limit: int = Field(default=100, description="Max number of log entries to return")


class LogsErrorCountParams(BaseModel):
    """Parameters for counting errors."""

    service: str = Field(default="Learning Management Service", description="Service name")
    minutes: int = Field(default=60, description="Time window in minutes")


class TracesListParams(BaseModel):
    """Parameters for listing traces."""

    service: str = Field(default="Learning Management Service", description="Service name")
    limit: int = Field(default=20, description="Max number of traces to return")


class TracesGetParams(BaseModel):
    """Parameters for getting a specific trace."""

    trace_id: str = Field(description="Trace ID to fetch")


async def _text(data: Any) -> list[TextContent]:
    """Convert data to MCP text response."""
    if isinstance(data, BaseModel):
        payload = data.model_dump()
    else:
        payload = data
    return [TextContent(type="text", text=json.dumps(payload, ensure_ascii=False, default=str))]


def create_server(victorialogs_url: str, victoriatraces_url: str) -> Server:
    """Create MCP server with observability tools."""
    server = Server("mcp-obs")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="logs_search",
                description="Search logs in VictoriaLogs using LogsQL query",
                inputSchema=LogsSearchParams.model_json_schema(),
            ),
            Tool(
                name="logs_error_count",
                description="Count errors per service over a time window",
                inputSchema=LogsErrorCountParams.model_json_schema(),
            ),
            Tool(
                name="traces_list",
                description="List recent traces for a service from VictoriaTraces",
                inputSchema=TracesListParams.model_json_schema(),
            ),
            Tool(
                name="traces_get",
                description="Fetch a specific trace by ID from VictoriaTraces",
                inputSchema=TracesGetParams.model_json_schema(),
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                if name == "logs_search":
                    args = LogsSearchParams.model_validate(arguments or {})
                    return await _logs_search(client, victorialogs_url, args)
                elif name == "logs_error_count":
                    args = LogsErrorCountParams.model_validate(arguments or {})
                    return await _logs_error_count(client, victorialogs_url, args)
                elif name == "traces_list":
                    args = TracesListParams.model_validate(arguments or {})
                    return await _traces_list(client, victoriatraces_url, args)
                elif name == "traces_get":
                    args = TracesGetParams.model_validate(arguments or {})
                    return await _traces_get(client, victoriatraces_url, args)
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
            except Exception as exc:
                return [TextContent(type="text", text=f"Error: {type(exc).__name__}: {exc}")]

    return server


async def _logs_search(client: httpx.AsyncClient, base_url: str, args: LogsSearchParams) -> list[TextContent]:
    """Search logs using VictoriaLogs LogsQL API."""
    url = f"{base_url}/select/logsql/query"
    params = {"query": args.query, "limit": args.limit}
    response = await client.post(url, params=params)
    response.raise_for_status()
    # VictoriaLogs returns newline-delimited JSON
    lines = response.text.strip().split("\n") if response.text else []
    results = [json.loads(line) for line in lines if line.strip()]
    return await _text({"count": len(results), "entries": results[:args.limit]})


async def _logs_error_count(client: httpx.AsyncClient, base_url: str, args: LogsErrorCountParams) -> list[TextContent]:
    """Count errors in VictoriaLogs."""
    query = f'_time:{args.minutes}m service.name:"{args.service}" severity:ERROR'
    url = f"{base_url}/select/logsql/query"
    params = {"query": query, "limit": 1000}
    response = await client.post(url, params=params)
    response.raise_for_status()
    lines = response.text.strip().split("\n") if response.text else []
    error_count = len([l for l in lines if l.strip()])
    return await _text({"service": args.service, "time_window_minutes": args.minutes, "error_count": error_count})


async def _traces_list(client: httpx.AsyncClient, base_url: str, args: TracesListParams) -> list[TextContent]:
    """List traces from VictoriaTraces Jaeger API."""
    url = f"{base_url}/select/jaeger/api/traces"
    params = {"service": args.service, "limit": args.limit}
    response = await client.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    # Jaeger API returns {"data": [...]}
    traces = data.get("data", [])
    summary = [
        {
            "trace_id": t.get("traceID"),
            "spans": len(t.get("spans", [])),
            "service": args.service,
        }
        for t in traces[:args.limit]
    ]
    return await _text({"count": len(summary), "traces": summary})


async def _traces_get(client: httpx.AsyncClient, base_url: str, args: TracesGetParams) -> list[TextContent]:
    """Get specific trace from VictoriaTraces Jaeger API."""
    url = f"{base_url}/select/jaeger/api/traces/{args.trace_id}"
    response = await client.get(url)
    response.raise_for_status()
    data = response.json()
    # Jaeger API returns {"data": [...]}
    traces = data.get("data", [])
    if not traces:
        return await _text({"error": "Trace not found", "trace_id": args.trace_id})
    trace = traces[0]
    spans = trace.get("spans", [])
    span_summary = [
        {
            "span_id": s.get("spanID"),
            "operation": s.get("operationName"),
            "service": s.get("process", {}).get("serviceName"),
            "duration_ms": s.get("duration", 0) // 1000,
        }
        for s in spans
    ]
    return await _text({
        "trace_id": args.trace_id,
        "span_count": len(spans),
        "spans": span_summary,
    })


async def main() -> None:
    """Run the MCP server."""
    import os

    victorialogs_url = os.environ.get("VICTORIALOGS_URL", "http://localhost:42010")
    victoriatraces_url = os.environ.get("VICTORIATRACES_URL", "http://localhost:42011")

    server = create_server(victorialogs_url, victoriatraces_url)
    async with stdio_server() as (read_stream, write_stream):
        init_options = server.create_initialization_options()
        await server.run(read_stream, write_stream, init_options)


if __name__ == "__main__":
    asyncio.run(main())
