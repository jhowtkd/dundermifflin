import { query } from "./_generated/server";

export const getDashboardStats = query({
  args: {},
  handler: async (ctx) => {
    // Get all tasks
    const tasks = await ctx.db.query("tasks").take(1000);
    const totalTasks = tasks.length;
    const completedTasks = tasks.filter((t) => t.status === "completed").length;
    const failedTasks = tasks.filter((t) => t.status === "failed").length;
    const runningTasks = tasks.filter((t) => t.status === "running").length;
    const pendingTasks = tasks.filter((t) => t.status === "pending").length;

    // Get agents
    const agents = await ctx.db.query("agents").take(100);
    const activeAgents = agents.filter((a) => a.status !== "offline").length;

    // Get cost logs
    const costLogs = await ctx.db.query("costLogs").take(1000);
    const totalCost = costLogs.reduce((sum, log) => sum + log.costUsd, 0);
    const totalTokens = costLogs.reduce((sum, log) => sum + log.tokensIn + log.tokensOut, 0);
    const avgResponseTime = costLogs.length > 0
      ? costLogs.reduce((sum, log) => sum + log.durationMs, 0) / costLogs.length
      : 0;

    // Get recent activity
    const recentTasks = tasks.slice(0, 10);
    const recentCosts = costLogs.slice(0, 10);

    return {
      tasks: {
        total: totalTasks,
        completed: completedTasks,
        failed: failedTasks,
        running: runningTasks,
        pending: pendingTasks,
      },
      agents: {
        total: agents.length,
        active: activeAgents,
        list: agents,
      },
      costs: {
        total: totalCost,
        tokens: totalTokens,
        avgResponseTime,
        recent: recentCosts,
      },
      recentTasks,
    };
  },
});

export const getAgentActivity = query({
  args: {},
  handler: async (ctx) => {
    const agents = await ctx.db.query("agents").take(100);
    return agents.map((agent) => ({
      id: agent._id,
      name: agent.name,
      slug: agent.slug,
      status: agent.status,
      emoji: agent.emoji,
      color: agent.color,
      tasksCompleted: agent.tasksCompleted,
      currentTask: agent.currentTask,
      progress: agent.progress,
      lastActive: agent.lastActive,
    }));
  },
});

export const getHourlyStats = query({
  args: {},
  handler: async (ctx) => {
    const logs = await ctx.db.query("costLogs").take(500);
    const hourlyData: Record<string, { cost: number; tokens: number; count: number }> = {};

    for (const log of logs) {
      const hour = log.timestamp.slice(0, 13) + ":00:00";
      if (!hourlyData[hour]) {
        hourlyData[hour] = { cost: 0, tokens: 0, count: 0 };
      }
      hourlyData[hour].cost += log.costUsd;
      hourlyData[hour].tokens += log.tokensIn + log.tokensOut;
      hourlyData[hour].count++;
    }

    return Object.entries(hourlyData)
      .map(([hour, data]) => ({ hour, ...data }))
      .sort((a, b) => a.hour.localeCompare(b.hour))
      .slice(-24);
  },
});
