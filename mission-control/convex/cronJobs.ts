import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

export const list = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db.query("cronJobs").order("desc").take(100);
  },
});

export const get = query({
  args: { id: v.id("cronJobs") },
  handler: async (ctx, args) => {
    return await ctx.db.get(args.id);
  },
});

export const byStatus = query({
  args: { status: v.union(v.literal("active"), v.literal("paused"), v.literal("error")) },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("cronJobs")
      .withIndex("by_status", (q) => q.eq("status", args.status))
      .collect();
  },
});

export const create = mutation({
  args: {
    name: v.string(),
    schedule: v.string(),
    metadata: v.optional(v.record(v.string(), v.any())),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("cronJobs", {
      name: args.name,
      schedule: args.schedule,
      status: "active",
      lastRun: undefined,
      nextRun: undefined,
      metadata: args.metadata ?? {},
    });
  },
});

export const updateStatus = mutation({
  args: {
    id: v.id("cronJobs"),
    status: v.union(v.literal("active"), v.literal("paused"), v.literal("error")),
  },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, {
      status: args.status,
    });
  },
});

export const recordRun = mutation({
  args: {
    id: v.id("cronJobs"),
    nextRun: v.number(),
  },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, {
      lastRun: Date.now(),
      nextRun: args.nextRun,
    });
  },
});
