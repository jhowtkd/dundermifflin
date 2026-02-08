import { v } from "convex/values";
import { query, mutation, action } from "./_generated/server";

// ============ AGENTS ============

export const listAgents = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db.query("agents").collect();
  },
});

export const getAgent = query({
  args: { slug: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("agents")
      .withIndex("by_slug", (q) => q.eq("slug", args.slug))
      .first();
  },
});

export const getAgentStats = query({
  args: { agentId: v.id("agents") },
  handler: async (ctx, args) => {
    const agent = await ctx.db.get(args.agentId);
    if (!agent) return null;

    const missions = await ctx.db
      .query("missions")
      .withIndex("by_agent", (q) => q.eq("agentId", args.agentId))
      .collect();

    const proposals = await ctx.db
      .query("proposals")
      .withIndex("by_agent", (q) => q.eq("agentId", args.agentId))
      .collect();

    return {
      ...agent,
      stats: {
        totalMissions: missions.length,
        successfulMissions: missions.filter((m) => m.status === "succeeded").length,
        failedMissions: missions.filter((m) => m.status === "failed").length,
        totalProposals: proposals.length,
        pendingProposals: proposals.filter((p) => p.status === "pending").length,
      },
    };
  },
});

// ============ PROPOSALS ============

export const listProposals = query({
  args: { status: v.optional(v.union(v.literal("pending"), v.literal("accepted"), v.literal("rejected"))) },
  handler: async (ctx, args) => {
    if (args.status) {
      return await ctx.db
        .query("proposals")
        .withIndex("by_status", (q) => q.eq("status", args.status!))
        .order("desc")
        .take(50);
    }
    return await ctx.db.query("proposals").order("desc").take(50);
  },
});

export const getProposal = query({
  args: { id: v.id("proposals") },
  handler: async (ctx, args) => {
    return await ctx.db.get(args.id);
  },
});

export const createProposal = mutation({
  args: {
    agentId: v.id("agents"),
    title: v.string(),
    description: v.optional(v.string()),
    missionType: v.optional(v.string()),
    priority: v.optional(v.number()),
    parameters: v.optional(v.object({})),
  },
  handler: async (ctx, args) => {
    const code = `PROP-${Date.now().toString(36).toUpperCase()}`;
    
    const proposalId = await ctx.db.insert("proposals", {
      proposalCode: code,
      agentId: args.agentId,
      title: args.title,
      description: args.description,
      missionType: args.missionType || "general",
      priority: args.priority || 5,
      parameters: args.parameters,
      status: "pending",
      proposedAt: Date.now(),
      autoApproved: false,
    });

    // Emitir evento
    await ctx.db.insert("events", {
      eventCode: `EVT-${Date.now().toString(36)}`,
      eventType: "mission_proposed",
      severity: "info",
      agentId: args.agentId,
      proposalId,
      title: `Proposta criada: ${args.title}`,
      occurredAt: Date.now(),
    });

    return proposalId;
  },
});

export const reviewProposal = mutation({
  args: {
    id: v.id("proposals"),
    status: v.union(v.literal("accepted"), v.literal("rejected")),
    notes: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, {
      status: args.status,
      reviewNotes: args.notes,
      reviewedAt: Date.now(),
    });

    // Se aceita, criar missão
    if (args.status === "accepted") {
      const proposal = await ctx.db.get(args.id);
      if (proposal) {
        const missionCode = `MS-${Date.now().toString(36).toUpperCase()}`;
        await ctx.db.insert("missions", {
          missionCode,
          proposalId: args.id,
          agentId: proposal.agentId,
          title: proposal.title,
          description: proposal.description,
          missionType: proposal.missionType,
          priority: proposal.priority,
          status: "approved",
        });
      }
    }

    return { success: true };
  },
});

// ============ MISSIONS ============

export const listMissions = query({
  args: { status: v.optional(v.union(v.literal("approved"), v.literal("running"), v.literal("succeeded"), v.literal("failed"), v.literal("cancelled"))) },
  handler: async (ctx, args) => {
    if (args.status) {
      return await ctx.db
        .query("missions")
        .withIndex("by_status", (q) => q.eq("status", args.status!))
        .order("desc")
        .take(50);
    }
    return await ctx.db.query("missions").order("desc").take(50);
  },
});

export const getMission = query({
  args: { id: v.id("missions") },
  handler: async (ctx, args) => {
    const mission = await ctx.db.get(args.id);
    if (!mission) return null;

    const steps = await ctx.db
      .query("steps")
      .withIndex("by_mission", (q) => q.eq("missionId", args.id))
      .collect();

    return { ...mission, steps };
  },
});

export const startMission = mutation({
  args: { id: v.id("missions") },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, {
      status: "running",
      startedAt: Date.now(),
    });

    const mission = await ctx.db.get(args.id);
    if (mission) {
      await ctx.db.insert("events", {
        eventCode: `EVT-${Date.now().toString(36)}`,
        eventType: "mission_started",
        severity: "info",
        agentId: mission.agentId,
        missionId: args.id,
        title: `Missão iniciada: ${mission.title}`,
        occurredAt: Date.now(),
      });
    }

    return { success: true };
  },
});

export const completeMission = mutation({
  args: {
    id: v.id("missions"),
    status: v.union(v.literal("succeeded"), v.literal("failed")),
    result: v.optional(v.any()),
    errorMessage: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, {
      status: args.status,
      completedAt: Date.now(),
      result: args.result,
      errorMessage: args.errorMessage,
    });

    const mission = await ctx.db.get(args.id);
    if (mission) {
      await ctx.db.insert("events", {
        eventCode: `EVT-${Date.now().toString(36)}`,
        eventType: args.status === "succeeded" ? "mission_completed" : "mission_failed",
        severity: args.status === "succeeded" ? "info" : "error",
        agentId: mission.agentId,
        missionId: args.id,
        title: `Missão ${args.status}: ${mission.title}`,
        payload: args.result,
        occurredAt: Date.now(),
      });
    }

    return { success: true };
  },
});

// ============ EVENTS ============

export const listEvents = query({
  args: { limit: v.optional(v.number()) },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("events")
      .order("desc")
      .take(args.limit || 100);
  },
});

export const getRecentEvents = query({
  args: { hours: v.optional(v.number()) },
  handler: async (ctx, args) => {
    const since = Date.now() - (args.hours || 24) * 60 * 60 * 1000;
    return await ctx.db
      .query("events")
      .withIndex("by_occurred", (q) => q.gte("occurredAt", since))
      .order("desc")
      .take(100);
  },
});

// ============ DASHBOARD STATS ============

export const getDashboardStats = query({
  args: {},
  handler: async (ctx) => {
    const agents = await ctx.db.query("agents").collect();
    const missions = await ctx.db.query("missions").collect();
    const proposals = await ctx.db.query("proposals").collect();
    const events = await ctx.db
      .query("events")
      .withIndex("by_occurred", (q) =>
        q.gte("occurredAt", Date.now() - 24 * 60 * 60 * 1000)
      )
      .collect();

    return {
      totalAgents: agents.length,
      activeAgents: agents.filter((a) => a.isActive).length,
      totalMissions: missions.length,
      runningMissions: missions.filter((m) => m.status === "running").length,
      completedMissions: missions.filter((m) => m.status === "succeeded").length,
      failedMissions: missions.filter((m) => m.status === "failed").length,
      pendingProposals: proposals.filter((p) => p.status === "pending").length,
      events24h: events.length,
    };
  },
});

// ============ STEPS ============

export const listSteps = query({
  args: { status: v.optional(v.union(v.literal("queued"), v.literal("running"), v.literal("succeeded"), v.literal("failed"), v.literal("skipped"))), missionId: v.optional(v.id("missions")) },
  handler: async (ctx, args) => {
    if (args.missionId) {
      return await ctx.db
        .query("steps")
        .withIndex("by_mission", (q) => q.eq("missionId", args.missionId!))
        .collect();
    }
    if (args.status) {
      return await ctx.db
        .query("steps")
        .withIndex("by_status", (q) => q.eq("status", args.status!))
        .order("desc")
        .take(50);
    }
    return await ctx.db.query("steps").order("desc").take(50);
  },
});

export const startStep = mutation({
  args: { id: v.id("steps") },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, {
      status: "running",
      startedAt: Date.now(),
    });
    
    const step = await ctx.db.get(args.id);
    if (step) {
      await ctx.db.insert("events", {
        eventCode: `EVT-${Date.now().toString(36)}`,
        eventType: "step_started",
        severity: "info",
        stepId: args.id,
        missionId: step.missionId,
        title: `Step iniciado: ${step.title}`,
        occurredAt: Date.now(),
      });
    }
    
    return { success: true };
  },
});

export const completeStep = mutation({
  args: { 
    id: v.id("steps"), 
    status: v.union(v.literal("succeeded"), v.literal("failed")),
    outputData: v.optional(v.any()),
    errorDetails: v.optional(v.any())
  },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, {
      status: args.status,
      completedAt: Date.now(),
      outputData: args.outputData,
      errorDetails: args.errorDetails,
    });
    
    const step = await ctx.db.get(args.id);
    if (step) {
      await ctx.db.insert("events", {
        eventCode: `EVT-${Date.now().toString(36)}`,
        eventType: args.status === "succeeded" ? "step_completed" : "step_failed",
        severity: args.status === "succeeded" ? "info" : "error",
        stepId: args.id,
        missionId: step.missionId,
        title: `Step ${args.status}: ${step.title}`,
        payload: args.outputData,
        occurredAt: Date.now(),
      });
    }
    
    return { success: true };
  },
});
