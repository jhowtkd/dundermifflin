export interface Agent {
  id: string;
  name: string;
  slug: string;
  role: string;
  status: "idle" | "working" | "error" | "offline";
  emoji: string;
  color: string;
  lastActive: string;
  tasksCompleted: number;
  currentTask?: string;
  progress: number;
}

export interface Task {
  id: string;
  title: string;
  description: string;
  status: "pending" | "running" | "completed" | "failed";
  agentId?: string;
  agentName?: string;
  project?: string;
  priority: "low" | "medium" | "high";
  createdAt: string;
  updatedAt: string;
  completedAt?: string;
  cost?: number;
  tokens?: number;
  duration?: number;
}

export interface CostEntry {
  agent: string;
  model: string;
  timestamp: string;
  tokensIn: number;
  tokensOut: number;
  costUsd: number;
  durationMs: number;
  success: boolean;
  error: string | null;
}

export interface Channel {
  id: string;
  name: string;
  description?: string;
  messageCount: number;
  lastMessageAt?: string;
}

export interface Message {
  id: string;
  channelId: string;
  authorId: string;
  authorName?: string;
  content: string;
  createdAt: string;
}

export interface ActivityLog {
  id: string;
  timestamp: string;
  agent: string;
  action: string;
  channel?: string;
  metadata?: Record<string, unknown>;
}

export interface SystemStats {
  totalTasks: number;
  completedTasks: number;
  failedTasks: number;
  totalCost: number;
  totalTokens: number;
  activeAgents: number;
  avgResponseTime: number;
}

export interface Project {
  id: string;
  name: string;
  path: string;
  description?: string;
  status: "active" | "archived" | "paused";
  createdAt: string;
  lastActivity?: string;
}
