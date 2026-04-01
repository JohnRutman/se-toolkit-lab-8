---
name: lms
description: Use LMS MCP tools for live course data
always: true
---

# LMS Skill

Use LMS MCP tools to access live course data from the LMS backend.

## Available Tools

- `lms_health` — Check if the LMS backend is healthy and get item count
- `lms_labs` — List all available labs
- `lms_learners` — List all registered learners
- `lms_pass_rates` — Get pass rates for a specific lab (requires `lab` parameter)
- `lms_timeline` — Get submission timeline for a specific lab (requires `lab` parameter)
- `lms_groups` — Get group performance for a specific lab (requires `lab` parameter)
- `lms_top_learners` — Get top learners for a specific lab (requires `lab` parameter, optional `limit`)
- `lms_completion_rate` — Get completion rate for a specific lab (requires `lab` parameter)
- `lms_sync_pipeline` — Trigger the LMS sync pipeline

## Strategy

### When the user asks about scores, pass rates, completion, groups, timeline, or top learners:

1. **Check if a lab is specified** — If the user did not name a specific lab, call `lms_labs` first to get the list of available labs.

2. **If multiple labs are available** — Use the `structured-ui` skill to present a choice to the user. For each lab, use:
   - `label`: The lab's `title` field (e.g., "Lab 01 – Products, Architecture & Roles")
   - `value`: The lab's `id` field (e.g., "lab-01")

3. **Once a lab is selected** — Call the appropriate tool:
   - For scores → `lms_pass_rates` with `lab` parameter
   - For timeline → `lms_timeline` with `lab` parameter
   - For groups → `lms_groups` with `lab` parameter
   - For top learners → `lms_top_learners` with `lab` and optional `limit`
   - For completion → `lms_completion_rate` with `lab` parameter

### Formatting results

- **Percentages**: Format as `XX.X%` (e.g., "89.1%" not "0.891")
- **Counts**: Show as integers (e.g., "258 students" not "258.0")
- **Dates**: Keep ISO format or format nicely depending on context
- **Tables**: Present structured data in table format when comparing multiple values

### Response style

- Keep responses concise and focused on the data
- Highlight key insights (e.g., "Lab 02 has the lowest pass rate at 89.1%")
- When showing multiple labs' data, use tables for clarity
- If the backend is unhealthy or returns no data, inform the user clearly

### When the user asks "what can you do?"

Explain that you can access live LMS data including:
- Lab availability and details
- Student performance metrics (pass rates, completion rates)
- Submission timelines
- Group performance comparisons
- Top learners by lab
- Overall system health

Always clarify that you need a specific lab name for detailed metrics.
