import json
import subprocess
import sys

from collider.mcp_server import TOOLS, call_tool, handle_request


def _text_payload(result):
    return json.loads(result["content"][0]["text"])


def test_mcp_initialize_exposes_server_and_tools_capability():
    response = handle_request(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {},
        }
    )

    assert response["id"] == 1
    assert response["result"]["serverInfo"]["name"] == "collider-semantic-ci"
    assert "tools" in response["result"]["capabilities"]


def test_mcp_tools_list_exposes_native_collider_surface():
    response = handle_request(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {},
        }
    )

    names = {tool["name"] for tool in response["result"]["tools"]}
    assert {
        "collider_gate",
        "collider_pr_gate",
        "collider_decision_memory",
        "collider_validate_live_bob",
        "collider_export_decision_rule",
        "collider_evaluate_replay",
    } <= names
    assert len(TOOLS) >= 6


def test_mcp_notification_has_no_response():
    assert (
        handle_request(
            {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {},
            }
        )
        is None
    )


def test_mcp_unknown_method_returns_jsonrpc_error():
    response = handle_request(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "collider/does-not-exist",
        }
    )

    assert response["error"]["code"] == -32601


def test_mcp_reads_canonical_decision_memory():
    result = call_tool("collider_decision_memory")
    payload = _text_payload(result)

    assert payload["schema"] == "collider.decision-memory/v1"
    assert payload["decisions"][0]["concept"] == "customer_identity"
    assert payload["decisions"][0]["canonical_value"] == "account_id"


def test_mcp_rejects_path_escape():
    result = call_tool(
        "collider_decision_memory",
        {"path": "../outside.json"},
    )

    assert result["isError"] is True
    payload = _text_payload(result)
    assert payload["error"] == "ValueError"
    assert "escapes COLLIDER workspace" in payload["message"]


def test_mcp_stdio_process_roundtrip():
    messages = [
        {
            "jsonrpc": "2.0",
            "id": 11,
            "method": "initialize",
            "params": {},
        },
        {
            "jsonrpc": "2.0",
            "id": 12,
            "method": "tools/list",
            "params": {},
        },
    ]
    payload = "\n".join(json.dumps(message) for message in messages) + "\n"

    proc = subprocess.run(
        [sys.executable, "-m", "collider.mcp_server"],
        input=payload,
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert proc.returncode == 0, proc.stderr
    responses = [
        json.loads(line)
        for line in proc.stdout.splitlines()
        if line.strip()
    ]
    assert responses[0]["id"] == 11
    assert responses[0]["result"]["serverInfo"]["name"] == "collider-semantic-ci"
    assert responses[1]["id"] == 12
    names = {tool["name"] for tool in responses[1]["result"]["tools"]}
    assert "collider_pr_gate" in names
    assert "collider_validate_live_bob" in names
