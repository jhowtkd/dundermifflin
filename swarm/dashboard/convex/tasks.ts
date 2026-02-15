import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

export const list = query({
  args: { limit: v.optional(v.number()) },
  handler: async (ctx, { limit = 50 }) => {
    return await ctx.db.query("tasks").order("desc").take(limit);
  },
});

export const getByStatus = query({
  args: { 
    status: v.union(v.literal("pending"), v.literal("running"), v.literal("completed"), v.literal("failed"))
  },
  handler: async (ctx, { status }) => {
    return await ctx.db
      .query("tasks")
      .withIndex("by_status", (q) => q.eq("status", status))
      .order("desc")
      .take(50);
  },
});

export const create = mutation({
  args: {
    title: v.string(),
    description: v.string(),
    priority: v.union(v.literal("low"), v.literal("medium"), v.literal("high")),
    project: v.optional(v.string()),
  },
  handler: async (ctx, { title, description, priority, project }) => {
    const now = new Date().toISOString();
    return await ctx.db.insert("tasks", {
      title,
      description,
      priority,
      project,
      status: "pending",
      createdAt: now,
      updatedAt: now,
    });
  },
});

export const updateStatus = mutation({
  args: {
    id: v.id("tasks"),
    status: v.union(v.literal("pending"), v.literal("running"), v.literal("completed"), v.literal("failed")),
    cost: v.optional(v.number()),
    tokens: v.optional(v.number()),
    duration: v.optional(v.number()),
  },
  handler: async (ctx, { id, status, cost, tokens, duration }) => {
    const updates: Record<string, unknown> = { status, updatedAt: new Date().toISOString() };
    if (cost !== undefined) updates.cost = cost;
    if (tokens !== undefined) updates.tokens = tokens;
    if (duration !== undefined) updates.duration = duration;
    if (status === "completed" || status === "failed") {
      updates.completedAt = new Date().toISOString();
    }
    await ctx.db.patch(id, updates);
  },
});

export const assign = mutation({
  args: {
    id: v.id("tasks"),
    agentId: v.id("agents"),
  },
  handler: async (ctx, { id, agentId }) => {
    const agent = await ctx.db.get(agentId);
    await ctx.db.patch(id, {
      agentId,
      agentName: agent?.name,
      status: "running",
      updatedAt: new Date().toISOString(),
    });
  },
});

export const recent = query({
  args: { limit: v.optional(v.number()) },
  handler: async (ctx, { limit = 10 }) => {
    return await ctx.db.query("tasks").order("desc").take(limit);
  },
});
