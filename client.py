"""
Raft Distributed Consensus State Machine Skill Client
Pure Python Standard Library implementation of Raft Consensus (Ongaro & Ousterhout).
Provides leader election, term handling, log entry replication, and commit index updates
for decentralized multi-agent coordination without external infrastructure.
"""

from typing import List, Dict, Any, Tuple, Optional
import time
import uuid


class LogEntry:
    def __init__(self, term: int, index: int, command: str, payload: Any):
        self.term = term
        self.index = index
        self.command = command
        self.payload = payload

    def to_dict(self) -> Dict[str, Any]:
        return {
            "term": self.term,
            "index": self.index,
            "command": self.command,
            "payload": self.payload
        }


class RaftNode:
    def __init__(self, node_id: str, peers: List[str]):
        self.node_id = node_id
        self.peers = peers
        self.current_term = 0
        self.voted_for: Optional[str] = None
        self.log: List[LogEntry] = []
        self.commit_index = 0
        self.last_applied = 0
        self.role = "Follower"  # Follower, Candidate, Leader
        self.state_machine: Dict[str, Any] = {}
        self.next_index: Dict[str, int] = {}
        self.match_index: Dict[str, int] = {}

    def request_vote(self, term: int, candidate_id: str, last_log_index: int, last_log_term: int) -> Tuple[int, bool]:
        if term > self.current_term:
            self.current_term = term
            self.role = "Follower"
            self.voted_for = None

        my_last_term = self.log[-1].term if self.log else 0
        my_last_index = len(self.log)

        log_ok = (last_log_term > my_last_term) or (last_log_term == my_last_term and last_log_index >= my_last_index)

        vote_granted = False
        if term == self.current_term and (self.voted_for is None or self.voted_for == candidate_id) and log_ok:
            self.voted_for = candidate_id
            vote_granted = True

        return self.current_term, vote_granted

    def append_entries(self, term: int, leader_id: str, prev_log_index: int, prev_log_term: int,
                       entries: List[Dict[str, Any]], leader_commit: int) -> Tuple[int, bool]:
        if term < self.current_term:
            return self.current_term, False

        if term > self.current_term:
            self.current_term = term
            self.role = "Follower"
            self.voted_for = None

        self.role = "Follower"

        if prev_log_index > 0:
            if len(self.log) < prev_log_index:
                return self.current_term, False
            if self.log[prev_log_index - 1].term != prev_log_term:
                return self.current_term, False

        # Overwrite conflicting entries
        insert_idx = prev_log_index
        for e in entries:
            entry_obj = LogEntry(e["term"], e["index"], e["command"], e["payload"])
            if insert_idx < len(self.log):
                self.log[insert_idx] = entry_obj
            else:
                self.log.append(entry_obj)
            insert_idx += 1

        if leader_commit > self.commit_index:
            self.commit_index = min(leader_commit, len(self.log))
            self._apply_entries()

        return self.current_term, True

    def _apply_entries(self):
        while self.last_applied < self.commit_index:
            self.last_applied += 1
            entry = self.log[self.last_applied - 1]
            if entry.command == "SET" and isinstance(entry.payload, dict):
                for k, v in entry.payload.items():
                    self.state_machine[k] = v


class RaftCluster:
    def __init__(self, node_ids: List[str]):
        self.node_ids = node_ids
        self.nodes: Dict[str, RaftNode] = {}
        for nid in node_ids:
            peers = [p for p in node_ids if p != nid]
            self.nodes[nid] = RaftNode(nid, peers)
        self.leader_id: Optional[str] = None

    def start_election(self, candidate_id: str) -> bool:
        candidate = self.nodes[candidate_id]
        candidate.role = "Candidate"
        candidate.current_term += 1
        candidate.voted_for = candidate_id
        votes = 1

        last_log_index = len(candidate.log)
        last_log_term = candidate.log[-1].term if candidate.log else 0

        for peer_id in candidate.peers:
            peer = self.nodes[peer_id]
            _, granted = peer.request_vote(candidate.current_term, candidate_id, last_log_index, last_log_term)
            if granted:
                votes += 1

        majority = (len(self.node_ids) // 2) + 1
        if votes >= majority:
            candidate.role = "Leader"
            self.leader_id = candidate_id
            for p in candidate.peers:
                candidate.next_index[p] = len(candidate.log) + 1
                candidate.match_index[p] = 0
            return True
        else:
            candidate.role = "Follower"
            return False

    def propose(self, command: str, payload: Any) -> bool:
        if not self.leader_id:
            return False
        leader = self.nodes[self.leader_id]
        new_index = len(leader.log) + 1
        entry = LogEntry(leader.current_term, new_index, command, payload)
        leader.log.append(entry)

        success_count = 1
        for peer_id in leader.peers:
            peer = self.nodes[peer_id]
            prev_idx = len(leader.log) - 1
            prev_term = leader.log[prev_idx - 1].term if prev_idx > 0 else 0
            entries_to_send = [entry.to_dict()]
            _, ok = peer.append_entries(leader.current_term, leader.node_id, prev_idx, prev_term, entries_to_send, leader.commit_index)
            if ok:
                success_count += 1

        majority = (len(self.node_ids) // 2) + 1
        if success_count >= majority:
            leader.commit_index = new_index
            leader._apply_entries()
            for peer_id in leader.peers:
                peer = self.nodes[peer_id]
                peer.append_entries(leader.current_term, leader.node_id, new_index, entry.term, [], leader.commit_index)
            return True
        return False
