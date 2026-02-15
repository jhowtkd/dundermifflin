import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  // Agent status tracking
  agents: defineTable({
    slug: v.string(),
    name: v.string(),
    role: v.string(),
    emoji: v.string(),
    status: v.union(v.literal("idle"), v.literal("working"), v.literal("offline")),
    currentTask: v.optional(v.string()),
    lastHeartbeat: v.number(),
    tasksCompleted: v.number(),
    tasksFailed: v.number(),
  })
    .index("by_slug", ["slug"])
    .index("by_status", ["status"]),

  // Tasks
  tasks: defineTable({
    code: v.string(),
    description: v.string(),
    status: v.union(
      v.literal("pending"),
      v.literal("in_progress"),
      v.literal("completed"),
      v.literal("failed")
    ),
    priority: v.union(v.literal("low"), v.literal("medium"), v.literal("high")),
    assignedAgent: v.optional(v.string()),
    createdAt: v.number(),
    startedAt: v.optional(v.number()),
    completedAt: v.optional(v.number()),
    complexity: v.union(v.literal("simple"), v.literal("medium"), v.literal("complex")),
    agentsRequired: v.array(v.string()),
    parentTaskId: v.optional(v.id("tasks")),
  })
    .index("by_status", ["status"])
    .index("by_assigned_agent", ["assignedAgent"])
    .index("by_created_at", ["createdAt"]),

  // Live feed / Activity log
  activities: defineTable({
    type: v.union(
      v.literal("task_created"),
      v.literal("task_started"),
      v.literal("task_completed"),
      v.literal("task_failed"),
      v.literal("agent_assigned"),
      v.literal("agent_message"),
      v.literal("system_event")
    ),
    agentSlug: v.optional(v.string()),
    taskId: v.optional(v.id("tasks")),
    message: v.string(),
    metadata: v.optional(v.record(v.string(), v.any())),
    timestamp: v.number(),
  })
    .index("by_timestamp", ["timestamp"])
    .index("by_agent", ["agentSlug"])
    .index("by_task", ["taskId"]),

  // Channels
  channels: defineTable({
    name: v.string(),
    description: v.string(),
    messageCount: v.number(),
    lastActivity: v.number(),
    isActive: v.boolean(),
  }).index("by_name", ["name"]),

  // Channel messages
  messages: defineTable({
    channelId: v.id("channels"),
    authorId: v.string(),
    content: v.string(),
    timestamp: v.number(),
    isSystem: v.boolean(),
  })
    .index("by_channel", ["channelId"])
    .index("by_timestamp", ["timestamp"]),

  // System metrics
  metrics: defineTable({
    date: v.string(),
    tasksCreated: v.number(),
    tasksCompleted: v.number(),
    tasksFailed: v.number(),
    tokensUsed: v.number(),
    costUSD: v.number(),
    activeAgents: v.number(),
    avgResponseTime: v.number(),
  }).index("by_date", ["date"]),

  // Swarm coordination state
  swarmState: defineTable({
    isActive: v.boolean(),
    currentMission: v.optional(v.string()),
    leadAgent: v.optional(v.string()),
    participatingAgents: v.array(v.string()),
    startedAt: v.optional(v.number()),
    lastUpdate: v.number(),
  }),
});
