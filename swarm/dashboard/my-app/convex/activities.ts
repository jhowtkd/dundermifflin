import { v } from "convex/values";
import { query, mutation } from "./_generated/server";

// Get recent activities
export const getRecent = query({
  args: { limit: v.optional(v.number()) },
  handler: async (ctx, { limit = 50 }) => {
    return await ctx.db
      .query("activities")
      .order("desc")
      .take(limit);
  },
});

// Get activities by agent
export const getByAgent = query({
  args: { 
    agentSlug: v.string(),
    limit: v.optional(v.number()) 
  },
  handler: async (ctx, { agentSlug, limit = 20 }) => {
    return await ctx.db
      .query("activities")
      .withIndex("by_agent", (q) => q.eq("agentSlug", agentSlug))
      .order("desc")
      .take(limit);
  },
});

// Create activity
export const create = mutation({
  args: {
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
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("activities", {
      ...args,
      timestamp: Date.now(),
    });
  },
});

// Get live feed (last 20 activities)
export const getLiveFeed = query({
  handler: async (ctx) => {
    return await ctx.db
      .query("activities")
      .order("desc")
      .take(20);
  },
});
