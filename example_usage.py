"""Example usage for Raft Consensus Skill."""
from client import RaftNode

def main():
    print("Executing Raft Consensus Protocol...")
    node = RaftNode("agent_leader", ["agent_peer_1", "agent_peer_2"])
    success = node.start_election()
    print("Election result:", success, "Current Role:", node.state)
    assert success and node.state == RaftNode.LEADER

    appended = node.append_entry({"task": "DISPATCH_MISSION", "priority": 1})
    print("Appended entry:", appended)
    assert appended and len(node.log) == 1
    print("Raft Consensus verified successfully!")

if __name__ == "__main__":
    main()
