# OpenClaw Dashboard Integration Guide

This guide explains how to integrate the Mission Control Dashboard with your existing OpenClaw Python backend.

## Overview

The dashboard uses **Convex** as its real-time backend. To connect your Python agents to the dashboard, you have two options:

1. **Webhook Integration** (Recommended) - Push updates from Python to Convex
2. **API Polling** - Python backend exposes REST API, dashboard polls for updates

## Option 1: Webhook Integration

### Setup

1. Deploy your Convex project:
```bash
cd dashboard/my-app
npx convex deploy
```

2. Get your Convex HTTP URL from the Convex dashboard.

3. Configure your Python backend to send webhooks:

```python
import requests
import os

CONVEX_WEBHOOK_URL = os.getenv("CONVEX_WEBHOOK_URL", "https://your-deployment.convex.site")

class DashboardClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    def update_agent_status(self, slug: str, status: str, current_task: str = None):
        """Update agent status in dashboard"""
        requests.post(
            f"{self.base_url}/webhook/agent-status",
            json={
                "slug": slug,
                "status": status,  # "idle", "working", "offline"
                "currentTask": current_task
            }
        )
    
    def create_task(self, code: str, description: str, priority: str = "medium", 
                    complexity: str = "medium", agents_required: list = None):
        """Create a new task in dashboard"""
        response = requests.post(
            f"{self.base_url}/webhook/task",
            json={
                "code": code,
                "description": description,
                "priority": priority,
                "complexity": complexity,
                "agentsRequired": agents_required or []
            }
        )
        return response.json().get("taskId")
    
    def log_activity(self, message: str, agent_slug: str = None, 
                     task_id: str = None, activity_type: str = "system_event",
                     metadata: dict = None):
        """Log activity to dashboard"""
        requests.post(
            f"{self.base_url}/webhook/activity",
            json={
                "type": activity_type,
                "agentSlug": agent_slug,
                "taskId": task_id,
                "message": message,
                "metadata": metadata or {}
            }
        )

# Usage in your agent code:
dashboard = DashboardClient(CONVEX_WEBHOOK_URL)

# When agent starts working
dashboard.update_agent_status("max", "working", "Building landing page")

# When task is created
dashboard.create_task(
    code="TSK-001",
    description="Research competitors",
    priority="high",
    agents_required=["scout"]
)

# Log activity
dashboard.log_activity(
    message="Research completed",
    agent_slug="scout",
    activity_type="task_completed"
)
```

## Option 2: API Polling

If you prefer to keep the Python backend as the source of truth:

1. Create a REST API in your Python backend (using Flask/FastAPI)
2. Update the dashboard to poll your API instead of using Convex

See `lib/openclaw-api.ts` for a sample implementation.

## Environment Variables

Add to your Python `.env`:
```
CONVEX_WEBHOOK_URL=https://your-deployment.convex.site
DASHBOARD_ENABLED=true
```

Add to your dashboard `.env.local`:
```
NEXT_PUBLIC_CONVEX_URL=https://your-convex-url.convex.cloud
```

## Data Flow

```
Python Agents → Webhooks → Convex → Dashboard (Real-time)
     ↓
  SQLite DB (local persistence)
```

## Convex Schema

The dashboard uses the following tables:

- **agents**: Agent status and metadata
- **tasks**: Task queue and progress
- **activities**: Activity log / live feed
- **channels**: Communication channels
- **messages**: Channel messages
- **metrics**: Daily usage metrics

## Customization

### Adding New Agent Types

1. Update `types/index.ts`:
```typescript
export const AGENT_CONFIG = {
  // ... existing agents
  custom: { name: "Custom", role: "custom", emoji: "🚀", color: "#ff0000" },
};
```

2. Initialize in Convex:
```typescript
// convex/agents.ts
await ctx.db.insert("agents", {
  slug: "custom",
  name: "Custom",
  role: "custom",
  emoji: "🚀",
  status: "idle",
  lastHeartbeat: Date.now(),
  tasksCompleted: 0,
  tasksFailed: 0,
});
```

### Custom Metrics

Add custom metrics tracking in `convex/metrics.ts`:

```typescript
export const trackCustomMetric = mutation({
  args: { name: v.string(), value: v.number() },
  handler: async (ctx, { name, value }) => {
    // Store custom metric
  },
});
```

## Troubleshooting

### Dashboard not updating

1. Check Convex connection: `npx convex dashboard`
2. Verify webhook URL is correct
3. Check Python logs for webhook errors

### Agents showing offline

Agents send heartbeats every 30 seconds. If no heartbeat is received for 5 minutes, the agent is marked offline.

### CORS errors

If using webhooks from localhost, ensure your Convex deployment allows CORS from your Python backend URL.

## Deployment

### Deploy Dashboard

```bash
cd dashboard/my-app
npm run build
# Upload dist/ folder to your hosting provider (Vercel, Netlify, etc.)
```

Or use Vercel:
```bash
npx vercel --prod
```

### Deploy Convex

```bash
npx convex deploy
```

## Support

For issues or questions, check:
- Convex docs: https://docs.convex.dev
- Next.js docs: https://nextjs.org/docs
