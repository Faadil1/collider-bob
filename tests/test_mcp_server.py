import json

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
