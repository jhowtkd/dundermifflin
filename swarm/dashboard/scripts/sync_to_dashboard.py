#!/usr/bin/env python3
"""
OpenClaw → Dashboard Sync Bridge

This script syncs data from the OpenClaw Python backend to the Next.js dashboard.
Run this alongside the main OpenClaw system to populate the dashboard.
"""

import json
import time
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

DASHBOARD_URL = "http://localhost:3000"
COST_LOG_FILE = Path(__file__).parent.parent.parent / "cost_log.jsonl"
TASK_STATE_FILE = Path(__file__).parent.parent.parent / "task_state.json"


class DashboardSync:
    def __init__(self, dashboard_url: str = DASHBOARD_URL):
        self.dashboard_url = dashboard_url
        self.last_cost_line = 0
        
    def sync_cost_log(self, entry: Dict) -> bool:
        """Sync a single cost log entry to the dashboard"""
        try:
            response = requests.post(
                f"{self.dashboard_url}/api/sync",
                json={
                    "type": "cost_log",
                    "data": entry
                },
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error syncing cost log: {e}")
            return False
    
    def sync_agent_status(self, agent: str, status: str, task: Optional[str] = None) -> bool:
        """Sync agent status to the dashboard"""
        try:
            response = requests.post(
                f"{self.dashboard_url}/api/sync",
                json={
                    "type": "agent_status",
                    "data": {
                        "agent": agent,
                        "status": status,
                        "task": task,
                        "timestamp": datetime.now().isoformat()
                    }
                },
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error syncing agent status: {e}")
            return False
    
    def poll_cost_logs(self):
        """Poll cost_log.jsonl for new entries"""
        if not COST_LOG_FILE.exists():
            return
        
        with open(COST_LOG_FILE, "r") as f:
            lines = f.readlines()
        
        # Process new lines only
        new_lines = lines[self.last_cost_line:]
        for line in new_lines:
            try:
                entry = json.loads(line.strip())
                if self.sync_cost_log(entry):
                    print(f"✓ Synced cost log: {entry['agent']} - ${entry['cost_usd']:.4f}")
                else:
                    print(f"✗ Failed to sync cost log")
            except json.JSONDecodeError:
                continue
        
        self.last_cost_line = len(lines)
    
    def run(self, interval: int = 5):
        """Run the sync loop"""
        print(f"🚀 Dashboard Sync started")
        print(f"   Dashboard URL: {self.dashboard_url}")
        print(f"   Watching: {COST_LOG_FILE}")
        print(f"   Press Ctrl+C to stop\n")
        
        try:
            while True:
                self.poll_cost_logs()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n👋 Sync stopped")


def quick_sync_cost_entry(agent: str, model: str, tokens_in: int, tokens_out: int,
                          cost_usd: float, duration_ms: int, success: bool = True,
                          error: Optional[str] = None):
    """Quick sync a single cost entry"""
    sync = DashboardSync()
    entry = {
        "agent": agent,
        "model": model,
        "timestamp": datetime.now().isoformat(),
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "cost_usd": cost_usd,
        "duration_ms": duration_ms,
        "success": success,
        "error": error
    }
    return sync.sync_cost_log(entry)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--watch":
        # Run continuous sync
        sync = DashboardSync()
        sync.run()
    else:
        # One-time sync test
        print("Testing dashboard connection...")
        try:
            response = requests.get(f"{DASHBOARD_URL}/api/sync")
            print(f"Dashboard response: {response.json()}")
        except Exception as e:
            print(f"Dashboard not available: {e}")
            print("\nTo start continuous sync, run:")
            print("  python sync_to_dashboard.py --watch")
