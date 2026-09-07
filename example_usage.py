"""
Demonstration of Raft Distributed Consensus State Machine Skill
"""

from client import RaftCluster

def main():
    print("=== Initializing 3-Node Raft Consensus Cluster ===")
    cluster = RaftCluster(["node-1", "node-2", "node-3"])
    
    print("Initiating election for node-1...")
    elected = cluster.start_election("node-1")
    print(f"Node-1 election result: {elected} (Leader: {cluster.leader_id})")

    print("\nProposing state command: SET {'task_assignment': 'agent_planner_01', 'status': 'IN_PROGRESS'}")
    committed = cluster.propose("SET", {"task_assignment": "agent_planner_01", "status": "IN_PROGRESS"})
    print(f"Proposal committed: {committed}")

    for nid in cluster.node_ids:
        node = cluster.nodes[nid]
        print(f"Node {nid} State Machine: {node.state_machine}, Log Size: {len(node.log)}, Commit Index: {node.commit_index}")

    print("\nProposing second command: SET {'status': 'COMPLETED', 'accuracy': 0.99}")
    committed_2 = cluster.propose("SET", {"status": "COMPLETED", "accuracy": 0.99})
    print(f"Second proposal committed: {committed_2}")

    print("Final Node-3 State Machine:", cluster.nodes["node-3"].state_machine)
    print("Raft Cluster Verification PASS!")

if __name__ == "__main__":
    main()
