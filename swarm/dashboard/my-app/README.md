# OpenClaw Mission Control Dashboard

A modern, real-time mission control dashboard for the Ralph Swarm AI agent system.

## Features

- **Real-time Monitoring**: Live feed of agent activities, tasks, and system events
- **Agent Management**: Visual overview of all 6 agents (Ralph, Scout, Max, Maya, Tracker, Watcher)
- **Task Queue**: Track pending, in-progress, and completed tasks
- **Channel Communication**: View messages across different output channels
- **Command Center**: Create new tasks directly from the dashboard
- **Swarm Status**: Monitor overall swarm health and coordination state

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Backend**: Convex (real-time database)
- **Styling**: Tailwind CSS v4
- **Animations**: Framer Motion
- **UI Components**: Custom ShadCN UI components
- **Icons**: Lucide React

## Getting Started

### Prerequisites

- Node.js 18+
- A Convex account and project

### Installation

1. Clone the repository:
```bash
git clone <repo-url>
cd dashboard/my-app
```

2. Install dependencies:
```bash
npm install
```

3. Set up Convex:
```bash
npx convex dev
```

4. Copy environment variables:
```bash
cp .env.example .env.local
```

5. Update `.env.local` with your Convex URL.

6. Run the development server:
```bash
npm run dev
```

7. Open [http://localhost:3000](http://localhost:3000)

### Building for Production

```bash
npm run build
```

The static export will be in the `dist` folder.

## Architecture

### Components

- `Header`: Navigation and connection status
- `StatsOverview`: Key metrics cards
- `AgentGrid`: Agent status and activity
- `LiveFeed`: Real-time activity stream
- `TaskQueue`: Task management view
- `TaskCreator`: Command input for new tasks
- `ChannelView`: Channel message viewer
- `SwarmStatus`: Overall swarm coordination state

### Data Model

See `convex/schema.ts` for the complete data model including:
- Agents
- Tasks
- Activities
- Channels
- Messages
- Metrics

### Integration with OpenClaw

The dashboard can be integrated with the existing OpenClaw Python backend by:

1. Creating API endpoints in the Python backend
2. Using Convex actions to sync data
3. WebSocket connections for real-time updates

## Customization

### Themes

The dashboard uses CSS variables for theming. Edit `app/globals.css` to customize:

```css
.dark {
  --background: oklch(0.08 0.02 264);
  --foreground: oklch(0.985 0 0);
  /* ... */
}
```

### Adding New Agents

Update `types/index.ts`:

```typescript
export const AGENT_CONFIG = {
  // ... existing agents
  newagent: { name: "NewAgent", role: "custom", emoji: "🚀", color: "#ff0000" },
};
```

## License

MIT
