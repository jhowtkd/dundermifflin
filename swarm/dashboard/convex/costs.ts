import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

export const list = query({
  args: { limit: v.optional(v.number()) },
  handler: async (ctx, { limit = 100 }) => {
    return await ctx.db.query("costLogs").order("desc").take(limit);
  },
});

export const add = mutation({
  args: {
    agent: v.string(),
    model: v.string(),
    tokensIn: v.number(),
    tokensOut: v.number(),
    costUsd: v.number(),
    durationMs: v.number(),
    success: v.boolean(),
    error: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("costLogs", {
      ...args,
      timestamp: new Date().toISOString(),
    });
  },
});

export const stats = query({
  args: {},
  handler: async (ctx) => {
    const logs = await ctx.db.query("costLogs").take(1000);
    
    let totalCost = 0;
    let totalTokens = 0;
    let successCount = 0;
    let errorCount = 0;
    let totalDuration = 0;
    const agentStats: Record<string, { cost: number; tokens: number; count: number }> = {};
    const modelStats: Record<string, { cost: number; tokens: number; count: number }> = {};

    for (const log of logs) {
      totalCost += log.costUsd;
      totalTokens += log.tokensIn + log.tokensOut;
      totalDuration += log.durationMs;
      if (log.success) successCount++;
      else errorCount++;

      if (!agentStats[log.agent]) {
        agentStats[log.agent] = { cost: 0, tokens: 0, count: 0 };
      }
      agentStats[log.agent].cost += log.costUsd;
      agentStats[log.agent].tokens += log.tokensIn + log.tokensOut;
      agentStats[log.agent].count++;

      if (!modelStats[log.model]) {
        modelStats[log.model] = { cost: 0, tokens: 0, count: 0 };
      }
      modelStats[log.model].cost += log.costUsd;
      modelStats[log.model].tokens += log.tokensIn + log.tokensOut;
      modelStats[log.model].count++;
    }

    return {
      totalCost,
      totalTokens,
      successCount,
      errorCount,
      avgDuration: logs.length > 0 ? totalDuration / logs.length : 0,
      agentStats,
      modelStats,
    };
  },
});

export const recent = query({
  args: { limit: v.optional(v.number()) },
  handler: async (ctx, { limit = 20 }) => {
    return await ctx.db.query("costLogs").order("desc").take(limit);
  },
});
