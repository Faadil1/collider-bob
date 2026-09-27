"""
COLLIDER MCP server for IBM Bob.

Zero third-party runtime dependencies: Bob starts this process over STDIO from
the project-level .bob/mcp.json configuration. Messages are newline-delimited
JSON-RPC 2.0, matching Bob's documented STDIO transport.

The MCP surface turns COLLIDER into a tool Bob can invoke directly:
- inspect the current semantic gate
- evaluate a pull-request semantic diff
- read canonical decision memory
- validate real LIVE_BOB interpretation bundles
- export decision memory into Bob workspace rules
- evaluate a fresh-agent replay receipt

Truth boundary:
- MCP availability is not LIVE_BOB interpretation proof.
- PRESEEDED evidence cannot be relabeled through any tool here.
- mutating rule export is not auto-approved in .bob/mcp.json.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from collider.bob_live import LiveBobEvidenceError, validate_live_bundle
from collider.bob_rules import export_decision_rules
from collider.replay import evaluate_replay_result

ROOT = Path(os.environ.get("COLLIDER_ROOT", Path.cwd())).resolve()
SERVER_NAME = "collider-semantic-ci"
SERVER_VERSION = "0.2.0"
PROTOCOL_VERSION = "2025-06-18"


def _text_result(payload: Any, *, is_error: bool = False) -> dict[str, Any]:
    text = payload if isinstance(payload, str) else json.dumps(payload, indent=2)
    result: dict[str, Any] = {
        "content": [{"type": "text", "text": text}],
    }
    if is_error:
        result["isError"] = True
    return result


def _run_json_command(args: list[str]) -> tuple[int, Any]:
    proc = subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    stdout = proc.stdout.strip()
    if stdout:
        try:
            payload: Any = json.loads(stdout)
        except json.JSONDecodeError:
            payload = {
                "stdout": stdout,
                "stderr": proc.stderr.strip(),
                "exit_code": proc.returncode,
            }
    else:
        payload = {
            "stdout": "",
            "stderr": proc.stderr.strip(),
            "exit_code": proc.returncode,
        }
    return proc.returncode, payload


TOOLS = [
    {
        "name": "collider_gate",
        "description": (
            "Evaluate COLLIDER Semantic CI on the current workspace. Returns "
            "DECISION_REQUIRED, AGENT_DRIFT, SEMANTICALLY_READY, or "
            "VERIFICATION_FAILED with evidence-backed findings."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
    {
        "name": "collider_pr_gate",
        "description": (
            "Evaluate only semantic concepts changed relative to a Git base ref. "
            "Returns MERGE_ALLOWED, MERGE_BLOCKED, or DECISION_REQUIRED."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["base_ref"],
            "properties": {
                "base_ref": {
                    "type": "string",
                    "description": "Git ref to compare against, e.g. origin/main",
                }
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "collider_decision_memory",
        "description": (
            "Read the committed COLLIDER canonical decision memory used by the "
            "PR semantic gate. This is read-only."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "default": "evidence/decisions/decision-001/decision-memory.json",
                }
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "collider_validate_live_bob",
        "description": (
            "Validate a real IBM Bob subagent interpretation bundle. Rejects "
            "PRESEEDED relabeling, missing session/task references, duplicate "
            "agent IDs, and unsupported evidence claims."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["interpretations_dir", "session_ref"],
            "properties": {
                "interpretations_dir": {"type": "string"},
                "session_ref": {"type": "string"},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "collider_export_decision_rule",
        "description": (
            "Export verified COLLIDER decision memory into a Bob workspace rule. "
            "This writes a file and therefore requires approval."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["memory_path"],
            "properties": {
                "memory_path": {"type": "string"},
                "output_path": {
                    "type": "string",
                    "default": ".bob/rules/collider-decision-memory.md",
                },
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "collider_evaluate_replay",
        "description": (
            "Evaluate actual fresh-agent replay evidence against the COLLIDER "
            "replay contract. Only LIVE_BOB_SESSION evidence can pass."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["request_path", "result_path", "canonical_value"],
            "properties": {
                "request_path": {"type": "string"},
                "result_path": {"type": "string"},
                "canonical_value": {"type": "string"},
            },
            "additionalProperties": False,
        },
    },
]


def _resolve_inside_root(path: str) -> Path:
    candidate = (ROOT / path).resolve() if not Path(path).is_absolute() else Path(path).resolve()
    if ROOT != candidate and ROOT not in candidate.parents:
        raise ValueError(f"path escapes COLLIDER workspace: {path}")
    return candidate


def call_tool(name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    args = arguments or {}

    try:
        if name == "collider_gate":
            _, payload = _run_json_command(["-m", "collider.gate", "--json"])
            return _text_result(payload)

        if name == "collider_pr_gate":
            base_ref = str(args["base_ref"]).strip()
            if not base_ref:
                raise ValueError("base_ref must be non-empty")
            _, payload = _run_json_command(
                ["-m", "collider.pr_gate", "--base-ref", base_ref, "--json"]
            )
            return _text_result(payload)

        if name == "collider_decision_memory":
            path = _resolve_inside_root(
                str(args.get(
                    "path",
                    "evidence/decisions/decision-001/decision-memory.json",
                ))
            )
            return _text_result(json.loads(path.read_text()))

        if name == "collider_validate_live_bob":
            interpretations_dir = _resolve_inside_root(str(args["interpretations_dir"]))
            session_ref = str(args["session_ref"]).strip()
            receipt = validate_live_bundle(interpretations_dir, session_ref)
            return _text_result(receipt)

        if name == "collider_export_decision_rule":
            memory_path = _resolve_inside_root(str(args["memory_path"]))
            output_path = _resolve_inside_root(
                str(args.get(
                    "output_path",
                    ".bob/rules/collider-decision-memory.md",
                ))
            )
            output = export_decision_rules(memory_path, output_path)
            return _text_result(
                {
                    "status": "EXPORTED",
                    "output": str(output.relative_to(ROOT)),
                    "truth_boundary": (
                        "Rule export records canon; future Bob compliance still "
                        "requires execution/replay evidence."
                    ),
                }
            )

        if name == "collider_evaluate_replay":
            request_path = _resolve_inside_root(str(args["request_path"]))
            result_path = _resolve_inside_root(str(args["result_path"]))
            request = json.loads(request_path.read_text())
            result = json.loads(result_path.read_text())
            verdict = evaluate_replay_result(
                request,
                result,
                str(args["canonical_value"]),
            )
            return _text_result(verdict, is_error=not verdict.get("accepted", False))

        return _text_result(f"unknown tool: {name}", is_error=True)

    except (KeyError, ValueError, OSError, json.JSONDecodeError, LiveBobEvidenceError) as exc:
        return _text_result(
            {
                "error": type(exc).__name__,
                "message": str(exc),
            },
            is_error=True,
        )


def handle_request(message: dict[str, Any]) -> dict[str, Any] | None:
    method = message.get("method")
    request_id = message.get("id")

    # Notifications intentionally receive no response.
    if request_id is None:
        return None

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {
                    "name": SERVER_NAME,
                    "version": SERVER_VERSION,
                },
                "instructions": (
                    "COLLIDER is a truth-bounded Semantic CI server. "
                    "Do not narrate PRESEEDED evidence as LIVE_BOB."
                ),
            },
        }

    if method == "ping":
        return {"jsonrpc": "2.0", "id": request_id, "result": {}}

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"tools": TOOLS},
        }

    if method == "tools/call":
        params = message.get("params") or {}
        name = params.get("name", "")
        arguments = params.get("arguments") or {}
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": call_tool(name, arguments),
        }

    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": -32601,
            "message": f"Method not found: {method}",
        },
    }


def serve() -> None:
    for raw in sys.stdin:
        line = raw.strip()
        if not line:
            continue

        try:
            message = json.loads(line)
            response = handle_request(message)
        except Exception as exc:  # final protocol boundary
            response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {exc}",
                },
            }

        if response is not None:
            sys.stdout.write(json.dumps(response, separators=(",", ":")) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    serve()
