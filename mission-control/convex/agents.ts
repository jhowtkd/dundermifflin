import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

export const list = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db.query("agents").order("desc").take(100);
  },
});

export const get = query({
  args: { id: v.id("agents") },
  handler: async (ctx, args) => {
    return await ctx.db.get(args.id);
  },
});

export const byStatus = query({
  args: { status: v.union(v.literal("online"), v.literal("busy"), v.literal("offline"), v.literal("error")) },
  handler: async (ctx, args) => {
    return await ctx.db.query("agents").withIndex("by_status", (q) => q.eq("status", args.status)).collect();
  },
});

export const create = mutation({
  args: {
    name: v.string(),
    type: v.string(),
    status: v.optional(v.union(v.literal("online"), v.literal("busy"), v.literal("offline"), v.literal("error"))),
    metadata: v.optional(v.record(v.string(), v.any())),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("agents", {
      name: args.name,
      type: args.type,
      status: args.status ?? "offline",
      lastSeen: Date.now(),
      metadata: args.metadata ?? {},
    });
  },
});

export const updateStatus = mutation({
  args: {
    id: v.id("agents"),
    status: v.union(v.literal("online"), v.literal("busy"), v.literal("offline"), v.literal("error")),
    currentTask: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, {
      status: args.status,
      lastSeen: Date.now(),
      currentTask: args.currentTask,
    });
  },
});

export const heartbeat = mutation({
  args: {
    id: v.id("agents"),
    metadata: v.optional(v.record(v.string(), v.any())),
  },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, {
      lastSeen: Date.now(),
      metadata: args.metadata,
    });
  },
});
