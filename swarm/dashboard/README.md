# OpenClaw Mission Control Dashboard

A real-time mission control dashboard for monitoring and controlling autonomous AI agents running on OpenClaw.

## Features

- **Real-time Monitoring**: Live activity feed with Convex real-time backend
- **Agent Status**: Visual status of all agents (Ralph, Scout, Max, Maya, Tracker, Watcher)
- **Task Management**: Create, track and manage agent tasks
- **Cost Tracking**: Detailed cost analytics by agent and model
- **Modern UI**: Dark theme with Tailwind CSS v4 and Framer Motion animations

## Tech Stack

- **Frontend**: Next.js 15 (App Router) + TypeScript
- **Backend**: Convex (real-time)
- **Styling**: Tailwind CSS v4 + ShadCN UI
- **Animations**: Framer Motion
- **Icons**: Lucide React

## Quick Start

### 1. Install Dependencies

```bash
cd dashboard
npm install
```

### 2. Setup Convex

```bash
# Initialize Convex project
npx convex dev

# This will:
# - Create a Convex project
# - Generate the Convex URL
# - Deploy the schema
```

### 3. Environment Variables

Create `.env.local`:

```env
NEXT_PUBLIC_CONVEX_URL=your_convex_url_here
```

### 4. Seed Data

```bash
# Run Convex seed mutations to populate initial data
npx convex run agents:seed
npx convex run messages:seedChannels
```

### 5. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Project Structure

```
dashboard/
├── app/
│   ├── api/
│   │   └── sync/         # API route for Python backend sync
│   ├── globals.css       # Tailwind CSS v4 config
│   ├── layout.tsx        # Root layout with Convex provider
│   └── page.tsx          # Main dashboard page
├── components/
│   ├── ui/               # ShadCN UI components
│   ├── agent-card.tsx    # Agent status card
│   ├── activity-feed.tsx # Live activity feed
│   ├── cost-chart.tsx    # Cost analytics chart
│   ├── header.tsx        # Dashboard header
│   ├── stats-card.tsx    # Statistics cards
│   ├── task-creator.tsx  # New task form
│   └── task-list.tsx     # Task list component
├── convex/
│   ├── agents.ts         # Agent mutations/queries
│   ├── costs.ts          # Cost tracking
│   ├── messages.ts       # Channel messages
│   ├── schema.ts         # Convex schema
│   ├── stats.ts          # Dashboard stats aggregation
│   └── tasks.ts          # Task management
├── lib/
│   └── utils.ts          # Utility functions
└── types/
    └── index.ts          # TypeScript types
```

## Integration with OpenClaw Backend

To sync data from the Python backend:

```python
import requests

# Send cost log
requests.post("http://localhost:3000/api/sync", json={
    "type": "cost_log",
    "data": {
        "agent": "ralph",
        "model": "kimi-k2",
        "tokens_in": 1000,
        "tokens_out": 500,
        "cost_usd": 0.01,
        "duration_ms": 1500,
        "success": True
    }
})
```

## Deployment

### Deploy to Vercel

```bash
npm i -g vercel
vercel --prod
```

### Deploy Convex Functions

```bash
npx convex deploy
```

## Environment Variables for Production

```env
NEXT_PUBLIC_CONVEX_URL=https://your-project.convex.cloud
```

## License

MIT
