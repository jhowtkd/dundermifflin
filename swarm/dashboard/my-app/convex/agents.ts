import { v } from "convex/values";
import { query, mutation } from "./_generated/server";

// Get all agents
export const getAll = query({
  handler: async (ctx) => {
    return await ctx.db.query("agents").collect();
  },
});

// Get agent by slug
export const getBySlug = query({
  args: { slug: v.string() },
  handler: async (ctx, { slug }) => {
    return await ctx.db
      .query("agents")
      .withIndex("by_slug", (q) => q.eq("slug", slug))
      .first();
  },
});

// Update agent status
export const updateStatus = mutation({
  args: {
    slug: v.string(),
    status: v.union(v.literal("idle"), v.literal("working"), v.literal("offline")),
    currentTask: v.optional(v.string()),
  },
  handler: async (ctx, { slug, status, currentTask }) => {
    const agent = await ctx.db
      .query("agents")
      .withIndex("by_slug", (q) => q.eq("slug", slug))
      .first();
    
    if (agent) {
      await ctx.db.patch(agent._id, {
        status,
        currentTask,
        lastHeartbeat: Date.now(),
      });
    }
  },
});

// Heartbeat from agent
export const heartbeat = mutation({
  args: {
    slug: v.string(),
  },
  handler: async (ctx, { slug }) => {
    const agent = await ctx.db
      .query("agents")
      .withIndex("by_slug", (q) => q.eq("slug", slug))
      .first();
    
    if (agent) {
      await ctx.db.patch(agent._id, {
        lastHeartbeat: Date.now(),
      });
    }
  },
});

// Increment task counters
export const incrementCompleted = mutation({
  args: { slug: v.string() },
  handler: async (ctx, { slug }) => {
    const agent = await ctx.db
      .query("agents")
      .withIndex("by_slug", (q) => q.eq("slug", slug))
      .first();
    
    if (agent) {
      await ctx.db.patch(agent._id, {
        tasksCompleted: agent.tasksCompleted + 1,
        status: "idle",
        currentTask: undefined,
      });
    }
  },
});

export const incrementFailed = mutation({
  args: { slug: v.string() },
  handler: async (ctx, { slug }) => {
    const agent = await ctx.db
      .query("agents")
      .withIndex("by_slug", (q) => q.eq("slug", slug))
      .first();
    
    if (agent) {
      await ctx.db.patch(agent._id, {
        tasksFailed: agent.tasksFailed + 1,
        status: "idle",
        currentTask: undefined,
      });
    }
  },
});

// Initialize default agents
export const initialize = mutation({
  handler: async (ctx) => {
    const defaultAgents = [
      { slug: "ralph", name: "Ralph", role: "coordinate", emoji: "🎩", status: "idle" },
      { slug: "scout", name: "Scout", role: "find", emoji: "🔍", status: "idle" },
      { slug: "max", name: "Max", role: "build", emoji: "🛠️", status: "idle" },
      { slug: "maya", name: "Maya", role: "create", emoji: "✍️", status: "idle" },
      { slug: "tracker", name: "Tracker", role: "track", emoji: "📊", status: "idle" },
      { slug: "watcher", name: "Watcher", role: "watch", emoji: "👁️", status: "idle" },
    ];

    for (const agent of defaultAgents) {
      const existing = await ctx.db
        .query("agents")
        .withIndex("by_slug", (q) => q.eq("slug", agent.slug))
        .first();
      
      if (!existing) {
        await ctx.db.insert("agents", {
          ...agent,
          status: "idle",
          lastHeartbeat: Date.now(),
          tasksCompleted: 0,
          tasksFailed: 0,
        });
      }
    }
  },
});
