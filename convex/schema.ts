import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

// Status enums
const proposalStatus = v.union(
  v.literal("pending"),
  v.literal("accepted"),
  v.literal("rejected")
);

const missionStatus = v.union(
  v.literal("approved"),
  v.literal("running"),
  v.literal("succeeded"),
  v.literal("failed"),
  v.literal("cancelled")
);

const stepStatus = v.union(
  v.literal("queued"),
  v.literal("running"),
  v.literal("succeeded"),
  v.literal("failed"),
  v.literal("skipped")
);

const eventType = v.union(
  v.literal("mission_proposed"),
  v.literal("mission_started"),
  v.literal("mission_completed"),
  v.literal("mission_failed"),
  v.literal("step_started"),
  v.literal("step_completed"),
  v.literal("step_failed"),
  v.literal("trigger_fired"),
  v.literal("reaction_queued"),
  v.literal("reaction_executed"),
  v.literal("insight_created"),
  v.literal("memory_stored"),
  v.literal("tweet_drafted"),
  v.literal("tweet_posted"),
  v.literal("system_alert"),
  v.literal("agent_communication")
);

const eventSeverity = v.union(
  v.literal("debug"),
  v.literal("info"),
  v.literal("warning"),
  v.literal("error"),
  v.literal("critical")
);

export default defineSchema({
  // Agents - Os 6 agentes de IA
  agents: defineTable({
    slug: v.string(),
    name: v.string(),
    role: v.string(),
    description: v.optional(v.string()),
    personality: v.optional(v.any()),
    capabilities: v.optional(v.array(v.string())),
    config: v.optional(v.any()),
    avatarUrl: v.optional(v.string()),
    isActive: v.boolean(),
    priority: v.number(),
    dailyQuota: v.number(),
    quotaUsed: v.optional(v.number()),
    lastResetAt: v.optional(v.number()), // Unix timestamp
  })
    .index("by_slug", ["slug"])
    .index("by_active", ["isActive"]),

  // Mission Proposals - Propostas de missão
  proposals: defineTable({
    proposalCode: v.string(),
    agentId: v.id("agents"),
    title: v.string(),
    description: v.optional(v.string()),
    missionType: v.string(),
    priority: v.number(),
    parameters: v.optional(v.any()),
    status: proposalStatus,
    proposedAt: v.number(),
    reviewedAt: v.optional(v.number()),
    reviewedBy: v.optional(v.string()),
    reviewNotes: v.optional(v.string()),
    autoApproved: v.boolean(),
  })
    .index("by_status", ["status"])
    .index("by_agent", ["agentId"])
    .index("by_status_agent", ["status", "agentId"]),

  // Missions - Missões aprovadas
  missions: defineTable({
    missionCode: v.string(),
    proposalId: v.optional(v.id("proposals")),
    agentId: v.id("agents"),
    title: v.string(),
    description: v.optional(v.string()),
    missionType: v.string(),
    priority: v.number(),
    status: missionStatus,
    startedAt: v.optional(v.number()),
    completedAt: v.optional(v.number()),
    result: v.optional(v.any()),
    errorMessage: v.optional(v.string()),
    parentMissionId: v.optional(v.id("missions")),
  })
    .index("by_status", ["status"])
    .index("by_agent", ["agentId"])
    .index("by_status_agent", ["status", "agentId"]),

  // Mission Steps - Passos individuais
  steps: defineTable({
    missionId: v.id("missions"),
    stepNumber: v.number(),
    stepCode: v.string(),
    title: v.string(),
    description: v.optional(v.string()),
    actionType: v.string(),
    actionConfig: v.optional(v.any()),
    status: stepStatus,
    startedAt: v.optional(v.number()),
    completedAt: v.optional(v.number()),
    inputData: v.optional(v.any()),
    outputData: v.optional(v.any()),
    errorDetails: v.optional(v.any()),
    retryCount: v.number(),
    maxRetries: v.number(),
    dependsOn: v.optional(v.array(v.id("steps"))),
  })
    .index("by_mission", ["missionId"])
    .index("by_status", ["status"])
    .index("by_mission_status", ["missionId", "status"]),

  // Events - Stream de eventos
  events: defineTable({
    eventCode: v.string(),
    eventType: eventType,
    severity: eventSeverity,
    agentId: v.optional(v.id("agents")),
    missionId: v.optional(v.id("missions")),
    stepId: v.optional(v.id("steps")),
    proposalId: v.optional(v.id("proposals")),
    title: v.string(),
    description: v.optional(v.string()),
    payload: v.optional(v.any()),
    metadata: v.optional(v.any()),
    correlationId: v.optional(v.string()),
    parentEventId: v.optional(v.id("events")),
    occurredAt: v.number(),
  })
    .index("by_type", ["eventType"])
    .index("by_agent", ["agentId"])
    .index("by_mission", ["missionId"])
    .index("by_occurred", ["occurredAt"]),

  // Policies - Políticas configuráveis
  policies: defineTable({
    policyKey: v.string(),
    policyName: v.string(),
    description: v.optional(v.string()),
    category: v.string(),
    value: v.any(),
    isActive: v.boolean(),
    appliesTo: v.optional(v.id("agents")), // null = global
  })
    .index("by_key", ["policyKey"])
    .index("by_active", ["isActive"]),

  // Memories - Memórias dos agentes
  memories: defineTable({
    memoryCode: v.string(),
    agentId: v.id("agents"),
    content: v.string(),
    memoryType: v.union(
      v.literal("short_term"),
      v.literal("long_term"),
      v.literal("episodic"),
      v.literal("semantic")
    ),
    context: v.optional(v.any()),
    tags: v.optional(v.array(v.string())),
    importance: v.number(),
    relevanceScore: v.optional(v.number()),
    sourceEventId: v.optional(v.id("events")),
    sourceMissionId: v.optional(v.id("missions")),
    expiresAt: v.optional(v.number()),
  })
    .index("by_agent", ["agentId"])
    .index("by_type", ["memoryType"])
    .index("by_expires", ["expiresAt"]),

  // Insights - Insights gerados
  insights: defineTable({
    insightCode: v.string(),
    agentId: v.id("agents"),
    title: v.string(),
    content: v.string(),
    insightType: v.string(),
    category: v.string(),
    confidence: v.number(),
    impactScore: v.number(),
    isPublic: v.boolean(),
  })
    .index("by_agent", ["agentId"])
    .index("by_type", ["insightType"]),
});
