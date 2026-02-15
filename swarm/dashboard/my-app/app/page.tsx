"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Header } from "@/components/dashboard/Header";
import { StatsOverview } from "@/components/dashboard/StatsOverview";
import { AgentGrid } from "@/components/dashboard/AgentGrid";
import { LiveFeed } from "@/components/dashboard/LiveFeed";
import { TaskQueue } from "@/components/dashboard/TaskQueue";
import { TaskCreator } from "@/components/dashboard/TaskCreator";
import { ChannelView } from "@/components/dashboard/ChannelView";
import { SwarmStatus } from "@/components/dashboard/SwarmStatus";
import { Agent, Task, Activity, Channel, Message, SwarmState, Metrics } from "@/types";

// Mock data for demonstration
const mockAgents: Agent[] = [
  { id: "1", slug: "ralph", name: "Ralph", role: "coordinate", emoji: "🎩", status: "idle", lastHeartbeat: Date.now(), tasksCompleted: 42, tasksFailed: 2 },
  { id: "2", slug: "scout", name: "Scout", role: "find", emoji: "🔍", status: "idle", lastHeartbeat: Date.now(), tasksCompleted: 38, tasksFailed: 1 },
  { id: "3", slug: "max", name: "Max", role: "build", emoji: "🛠️", status: "working", currentTask: "Building landing page", lastHeartbeat: Date.now(), tasksCompleted: 56, tasksFailed: 3 },
  { id: "4", slug: "maya", name: "Maya", role: "create", emoji: "✍️", status: "idle", lastHeartbeat: Date.now(), tasksCompleted: 45, tasksFailed: 0 },
  { id: "5", slug: "tracker", name: "Tracker", role: "track", emoji: "📊", status: "idle", lastHeartbeat: Date.now(), tasksCompleted: 29, tasksFailed: 1 },
  { id: "6", slug: "watcher", name: "Watcher", role: "watch", emoji: "👁️", status: "offline", lastHeartbeat: Date.now() - 3600000, tasksCompleted: 23, tasksFailed: 0 },
];

const mockTasks: Task[] = [
  { id: "1", code: "TSK-001", description: "Research AI competitors in the market", status: "completed", priority: "high", assignedAgent: "scout", createdAt: Date.now() - 3600000, completedAt: Date.now() - 1800000, complexity: "medium", agentsRequired: ["scout"] },
  { id: "2", code: "TSK-002", description: "Build comparison landing page", status: "in_progress", priority: "high", assignedAgent: "max", createdAt: Date.now() - 1800000, startedAt: Date.now() - 1200000, complexity: "complex", agentsRequired: ["max", "maya"] },
  { id: "3", code: "TSK-003", description: "Write marketing copy for landing page", status: "pending", priority: "medium", createdAt: Date.now() - 900000, complexity: "simple", agentsRequired: ["maya"] },
  { id: "4", code: "TSK-004", description: "Set up analytics tracking", status: "pending", priority: "low", createdAt: Date.now() - 300000, complexity: "simple", agentsRequired: ["tracker"] },
];

const mockActivities: Activity[] = [
  { id: "1", type: "task_completed", agentSlug: "scout", taskId: "1", message: "Completed research on AI competitors", timestamp: Date.now() - 1800000 },
  { id: "2", type: "task_started", agentSlug: "max", taskId: "2", message: "Started building landing page", timestamp: Date.now() - 1200000 },
  { id: "3", type: "task_created", message: "New task created: Write marketing copy", timestamp: Date.now() - 900000 },
  { id: "4", type: "agent_message", agentSlug: "ralph", message: "Coordinating next steps for the mission", timestamp: Date.now() - 600000 },
  { id: "5", type: "system_event", message: "Swarm initialized successfully", timestamp: Date.now() - 300000 },
];

const mockChannels: Channel[] = [
  { id: "1", name: "orders", description: "Main command channel", messageCount: 156, lastActivity: Date.now(), isActive: true },
  { id: "2", name: "find-output", description: "Research findings", messageCount: 89, lastActivity: Date.now() - 1800000, isActive: true },
  { id: "3", name: "build-output", description: "Code & technical output", messageCount: 124, lastActivity: Date.now() - 300000, isActive: true },
  { id: "4", name: "create-output", description: "Copy & content output", messageCount: 67, lastActivity: Date.now() - 3600000, isActive: true },
];

const mockMessages: Message[] = [
  { id: "1", channelId: "1", authorId: "ralph", content: "Starting new mission: Build AI competitor analysis landing page", timestamp: Date.now() - 3600000, isSystem: false },
  { id: "2", channelId: "1", authorId: "scout", content: "On it! Researching top 5 AI competitors in the space.", timestamp: Date.now() - 3500000, isSystem: false },
  { id: "3", channelId: "1", authorId: "scout", content: "Research complete. Found key differentiators for our positioning.", timestamp: Date.now() - 1800000, isSystem: false },
  { id: "4", channelId: "1", authorId: "max", content: "Starting build now. Will use Next.js with Tailwind.", timestamp: Date.now() - 1200000, isSystem: false },
  { id: "5", channelId: "2", authorId: "scout", content: "Competitor A: Strong in enterprise, weak in UX\nCompetitor B: Great UX, limited features\nCompetitor C: Expensive, good support", timestamp: Date.now() - 1800000, isSystem: false },
];

const mockSwarmState: SwarmState = {
  id: "1",
  isActive: true,
  currentMission: "Build AI competitor analysis landing page",
  leadAgent: "ralph",
  participatingAgents: ["scout", "max", "maya"],
  startedAt: Date.now() - 3600000,
  lastUpdate: Date.now(),
};

const mockStats = {
  total: 4,
  pending: 2,
  inProgress: 1,
  completed: 1,
  failed: 0,
};

export default function Dashboard() {
  const [isConnected, setIsConnected] = useState(true);
  const [selectedChannel, setSelectedChannel] = useState("1");
  const [activities, setActivities] = useState(mockActivities);

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      // Add random activity
      if (Math.random() > 0.7) {
        const newActivity: Activity = {
          id: Date.now().toString(),
          type: Math.random() > 0.5 ? "agent_message" : "system_event",
          agentSlug: ["ralph", "scout", "max", "maya"][Math.floor(Math.random() * 4)],
          message: ["Processing...", "Analyzing data...", "Optimizing...", "Task complete!"][Math.floor(Math.random() * 4)],
          timestamp: Date.now(),
        };
        setActivities((prev) => [newActivity, ...prev].slice(0, 20));
      }
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const handleCreateTask = async (task: string) => {
    // Simulate task creation
    await new Promise((resolve) => setTimeout(resolve, 1000));
    
    const newActivity: Activity = {
      id: Date.now().toString(),
      type: "task_created",
      message: `New task created: ${task}`,
      timestamp: Date.now(),
    };
    setActivities((prev) => [newActivity, ...prev]);
  };

  return (
    <div className="min-h-screen bg-background">
      <Header isConnected={isConnected} />
      
      <main className="container py-6 space-y-6">
        {/* Command Center */}
        <TaskCreator onCreateTask={handleCreateTask} />

        {/* Stats Overview */}
        <StatsOverview stats={mockStats} todayTasks={mockTasks.length} />

        {/* Main Grid */}
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Agent Grid */}
          <AgentGrid agents={mockAgents} />

          {/* Live Feed */}
          <LiveFeed activities={activities} />
        </div>

        {/* Second Row */}
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Task Queue */}
          <div className="lg:col-span-2">
            <TaskQueue tasks={mockTasks} />
          </div>

          {/* Swarm Status */}
          <SwarmStatus swarmState={mockSwarmState} agents={mockAgents} />
        </div>

        {/* Channel View */}
        <ChannelView
          channels={mockChannels}
          messages={mockMessages}
          selectedChannel={selectedChannel}
          onSelectChannel={setSelectedChannel}
        />
      </main>

      {/* Footer */}
      <footer className="border-t py-6 mt-12">
        <div className="container flex items-center justify-between text-sm text-muted-foreground">
          <p>OpenClaw Mission Control v5.0</p>
          <p>Running on Mac Mini M4</p>
        </div>
      </footer>
    </div>
  );
}
