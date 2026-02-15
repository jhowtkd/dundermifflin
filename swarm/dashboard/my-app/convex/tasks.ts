import { v } from "convex/values";
import { query, mutation } from "./_generated/server";

// Get all tasks
export const getAll = query({
  handler: async (ctx) => {
    return await ctx.db
      .query("tasks")
      .order("desc")
      .take(100);
  },
});

// Get tasks by status
export const getByStatus = query({
  args: { 
    status: v.union(
      v.literal("pending"),
      v.literal("in_progress"),
      v.literal("completed"),
      v.literal("failed")
    ) 
  },
  handler: async (ctx, { status }) => {
    return await ctx.db
      .query("tasks")
      .withIndex("by_status", (q) => q.eq("status", status))
      .order("desc")
      .take(50);
  },
});

// Get task by code
export const getByCode = query({
  args: { code: v.string() },
  handler: async (ctx, { code }) => {
    return await ctx.db
      .query("tasks")
      .filter((q) => q.eq(q.field("code"), code))
      .first();
  },
});

// Create new task
export const create = mutation({
  args: {
    code: v.string(),
    description: v.string(),
    priority: v.union(v.literal("low"), v.literal("medium"), v.literal("high")),
    complexity: v.union(v.literal("simple"), v.literal("medium"), v.literal("complex")),
    agentsRequired: v.array(v.string()),
    parentTaskId: v.optional(v.id("tasks")),
  },
  handler: async (ctx, args) => {
    const taskId = await ctx.db.insert("tasks", {
      ...args,
      status: "pending",
      createdAt: Date.now(),
    });
    return taskId;
  },
});

// Assign task to agent
export const assign = mutation({
  args: {
    taskId: v.id("tasks"),
    agentSlug: v.string(),
  },
  handler: async (ctx, { taskId, agentSlug }) => {
    await ctx.db.patch(taskId, {
      assignedAgent: agentSlug,
      status: "in_progress",
      startedAt: Date.now(),
    });
  },
});

// Complete task
export const complete = mutation({
  args: { taskId: v.id("tasks") },
  handler: async (ctx, { taskId }) => {
    await ctx.db.patch(taskId, {
      status: "completed",
      completedAt: Date.now(),
    });
  },
});

// Fail task
export const fail = mutation({
  args: { taskId: v.id("tasks") },
  handler: async (ctx, { taskId }) => {
    await ctx.db.patch(taskId, {
      status: "failed",
      completedAt: Date.now(),
    });
  },
});

// Get task stats
export const getStats = query({
  handler: async (ctx) => {
    const all = await ctx.db.query("tasks").collect();
    return {
      total: all.length,
      pending: all.filter((t) => t.status === "pending").length,
      inProgress: all.filter((t) => t.status === "in_progress").length,
      completed: all.filter((t) => t.status === "completed").length,
      failed: all.filter((t) => t.status === "failed").length,
    };
  },
});

// Get today's tasks
export const getToday = query({
  handler: async (ctx) => {
    const startOfDay = new Date();
    startOfDay.setHours(0, 0, 0, 0);
    
    const all = await ctx.db.query("tasks").collect();
    return all.filter((t) => t.createdAt >= startOfDay.getTime());
  },
});
