import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

export const list = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db.query("agents").order("desc").take(100);
  },
});

export const get = query({
  args: { slug: v.string() },
  handler: async (ctx, { slug }) => {
    return await ctx.db
      .query("agents")
      .withIndex("by_slug", (q) => q.eq("slug", slug))
      .first();
  },
});

export const updateStatus = mutation({
  args: {
    id: v.id("agents"),
    status: v.union(v.literal("idle"), v.literal("working"), v.literal("error"), v.literal("offline")),
    currentTask: v.optional(v.string()),
    progress: v.number(),
  },
  handler: async (ctx, { id, status, currentTask, progress }) => {
    await ctx.db.patch(id, {
      status,
      currentTask,
      progress,
      lastActive: new Date().toISOString(),
    });
  },
});

export const incrementTasks = mutation({
  args: { id: v.id("agents") },
  handler: async (ctx, { id }) => {
    const agent = await ctx.db.get(id);
    if (agent) {
      await ctx.db.patch(id, {
        tasksCompleted: agent.tasksCompleted + 1,
        lastActive: new Date().toISOString(),
      });
    }
  },
});

export const seed = mutation({
  args: {},
  handler: async (ctx) => {
    const agents = [
      { name: "Ralph", slug: "ralph", role: "Coordinator", emoji: "🎩", color: "#a855f7" },
      { name: "Scout", slug: "scout", role: "Research", emoji: "🔍", color: "#3b82f6" },
      { name: "Max", slug: "max", role: "Builder", emoji: "🛠️", color: "#22c55e" },
      { name: "Maya", slug: "maya", role: "Copywriter", emoji: "📝", color: "#f59e0b" },
      { name: "Tracker", slug: "tracker", role: "Analytics", emoji: "📊", color: "#ef4444" },
      { name: "Watcher", slug: "watcher", role: "Monitor", emoji: "👁️", color: "#6366f1" },
    ];

    for (const agent of agents) {
      const existing = await ctx.db
        .query("agents")
        .withIndex("by_slug", (q) => q.eq("slug", agent.slug))
        .first();
      
      if (!existing) {
        await ctx.db.insert("agents", {
          ...agent,
          status: "idle",
          lastActive: new Date().toISOString(),
          tasksCompleted: 0,
          progress: 0,
        });
      }
    }
    return { success: true };
  },
});
