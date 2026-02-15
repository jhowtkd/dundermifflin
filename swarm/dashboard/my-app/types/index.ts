export interface Agent {
  id: string;
  slug: string;
  name: string;
  role: string;
  emoji: string;
  status: "idle" | "working" | "offline";
  currentTask?: string;
  lastHeartbeat: number;
  tasksCompleted: number;
  tasksFailed: number;
}

export interface Task {
  id: string;
  code: string;
  description: string;
  status: "pending" | "in_progress" | "completed" | "failed";
  priority: "low" | "medium" | "high";
  assignedAgent?: string;
  createdAt: number;
  startedAt?: number;
  completedAt?: number;
  complexity: "simple" | "medium" | "complex";
  agentsRequired: string[];
  parentTaskId?: string;
}

export interface Activity {
  id: string;
  type: 
    | "task_created"
    | "task_started"
    | "task_completed"
    | "task_failed"
    | "agent_assigned"
    | "agent_message"
    | "system_event";
  agentSlug?: string;
  taskId?: string;
  message: string;
  metadata?: Record<string, any>;
  timestamp: number;
}

export interface Channel {
  id: string;
  name: string;
  description: string;
  messageCount: number;
  lastActivity: number;
  isActive: boolean;
}

export interface Message {
  id: string;
  channelId: string;
  authorId: string;
  content: string;
  timestamp: number;
  isSystem: boolean;
}

export interface Metrics {
  id: string;
  date: string;
  tasksCreated: number;
  tasksCompleted: number;
  tasksFailed: number;
  tokensUsed: number;
  costUSD: number;
  activeAgents: number;
  avgResponseTime: number;
}

export interface SwarmState {
  id: string;
  isActive: boolean;
  currentMission?: string;
  leadAgent?: string;
  participatingAgents: string[];
  startedAt?: number;
  lastUpdate: number;
}

export type AgentRole = "find" | "build" | "create" | "track" | "watch" | "coordinate";

export const AGENT_CONFIG: Record<string, { name: string; role: AgentRole; emoji: string; color: string }> = {
  scout: { name: "Scout", role: "find", emoji: "🔍", color: "#3b82f6" },
  max: { name: "Max", role: "build", emoji: "🛠️", color: "#22c55e" },
  maya: { name: "Maya", role: "create", emoji: "✍️", color: "#a855f7" },
  tracker: { name: "Tracker", role: "track", emoji: "📊", color: "#f59e0b" },
  watcher: { name: "Watcher", role: "watch", emoji: "👁️", color: "#ef4444" },
  ralph: { name: "Ralph", role: "coordinate", emoji: "🎩", color: "#ec4899" },
};
