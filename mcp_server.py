"""MCP Server for Raft Consensus Skill."""
import json
import sys
from client import RaftNode

def main():
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
            req_id = req.get("id")
            method = req.get("method")
            params = req.get("params", {})

            if method == "tools/list":
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "tools": [{
                            "name": "propose_raft_entry",
                            "description": "Propose command to Raft consensus cluster",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "node_id": {"type": "string"},
                                    "peers": {"type": "array", "items": {"type": "string"}},
                                    "command": {}
                                },
                                "required": ["node_id", "peers", "command"]
                            }
                        }]
                    }
                }
            elif method == "tools/call":
                args = params.get("arguments", {})
                node = RaftNode(args["node_id"], args["peers"])
                node.start_election()
                node.append_entry(args["command"])
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(node.get_status())}]}
                }
            else:
                res = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}
            print(json.dumps(res), flush=True)
        except Exception as e:
            err = {"jsonrpc": "2.0", "id": None, "error": {"code": -32000, "message": str(e)}}
            print(json.dumps(err), flush=True)

if __name__ == "__main__":
    main()
