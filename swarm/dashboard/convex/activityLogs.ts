import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

export const list = query({
  args: { limit: v.optional(v.number()) },
  handler: async (ctx, { limit = 100 }) => {
    return await ctx.db.query("activityLogs")
      .order("desc")
      .take(limit);
  },
});

export const getByAgent = query({
  args: { agent: v.string(), limit: v.optional(v.number()) },
  handler: async (ctx, { agent, limit = 50 }) => {
    return await ctx.db
      .query("activityLogs")
      .withIndex("by_agent", (q) => q.eq("agent", agent))
      .order("desc")
      .take(limit);
  },
});

export const getByMission = query({
  args: { missionId: v.string(), limit: v.optional(v.number()) },
  handler: async (ctx, { missionId, limit = 100 }) => {
    return await ctx.db
      .query("activityLogs")
      .filter((q) => q.eq(q.field("metadata.missionId"), missionId))
      .order("desc")
      .take(limit);
  },
});

export const create = mutation({
  args: {
    timestamp: v.string(),
    agent: v.string(),
    action: v.string(),
    channel: v.optional(v.string()),
    metadata: v.optional(v.record(v.any())),
  },
  handler: async (ctx, { timestamp, agent, action, channel, metadata }) => {
    return await ctx.db.insert("activityLogs", {
      timestamp,
      agent,
      action,
      channel,
      metadata,
    });
  },
});

export const clearOld = mutation({
  args: { days: v.number() },
  handler: async (ctx, { days }) => {
    const cutoff = new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString();
    const oldLogs = await ctx.db
      .query("activityLogs")
      .withIndex("by_timestamp", (q) => q.lt("timestamp", cutoff))
      .collect();
    
    for (const log of oldLogs) {
      await ctx.db.delete(log._id);
    }
    
    return { deleted: oldLogs.length };
  },
});
