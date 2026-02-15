import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  agents: defineTable({
    name: v.string(),
    status: v.union(v.literal("online"), v.literal("busy"), v.literal("offline"), v.literal("error")),
    type: v.string(),
    lastSeen: v.number(),
    currentTask: v.optional(v.string()),
    metadata: v.optional(v.record(v.string(), v.any())),
  })
    .index("by_status", ["status"])
    .index("by_name", ["name"]),

  missions: defineTable({
    title: v.string(),
    description: v.string(),
    status: v.union(v.literal("pending"), v.literal("running"), v.literal("completed"), v.literal("failed")),
    priority: v.union(v.literal("low"), v.literal("medium"), v.literal("high"), v.literal("critical")),
    agentId: v.optional(v.id("agents")),
    steps: v.array(v.record(v.string(), v.any())),
    progress: v.number(),
    startedAt: v.optional(v.number()),
    completedAt: v.optional(v.number()),
    metadata: v.optional(v.record(v.string(), v.any())),
  })
    .index("by_status", ["status"])
    .index("by_priority", ["priority"])
    .index("by_agent", ["agentId"]),

  logs: defineTable({
    level: v.union(v.literal("info"), v.literal("warn"), v.literal("error"), v.literal("debug")),
    message: v.string(),
    agentId: v.optional(v.id("agents")),
    missionId: v.optional(v.id("missions")),
    timestamp: v.number(),
    source: v.string(),
    metadata: v.optional(v.record(v.string(), v.any())),
  })
    .index("by_timestamp", ["timestamp"])
    .index("by_agent", ["agentId"])
    .index("by_mission", ["missionId"])
    .index("by_level", ["level"]),

  metrics: defineTable({
    agentId: v.id("agents"),
    timestamp: v.number(),
    cpu: v.optional(v.number()),
    memory: v.optional(v.number()),
    tasksCompleted: v.optional(v.number()),
    tasksFailed: v.optional(v.number()),
    avgResponseTime: v.optional(v.number()),
  })
    .index("by_agent_timestamp", ["agentId", "timestamp"]),

  cronJobs: defineTable({
    name: v.string(),
    schedule: v.string(),
    status: v.union(v.literal("active"), v.literal("paused"), v.literal("error")),
    lastRun: v.optional(v.number()),
    nextRun: v.optional(v.number()),
    metadata: v.optional(v.record(v.string(), v.any())),
  })
    .index("by_status", ["status"]),

  files: defineTable({
    path: v.string(),
    type: v.union(v.literal("memory"), v.literal("state"), v.literal("log"), v.literal("other")),
    size: v.number(),
    modifiedAt: v.number(),
    content: v.optional(v.string()),
  })
    .index("by_type", ["type"])
    .index("by_path", ["path"]),
});
