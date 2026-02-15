import { v } from "convex/values";
import { query, mutation } from "./_generated/server";

// Get metrics for date
export const getByDate = query({
  args: { date: v.string() },
  handler: async (ctx, { date }) => {
    return await ctx.db
      .query("metrics")
      .withIndex("by_date", (q) => q.eq("date", date))
      .first();
  },
});

// Get metrics range
export const getRange = query({
  args: { 
    startDate: v.string(),
    endDate: v.string() 
  },
  handler: async (ctx, { startDate, endDate }) => {
    return await ctx.db
      .query("metrics")
      .filter((q) => 
        q.and(
          q.gte(q.field("date"), startDate),
          q.lte(q.field("date"), endDate)
        )
      )
      .order("asc")
      .collect();
  },
});

// Update or create daily metrics
export const upsertDaily = mutation({
  args: {
    date: v.string(),
    tasksCreated: v.optional(v.number()),
    tasksCompleted: v.optional(v.number()),
    tasksFailed: v.optional(v.number()),
    tokensUsed: v.optional(v.number()),
    costUSD: v.optional(v.number()),
    activeAgents: v.optional(v.number()),
    avgResponseTime: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    const existing = await ctx.db
      .query("metrics")
      .withIndex("by_date", (q) => q.eq("date", args.date))
      .first();

    if (existing) {
      await ctx.db.patch(existing._id, args);
    } else {
      await ctx.db.insert("metrics", {
        ...args,
        tasksCreated: args.tasksCreated || 0,
        tasksCompleted: args.tasksCompleted || 0,
        tasksFailed: args.tasksFailed || 0,
        tokensUsed: args.tokensUsed || 0,
        costUSD: args.costUSD || 0,
        activeAgents: args.activeAgents || 0,
        avgResponseTime: args.avgResponseTime || 0,
      });
    }
  },
});

// Increment tasks created
export const incrementCreated = mutation({
  handler: async (ctx) => {
    const today = new Date().toISOString().split("T")[0];
    const existing = await ctx.db
      .query("metrics")
      .withIndex("by_date", (q) => q.eq("date", today))
      .first();

    if (existing) {
      await ctx.db.patch(existing._id, {
        tasksCreated: existing.tasksCreated + 1,
      });
    } else {
      await ctx.db.insert("metrics", {
        date: today,
        tasksCreated: 1,
        tasksCompleted: 0,
        tasksFailed: 0,
        tokensUsed: 0,
        costUSD: 0,
        activeAgents: 0,
        avgResponseTime: 0,
      });
    }
  },
});

// Increment tasks completed
export const incrementCompleted = mutation({
  handler: async (ctx) => {
    const today = new Date().toISOString().split("T")[0];
    const existing = await ctx.db
      .query("metrics")
      .withIndex("by_date", (q) => q.eq("date", today))
      .first();

    if (existing) {
      await ctx.db.patch(existing._id, {
        tasksCompleted: existing.tasksCompleted + 1,
      });
    } else {
      await ctx.db.insert("metrics", {
        date: today,
        tasksCreated: 0,
        tasksCompleted: 1,
        tasksFailed: 0,
        tokensUsed: 0,
        costUSD: 0,
        activeAgents: 0,
        avgResponseTime: 0,
      });
    }
  },
});

// Add cost
export const addCost = mutation({
  args: { 
    tokens: v.number(),
    cost: v.number() 
  },
  handler: async (ctx, { tokens, cost }) => {
    const today = new Date().toISOString().split("T")[0];
    const existing = await ctx.db
      .query("metrics")
      .withIndex("by_date", (q) => q.eq("date", today))
      .first();

    if (existing) {
      await ctx.db.patch(existing._id, {
        tokensUsed: existing.tokensUsed + tokens,
        costUSD: existing.costUSD + cost,
      });
    } else {
      await ctx.db.insert("metrics", {
        date: today,
        tasksCreated: 0,
        tasksCompleted: 0,
        tasksFailed: 0,
        tokensUsed: tokens,
        costUSD: cost,
        activeAgents: 0,
        avgResponseTime: 0,
      });
    }
  },
});
