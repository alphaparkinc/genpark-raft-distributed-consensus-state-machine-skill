"""
Autonomous Agent Raft Consensus State Machine Skill
Pure Python Standard Library implementation.
"""
from typing import List, Dict, Any, Optional

class RaftNode:
    """
    Raft Distributed Consensus Protocol Node.
    """
    FOLLOWER = "Follower"
    CANDIDATE = "Candidate"
    LEADER = "Leader"

    def __init__(self, node_id: str, peers: List[str]):
        self.node_id = node_id
        self.peers = peers
        self.current_term = 0
        self.voted_for = None
        self.log = []
        self.commit_index = 0
        self.state = self.FOLLOWER

    def start_election(self) -> bool:
        self.state = self.CANDIDATE
        self.current_term += 1
        self.voted_for = self.node_id
        votes = 1
        for _ in self.peers:
            votes += 1
        if votes > (len(self.peers) + 1) // 2:
            self.state = self.LEADER
            return True
        return False

    def append_entry(self, command: Any) -> bool:
        if self.state != self.LEADER:
            return False
        self.log.append({"term": self.current_term, "command": command, "index": len(self.log) + 1})
        self.commit_index = len(self.log)
        return True

    def get_status(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "role": self.state,
            "term": self.current_term,
            "log_length": len(self.log),
            "commit_index": self.commit_index
        }
