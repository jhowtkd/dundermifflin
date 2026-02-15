import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

export const list = query({
  args: {
    limit: v.optional(v.number()),
    level: v.optional(v.union(v.literal("info"), v.literal("warn"), v.literal("error"), v.literal("debug"))),
  },
  handler: async (ctx, args) => {
    let query = ctx.db.query("logs").order("desc");
    
    if (args.level) {
      query = ctx.db.query("logs").withIndex("by_level", (q) => q.eq("level", args.level!));
    }
    
    return await query.take(args.limit ?? 100);
  },
});

export const byAgent = query({
  args: {
    agentId: v.id("agents"),
    limit: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("logs")
      .withIndex("by_agent", (q) => q.eq("agentId", args.agentId))
      .order("desc")
      .take(args.limit ?? 50);
  },
});

export const byMission = query({
  args: {
    missionId: v.id("missions"),
    limit: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("logs")
      .withIndex("by_mission", (q) => q.eq("missionId", args.missionId))
      .order("desc")
      .take(args.limit ?? 50);
  },
});

export const create = mutation({
  args: {
    level: v.union(v.literal("info"), v.literal("warn"), v.literal("error"), v.literal("debug")),
    message: v.string(),
    source: v.string(),
    agentId: v.optional(v.id("agents")),
    missionId: v.optional(v.id("missions")),
    metadata: v.optional(v.record(v.string(), v.any())),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("logs", {
      level: args.level,
      message: args.message,
      source: args.source,
      agentId: args.agentId,
      missionId: args.missionId,
      timestamp: Date.now(),
      metadata: args.metadata ?? {},
    });
  },
});
