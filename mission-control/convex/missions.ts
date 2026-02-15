import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

export const list = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db.query("missions").order("desc").take(100);
  },
});

export const get = query({
  args: { id: v.id("missions") },
  handler: async (ctx, args) => {
    return await ctx.db.get(args.id);
  },
});

export const byStatus = query({
  args: { status: v.union(v.literal("pending"), v.literal("running"), v.literal("completed"), v.literal("failed")) },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("missions")
      .withIndex("by_status", (q) => q.eq("status", args.status))
      .order("desc")
      .collect();
  },
});

export const byAgent = query({
  args: { agentId: v.id("agents") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("missions")
      .withIndex("by_agent", (q) => q.eq("agentId", args.agentId))
      .order("desc")
      .collect();
  },
});

export const create = mutation({
  args: {
    title: v.string(),
    description: v.string(),
    priority: v.optional(v.union(v.literal("low"), v.literal("medium"), v.literal("high"), v.literal("critical"))),
    metadata: v.optional(v.record(v.string(), v.any())),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("missions", {
      title: args.title,
      description: args.description,
      status: "pending",
      priority: args.priority ?? "medium",
      steps: [],
      progress: 0,
      metadata: args.metadata ?? {},
    });
  },
});

export const start = mutation({
  args: {
    id: v.id("missions"),
    agentId: v.id("agents"),
  },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, {
      status: "running",
      agentId: args.agentId,
      startedAt: Date.now(),
    });
  },
});

export const updateProgress = mutation({
  args: {
    id: v.id("missions"),
    progress: v.number(),
    step: v.optional(v.record(v.string(), v.any())),
  },
  handler: async (ctx, args) => {
    const mission = await ctx.db.get(args.id);
    if (!mission) throw new Error("Mission not found");
    
    const steps = args.step ? [...mission.steps, args.step] : mission.steps;
    
    await ctx.db.patch(args.id, {
      progress: Math.min(100, Math.max(0, args.progress)),
      steps,
    });
  },
});

export const complete = mutation({
  args: {
    id: v.id("missions"),
    success: v.boolean(),
  },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, {
      status: args.success ? "completed" : "failed",
      progress: args.success ? 100 : undefined,
      completedAt: Date.now(),
    });
  },
});

export const cancel = mutation({
  args: { id: v.id("missions") },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, {
      status: "failed",
      completedAt: Date.now(),
    });
  },
});
