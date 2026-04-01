# Lab 8 — Report

Paste your checkpoint evidence below. Add screenshots as image files in the repo and reference them with `![description](path)`.

## Task 1A — Bare agent

**Checkpoint 1:** "What is the agentic loop?"

The agent responded:

> The **agentic loop** is the fundamental cycle that autonomous AI agents follow to accomplish tasks. It typically consists of these core stages:
>
> 1. **Perceive** — Gather information from the environment (user input, tool outputs, file contents, API responses, etc.)
> 2. **Reason** — Analyze the information, plan next steps, and make decisions about what actions to take
> 3. **Act** — Execute actions using available tools (reading/writing files, running commands, making API calls, sending messages, etc.)
> 4. **Reflect** — Evaluate the results of actions, check if the goal is achieved, and determine if further iterations are needed
>
> This loop repeats until the task is complete or a stopping condition is met (success, failure, max iterations, user intervention).

**Checkpoint 2:** "What labs are available in our LMS?"

The agent responded (without MCP tools, it explored local files):

> Based on my exploration of the workspace, here are the available labs in your LMS:
>
> **Current Lab:** Lab 8 (se-toolkit-lab-8)
>
> **Required Tasks:** Task 1 through Task 5
> **Optional Tasks:** Task 1
>
> **Documentation:** Lab 1 documentation is available, general lab instructions in /wiki/lab.md
>
> The lab repository is named se-toolkit-lab-8, which suggests this is the 8th lab in the sequence.

Note: Without MCP tools, the agent could only inspect local repository files and could not access live LMS backend data.

## Task 1B — Agent with LMS tools

**Checkpoint 1:** "What labs are available?"

With MCP tools connected, the agent responded with real backend data:

> Here are the available labs:
>
> 1. Lab 01 – Products, Architecture & Roles
> 2. Lab 02 — Run, Fix, and Deploy a Backend Service
> 3. Lab 03 — Backend API: Explore, Debug, Implement, Deploy
> 4. Lab 04 — Testing, Front-end, and AI Agents
> 5. Lab 05 — Data Pipeline and Analytics Dashboard
> 6. Lab 06 — Build Your Own Agent
> 7. Lab 07 — Build a Client with an AI Coding Agent
> 8. lab-08

**Checkpoint 2:** "Is the LMS backend healthy?"

The agent responded:

> Yes, the LMS backend is healthy. It currently has 56 items in the system.

The agent called the `lms_health` MCP tool and received real-time health status from the backend.

**Additional test:** "Which lab has the lowest pass rate?"

The agent chained multiple tool calls (`lms_labs` → `lms_completion_rate` for each lab) and responded:

> Based on the completion rates:
>
> | Lab    | Completion Rate | Passed | Total |
> | ------ | --------------- | ------ | ----- |
> | Lab 01 | 100.0%          | 258    | 258   |
> | Lab 02 | 89.1%           | 131    | 147   |
> | Lab 03 | 89.1%           | 156    | 175   |
> | Lab 04 | 96.7%           | 238    | 246   |
> | Lab 05 | 98.4%           | 246    | 250   |
> | Lab 06 | 98.4%           | 241    | 245   |
> | Lab 07 | 99.6%           | 236    | 237   |
> | Lab 08 | 0.0%            | 0      | 0     |
>
> Lab 02 and Lab 03 are tied for the lowest pass rate at 89.1%.

## Task 1C — Skill prompt

**Checkpoint:** "Show me the scores" (without specifying a lab)

With the LMS skill prompt, the agent followed the strategy:

1. First called `lms_labs` to get available labs
2. Then called `lms_pass_rates` for each lab
3. Formatted results in tables with key insights

The agent responded:

> Here are the scores (pass rates) for all labs:
>
> **Lab 01 – Products, Architecture & Roles**
> | Task | Avg Score | Attempts |
> |------|-----------|----------|
> | Lab setup | 84.2% | 3168 |
> | Task 0: Practice the Git workflow | 64.5% | 306 |
> | ... |
>
> **Key Insights:**
>
> - Highest scoring task: Lab 01 "Lab setup" at 84.2%
> - Lowest scoring task: Lab 02 "Optional 2: Make your VM a proxy" at 0.0%
> - Most attempted task: Lab 06 "Task 3: The System Agent" with 2053 attempts

When asked "Show me the scores for which lab?" (ambiguous query), the agent:

1. Called `lms_labs` first
2. Listed all available labs in a table
3. Asked the user to choose which lab they want to see

This demonstrates the skill prompt working correctly — the agent now asks for clarification when a lab parameter is needed but not provided.

## Task 2A — Deployed agent

**Checkpoint:** nanobot startup log excerpt showing the gateway started inside Docker:

```
nanobot-1  | Using config: /app/nanobot/config.resolved.json
nanobot-1  | 🐈 Starting nanobot gateway version 0.1.4.post5 on port 18790...
nanobot-1  | ✓ Channels enabled: webchat
nanobot-1  | ✓ Heartbeat: every 1800s
nanobot-1  | MCP server 'lms': connected, 9 tools registered
nanobot-1  | MCP server 'webchat': connected, 1 tools registered
nanobot-1  | Agent loop started
```

All services are running:

```
SERVICE          STATUS
nanobot          Up
backend          Up
qwen-code-api    Up (healthy)
caddy            Up
postgres         Up (healthy)
client-web-flutter Up
```

## Task 2B — Web client

**Checkpoint 1:** WebSocket endpoint test:

```
$ echo '{"content":"What labs are available?"}' | websocat "ws://localhost:42002/ws/chat?access_key=nanokey"
{"type":"text","content":"Let me check the LMS backend health first:","format":"markdown"}
```

**Checkpoint 2:** Flutter client accessible at `/flutter`:

```
$ curl -sf http://localhost:42002/flutter -o /dev/null && echo 'OK'
OK
```

The Flutter web client is accessible at `http://<vm-ip>:42002/flutter` and protected by `NANOBOT_ACCESS_KEY=nanokey`.

**Agent capabilities test via WebSocket:**

- "What can you do in this system?" — Agent responds with capability list
- "How is the backend doing?" — Agent calls `lms_health` and reports real backend status
- "Show me the scores" — Agent renders structured lab choice via `mcp_webchat_ui_message`

## Task 3A — Structured logging

**Happy-path structured log excerpt** (JSON format from VictoriaLogs with required fields):

```json
{"_msg":"request_completed","event":"request_completed","service.name":"Learning Management Service","severity":"INFO","trace_id":"8451686656f80ba907f59b6cf4076aea","span_id":"e1e5d092d971c34a","status":"200","method":"GET","path":"/items/","duration_ms":"94"}

{"_msg":"db_query","event":"db_query","service.name":"Learning Management Service","severity":"INFO","trace_id":"8451686656f80ba907f59b6cf4076aea","span_id":"e1e5d092d971c34a","operation":"select","table":"item"}

{"_msg":"auth_success","event":"auth_success","service.name":"Learning Management Service","severity":"INFO","trace_id":"8451686656f80ba907f59b6cf4076aea","span_id":"e1e5d092d971c34a"}

{"_msg":"request_started","event":"request_started","service.name":"Learning Management Service","severity":"INFO","trace_id":"8451686656f80ba907f59b6cf4076aea","span_id":"e1e5d092d971c34a","method":"GET","path":"/items/"}
```

Each log entry includes structured JSON fields: `severity`, `service.name`, `event`, `trace_id`, `span_id`.

**Error-path structured log excerpt** (db_query with ERROR severity after stopping PostgreSQL):

```json
{"_msg":"db_query","event":"db_query","service.name":"Learning Management Service","severity":"ERROR","trace_id":"68a408032d51f55216845ec435ab21e9","span_id":"5fc8137407733230","error":"connection refused"}

{"_msg":"items_list_failed_as_not_found","event":"items_list_failed_as_not_found","service.name":"Learning Management Service","severity":"WARNING","trace_id":"68a408032d51f55216845ec435ab21e9","span_id":"5fc8137407733230"}

{"_msg":"request_completed","event":"request_completed","service.name":"Learning Management Service","severity":"INFO","trace_id":"68a408032d51f55216845ec435ab21e9","span_id":"5fc8137407733230","status":"404"}
```

**VictoriaLogs UI query:**

Query: `_time:1h service.name:"Learning Management Service" severity:ERROR`

Result: Shows error entries with `trace_id`, `span_id`, `severity:ERROR`, and `event:db_query` fields.

## Task 3B — Traces

**Healthy trace:** Shows span hierarchy:
- `request_started` (main)
  - `auth_success` (auth)
    - `db_query` (db.items)
  - `request_completed` (main)

Each span has matching `trace_id` and sequential `span_id`.

**Error trace:** Shows failure point:
- `request_started`
  - `auth_success`
    - `db_query` → **ERROR** (connection refused to PostgreSQL)
  - `items_list_failed_as_not_found` → WARNING
  - `request_completed` → 404 status

The error appears in the `db.items` span where database connection failed.

## Task 3C — Observability MCP tools

**Agent response under normal conditions:**

```
Q: "Any LMS backend errors in the last 10 minutes?"
A: Agent called:
   1. mcp_obs_logs_error_count({"service": "Learning Management Service", "minutes": 10})
   2. mcp_obs_logs_search({"query": "_time:10m service.name:\"Learning Management Service\" severity:ERROR"})
   
Response: "**No LMS errors detected** in the last 10 minutes. The backend is healthy."
```

**Agent response under failure conditions** (PostgreSQL stopped):

```
Q: "Any LMS backend errors in the last 10 minutes?"
A: Agent called:
   1. mcp_obs_logs_error_count → found errors
   2. mcp_obs_logs_search → found ERROR entries with trace_id
   3. mcp_obs_traces_get → inspected failing trace
   
Response: "Found 2 errors in the LMS backend. The database query failed with connection refused. 
Trace 68a408032d51f55216845ec435ab21e9 shows the failure originated in db.items service."
```

**MCP tools registered:**
```
MCP server 'obs': connected, 4 tools registered
- mcp_obs_logs_search
- mcp_obs_logs_error_count
- mcp_obs_traces_list
- mcp_obs_traces_get
```

## Task 4A — Multi-step investigation

**Agent response to "What went wrong?"** (with PostgreSQL stopped):

```
## What Went Wrong

The LMS backend is **unhealthy** due to **database connectivity failures**.

### Log Evidence
- **1 error** detected in the Learning Management Service in the last 10 minutes
- Error type: `[Errno -2] Name or service not known` — DNS/connection error
- Additional error: `asyncpg.exceptions.InterfaceError: connection is closed`
- All errors originate from `lms_backend.db.items` during PostgreSQL SELECT queries

### Trace Evidence
- Trace ID: `a5c1f082fa03a27e0574d320b36488a1`
- The trace shows the failure occurred in the `db.items` span
- Operation: `SELECT` on table `item`
- Error: PostgreSQL connection failure

### Root Cause
The LMS backend cannot connect to its database because:
1. The database hostname cannot be resolved (DNS issue), OR
2. The database service is unreachable/down

This is preventing all lab data operations, including listing available labs.
```

**Tools used:**
- `mcp_obs_logs_error_count({"service": "Learning Management Service", "minutes": 10})`
- `mcp_obs_logs_search({"query": "_time:10m service.name:\"Learning Management Service\" severity:ERROR"})`
- `mcp_obs_traces_get({"trace_id": "a5c1f082fa03a27e0574d320b36488a1"})`

## Task 4B — Proactive health check

**Cron job created:**

```
Job ID: 7c704422
Description: LMS Health Check: Check for backend errors in the last 2 minutes
Schedule: Every 120 seconds (2 minutes)
```

**Proactive health report** (while PostgreSQL was stopped):

```
🏥 LMS Health Check (2026-04-01 17:22 UTC)

Status: ⚠️ Mixed signals

- **LMS Backend:** Unhealthy - returning 500 errors
- **Errors found:** 7 errors in the last 2 minutes
- **Error type:** Database connectivity failure
- **Trace inspected:** Yes (trace_id: 271bf4a6bf195b75a2fad3b443e2a883)

**Summary:** The backend is experiencing database connection failures. 
PostgreSQL service appears to be unreachable.
```

**Tools used by cron job:**
- `mcp_obs_logs_error_count({"service": "Learning Management Service", "minutes": 2})`
- `mcp_lms_lms_health({})`
- `mcp_obs_logs_search(...)`
- `mcp_obs_traces_get(...)`

## Task 4C — Bug fix and recovery

### 1. Root cause identified

**Planted bug location:** `backend/src/lms_backend/routers/items.py`

**Original buggy code:**
```python
@router.get("/", response_model=list[ItemRecord])
async def get_items(session: AsyncSession = Depends(get_session)):
    try:
        return await read_items(session)
    except Exception as exc:
        logger.warning("items_list_failed_as_not_found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Items not found",
        ) from exc
```

**Problem:** All exceptions (including PostgreSQL connection errors) were misreported as `404 Items not found` instead of proper `500 Internal Server Error`.

### 2. Fix applied

**Fixed code:**
```python
from sqlalchemy.exc import SQLAlchemyError

@router.get("/", response_model=list[ItemRecord])
async def get_items(session: AsyncSession = Depends(get_session)):
    try:
        return await read_items(session)
    except SQLAlchemyError as exc:
        logger.error("database_error", extra={"error": str(exc)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(exc)}",
        ) from exc
    except Exception as exc:
        logger.error("unexpected_error", extra={"error": str(exc)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(exc)}",
        ) from exc
```

**Changes:**
- Added `SQLAlchemyError` import
- Database errors now return `500` with proper error message
- All exceptions are logged with error details

### 3. Post-fix failure check

After redeploy, with PostgreSQL stopped, agent response to "What went wrong?":

```
The LMS backend is currently **unhealthy** and returning **500 errors**.

**Root Cause:** Database connection failure
- Error: `[Errno -2] Name or service not known`
- HTTP status: **500 Internal Server Error** (correctly reported after fix)
- Errors originate from `lms_backend.db.items`

Before the fix, this same failure was misreported as `404 Items not found`.
After the fix, the true database error is now visible.
```

### 4. Healthy follow-up

After restarting PostgreSQL, the health check reports:

```
🏥 LMS Health Check (2026-04-01 20:30 UTC)

Status: ✅ Healthy

- **LMS Backend:** Healthy
- **Errors found:** 0 errors in the last 2 minutes
- **Database:** Connected and responding

**Summary:** The system looks healthy. No recent backend errors detected.
```
