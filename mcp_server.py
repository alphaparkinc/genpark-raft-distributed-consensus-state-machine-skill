"""
MCP Server for Raft Distributed Consensus State Machine Skill
"""

import json
import sys
from client import RaftCluster

cluster = RaftCluster(["agent-node-1", "agent-node-2", "agent-node-3"])
cluster.start_election("agent-node-1")

def handle_call(name: str, args: dict) -> dict:
    if name == "propose_state":
        cmd = args.get("command", "SET")
        payload = args.get("payload", {})
        committed = cluster.propose(cmd, payload)
        return {"committed": committed, "leader": cluster.leader_id, "state": cluster.nodes[cluster.leader_id].state_machine}
    elif name == "get_state":
        nid = args.get("node_id", cluster.leader_id)
        node = cluster.nodes.get(nid)
        if node:
            return {"node_id": nid, "role": node.role, "term": node.current_term, "commit_index": node.commit_index, "state": node.state_machine}
        return {"error": "Node not found"}
    return {"error": f"Unknown tool: {name}"}

def main():
    for line in sys.stdin:
        if not line.strip():
            continue
        req = json.loads(line)
        res = handle_call(req.get("method"), req.get("params", {}))
        sys.stdout.write(json.dumps(res) + "\n")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
