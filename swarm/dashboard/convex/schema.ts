import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  agents: defineTable({
    name: v.string(),
    slug: v.string(),
    role: v.string(),
    status: v.union(v.literal("idle"), v.literal("working"), v.literal("error"), v.literal("offline")),
    emoji: v.string(),
    color: v.string(),
    lastActive: v.string(),
    tasksCompleted: v.number(),
    currentTask: v.optional(v.string()),
    progress: v.number(),
  })
    .index("by_slug", ["slug"])
    .index("by_status", ["status"]),

  tasks: defineTable({
    title: v.string(),
    description: v.string(),
    status: v.union(v.literal("pending"), v.literal("running"), v.literal("completed"), v.literal("failed")),
    agentId: v.optional(v.id("agents")),
    project: v.optional(v.string()),
    priority: v.union(v.literal("low"), v.literal("medium"), v.literal("high")),
    createdAt: v.string(),
    updatedAt: v.string(),
    completedAt: v.optional(v.string()),
    cost: v.optional(v.number()),
    tokens: v.optional(v.number()),
    duration: v.optional(v.number()),
  })
    .index("by_status", ["status"])
    .index("by_agent", ["agentId"])
    .index("by_created", ["createdAt"]),

  costLogs: defineTable({
    agent: v.string(),
    model: v.string(),
    timestamp: v.string(),
    tokensIn: v.number(),
    tokensOut: v.number(),
    costUsd: v.number(),
    durationMs: v.number(),
    success: v.boolean(),
    error: v.optional(v.string()),
  })
    .index("by_agent", ["agent"])
    .index("by_timestamp", ["timestamp"]),

  channels: defineTable({
    name: v.string(),
    description: v.optional(v.string()),
    messageCount: v.number(),
    lastMessageAt: v.optional(v.string()),
  })
    .index("by_name", ["name"]),

  messages: defineTable({
    channelId: v.id("channels"),
    authorId: v.string(),
    authorName: v.optional(v.string()),
    content: v.string(),
    createdAt: v.string(),
  })
    .index("by_channel", ["channelId", "createdAt"])
    .index("by_author", ["authorId"]),

  activityLogs: defineTable({
    timestamp: v.string(),
    agent: v.string(),
    action: v.string(),
    channel: v.optional(v.string()),
    metadata: v.optional(v.record(v.any())),
  })
    .index("by_timestamp", ["timestamp"])
    .index("by_agent", ["agent"]),

  projects: defineTable({
    name: v.string(),
    path: v.string(),
    description: v.optional(v.string()),
    status: v.union(v.literal("active"), v.literal("archived"), v.literal("paused")),
    createdAt: v.string(),
    lastActivity: v.optional(v.string()),
  })
    .index("by_status", ["status"])
    .index("by_path", ["path"]),
});
