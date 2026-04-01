#!/usr/bin/env python3
"""Entrypoint for nanobot gateway in Docker.

Resolves environment variables into config.json at runtime,
then execs into nanobot gateway.
"""

import json
import os
from pathlib import Path


def main():
    config_path = Path("/app/nanobot/config.json")
    resolved_path = Path("/app/nanobot/config.resolved.json")
    workspace_path = Path("/app/nanobot/workspace")

    # Read base config
    with open(config_path, "r") as f:
        config = json.load(f)

    # Override provider API key and base URL from env vars
    if "LLM_API_KEY" in os.environ:
        config["providers"]["custom"]["apiKey"] = os.environ["LLM_API_KEY"]
    if "LLM_API_BASE_URL" in os.environ:
        config["providers"]["custom"]["apiBase"] = os.environ["LLM_API_BASE_URL"]
    if "LLM_API_MODEL" in os.environ:
        config["agents"]["defaults"]["model"] = os.environ["LLM_API_MODEL"]

    # Override gateway settings
    if "NANOBOT_GATEWAY_CONTAINER_ADDRESS" in os.environ:
        config["gateway"] = config.get("gateway", {})
        config["gateway"]["host"] = os.environ["NANOBOT_GATEWAY_CONTAINER_ADDRESS"]
    if "NANOBOT_GATEWAY_CONTAINER_PORT" in os.environ:
        config["gateway"] = config.get("gateway", {})
        config["gateway"]["port"] = int(os.environ["NANOBOT_GATEWAY_CONTAINER_PORT"])

    # Configure webchat channel
    if "NANOBOT_WEBCHAT_CONTAINER_ADDRESS" in os.environ:
        config["channels"] = config.get("channels", {})
        config["channels"]["webchat"] = {
            "enabled": True,
            "host": os.environ["NANOBOT_WEBCHAT_CONTAINER_ADDRESS"],
            "port": int(os.environ.get("NANOBOT_WEBCHAT_CONTAINER_PORT", "8765")),
            "allowFrom": ["*"],
        }

    # Configure MCP servers for webchat UI message delivery
    if "NANOBOT_WS_URL" in os.environ and "NANOBOT_ACCESS_KEY" in os.environ:
        config["tools"] = config.get("tools", {})
        config["tools"]["mcpServers"] = config["tools"].get("mcpServers", {})
        config["tools"]["mcpServers"]["webchat"] = {
            "command": "python",
            "args": ["-m", "mcp_webchat"],
            "env": {
                "NANOBOT_WS_URL": os.environ["NANOBOT_WS_URL"],
                "NANOBOT_ACCESS_KEY": os.environ["NANOBOT_ACCESS_KEY"],
            },
        }

    # Update LMS MCP server env vars from Docker env
    if "NANOBOT_LMS_BACKEND_URL" in os.environ:
        if "tools" not in config:
            config["tools"] = {}
        if "mcpServers" not in config["tools"]:
            config["tools"]["mcpServers"] = {}
        if "lms" not in config["tools"]["mcpServers"]:
            config["tools"]["mcpServers"]["lms"] = {
                "command": "python",
                "args": ["-m", "mcp_lms"],
            }
        if "env" not in config["tools"]["mcpServers"]["lms"]:
            config["tools"]["mcpServers"]["lms"]["env"] = {}
        config["tools"]["mcpServers"]["lms"]["env"]["NANOBOT_LMS_BACKEND_URL"] = (
            os.environ["NANOBOT_LMS_BACKEND_URL"]
        )

    if "NANOBOT_LMS_API_KEY" in os.environ:
        config["tools"]["mcpServers"]["lms"]["env"]["NANOBOT_LMS_API_KEY"] = os.environ[
            "NANOBOT_LMS_API_KEY"
        ]

    # Write resolved config
    with open(resolved_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Using config: {resolved_path}")

    # Exec into nanobot gateway
    os.execvp(
        "nanobot",
        [
            "nanobot",
            "gateway",
            "--config",
            str(resolved_path),
            "--workspace",
            str(workspace_path),
        ],
    )


if __name__ == "__main__":
    main()
