#!/usr/bin/env python3
"""
OpenClaw Dashboard Integration Client

This module provides integration with the Mission Control Dashboard.
Add this to your Ralph Swarm Python backend to send updates to the dashboard.
"""

import os
import requests
import json
from typing import Optional, List, Dict, Any
from datetime import datetime


class DashboardClient:
    """Client for sending updates to the OpenClaw Mission Control Dashboard."""
    
    def __init__(self, webhook_url: Optional[str] = None):
        """
        Initialize dashboard client.
        
        Args:
            webhook_url: Convex webhook URL. If not provided, reads from CONVEX_WEBHOOK_URL env var.
        """
        self.webhook_url = webhook_url or os.getenv("CONVEX_WEBHOOK_URL")
        self.enabled = os.getenv("DASHBOARD_ENABLED", "true").lower() == "true"
        
        if not self.webhook_url and self.enabled:
            print("⚠️  Dashboard webhook URL not set. Set CONVEX_WEBHOOK_URL env var.")
    
    def _post(self, endpoint: str, data: Dict[str, Any]) -> bool:
        """Send POST request to webhook endpoint."""
        if not self.enabled or not self.webhook_url:
            return False
        
        try:
            url = f"{self.webhook_url}/webhook/{endpoint}"
            response = requests.post(url, json=data, timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"⚠️  Dashboard update failed: {e}")
            return False
    
    def update_agent_status(
        self, 
        slug: str, 
        status: str, 
        current_task: Optional[str] = None
    ) -> bool:
        """
        Update agent status in dashboard.
        
        Args:
            slug: Agent slug (e.g., "scout", "max", "maya")
            status: One of "idle", "working", "offline"
            current_task: Optional description of current task
        """
        return self._post("agent-status", {
            "slug": slug,
            "status": status,
            "currentTask": current_task
        })
    
    def create_task(
        self,
        code: str,
        description: str,
        priority: str = "medium",
        complexity: str = "medium",
        agents_required: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Create a new task in dashboard.
        
        Args:
            code: Task code (e.g., "TSK-001")
            description: Task description
            priority: "low", "medium", or "high"
            complexity: "simple", "medium", or "complex"
            agents_required: List of agent slugs required for this task
            
        Returns:
            Task ID if successful, None otherwise
        """
        if not self.enabled or not self.webhook_url:
            return None
        
        try:
            url = f"{self.webhook_url}/webhook/task"
            response = requests.post(url, json={
                "code": code,
                "description": description,
                "priority": priority,
                "complexity": complexity,
                "agentsRequired": agents_required or []
            }, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("taskId")
            return None
        except Exception as e:
            print(f"⚠️  Dashboard task creation failed: {e}")
            return None
    
    def log_activity(
        self,
        message: str,
        agent_slug: Optional[str] = None,
        task_id: Optional[str] = None,
        activity_type: str = "system_event",
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Log activity to dashboard live feed.
        
        Args:
            message: Activity message
            agent_slug: Optional agent slug
            task_id: Optional task ID
            activity_type: One of:
                - "task_created"
                - "task_started"
                - "task_completed"
                - "task_failed"
                - "agent_assigned"
                - "agent_message"
                - "system_event"
            metadata: Optional additional data
        """
        return self._post("activity", {
            "type": activity_type,
            "agentSlug": agent_slug,
            "taskId": task_id,
            "message": message,
            "metadata": metadata or {}
        })
    
    def agent_heartbeat(self, slug: str) -> bool:
        """Send agent heartbeat to mark as online."""
        return self.update_agent_status(slug, "idle")


# Global instance for easy import
dashboard = DashboardClient()


# Convenience functions for common operations

def agent_start_task(slug: str, task_description: str):
    """Mark agent as working on a task."""
    return dashboard.update_agent_status(slug, "working", task_description)


def agent_finish_task(slug: str):
    """Mark agent as idle after completing a task."""
    return dashboard.update_agent_status(slug, "idle")


def agent_go_offline(slug: str):
    """Mark agent as offline."""
    return dashboard.update_agent_status(slug, "offline")


def log_task_created(code: str, description: str, agents: List[str] = None):
    """Log task creation."""
    dashboard.create_task(code, description, agents_required=agents)
    dashboard.log_activity(
        f"Task created: {description}",
        activity_type="task_created"
    )


def log_task_completed(agent_slug: str, task_description: str):
    """Log task completion."""
    dashboard.log_activity(
        f"Completed: {task_description}",
        agent_slug=agent_slug,
        activity_type="task_completed"
    )
    dashboard.update_agent_status(agent_slug, "idle")


def log_task_failed(agent_slug: str, task_description: str, error: str = None):
    """Log task failure."""
    msg = f"Failed: {task_description}"
    if error:
        msg += f" - {error}"
    
    dashboard.log_activity(
        msg,
        agent_slug=agent_slug,
        activity_type="task_failed"
    )
    dashboard.update_agent_status(agent_slug, "idle")


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = DashboardClient()
    
    # Example: Scout starts research
    client.update_agent_status("scout", "working", "Researching competitors")
    client.log_activity("Starting competitor research", "scout", activity_type="task_started")
    
    # Example: Task completed
    client.update_agent_status("scout", "idle")
    client.log_activity("Research complete!", "scout", activity_type="task_completed")
