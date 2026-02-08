import { v } from "convex/values";
import { internalMutation } from "./_generated/server";

// Dados iniciais dos 6 agentes
const INITIAL_AGENTS = [
  {
    slug: "minion",
    name: "Minion",
    role: "Decision Maker",
    description: "Líder decisivo e pragmático. Toma decisões finais e aprova propostas.",
    personality: {
      traits: ["decisive", "pragmatic", "direct", "results-oriented"],
      communicationStyle: "direct",
      decisionSpeed: "fast",
    },
    capabilities: ["decision_making", "proposal_review", "strategy", "leadership"],
    avatarUrl: "🎯",
    priority: 100,
    dailyQuota: 8,
  },
  {
    slug: "sage",
    name: "Sage",
    role: "Strategist",
    description: "Analítico e ponderado. Analisa estratégia e diagnostica falhas.",
    personality: {
      traits: ["analytical", "thoughtful", "wise", "patient"],
      communicationStyle: "reflective",
      decisionSpeed: "deliberate",
    },
    capabilities: ["strategy", "diagnostics", "analysis", "planning"],
    avatarUrl: "🔮",
    priority: 90,
    dailyQuota: 5,
  },
  {
    slug: "scout",
    name: "Scout",
    role: "Intelligence",
    description: "Curioso e ágil. Coleta inteligência e pesquisa na web.",
    personality: {
      traits: ["curious", "agile", "investigative", "adaptable"],
      communicationStyle: "inquisitive",
      decisionSpeed: "fast",
    },
    capabilities: ["research", "web_search", "intelligence", "monitoring"],
    avatarUrl: "🔍",
    priority: 80,
    dailyQuota: 10,
  },
  {
    slug: "quill",
    name: "Quill",
    role: "Content Writer",
    description: "Criativo e eloquente. Escreve conteúdo, artigos e posts.",
    personality: {
      traits: ["creative", "eloquent", "detail-oriented", "expressive"],
      communicationStyle: "expressive",
      decisionSpeed: "moderate",
    },
    capabilities: ["writing", "content_creation", "editing", "storytelling"],
    avatarUrl: "✍️",
    priority: 70,
    dailyQuota: 6,
  },
  {
    slug: "xalt",
    name: "Xalt",
    role: "Social Media",
    description: "Extrovertido e engajado. Gerencia Twitter/X e responde mentions.",
    personality: {
      traits: ["extroverted", "engaging", "trend-aware", "responsive"],
      communicationStyle: "casual",
      decisionSpeed: "fast",
    },
    capabilities: ["social_media", "twitter", "engagement", "community"],
    avatarUrl: "📱",
    priority: 60,
    dailyQuota: 8,
  },
  {
    slug: "observer",
    name: "Observer",
    role: "Quality Checker",
    description: "Crítico e meticuloso. Revisa qualidade e aprova/rejeita conteúdo.",
    personality: {
      traits: ["critical", "meticulous", "objective", "thorough"],
      communicationStyle: "analytical",
      decisionSpeed: "deliberate",
    },
    capabilities: ["quality_control", "review", "validation", "feedback"],
    avatarUrl: "👁️",
    priority: 50,
    dailyQuota: 4,
  },
];

const INITIAL_POLICIES = [
  {
    policyKey: "auto_approve",
    policyName: "Auto-Approve Low Risk",
    description: "Aprova automaticamente propostas de baixo risco",
    category: "approval",
    value: { enabled: false, maxPriority: 3 },
    isActive: true,
  },
  {
    policyKey: "daily_quota",
    policyName: "Daily Action Quota",
    description: "Limita ações diárias por agente",
    category: "quota",
    value: { enabled: true, defaultQuota: 5 },
    isActive: true,
  },
];

export const seed = internalMutation({
  args: {},
  handler: async (ctx) => {
    // Verificar se já tem dados
    const existingAgents = await ctx.db.query("agents").collect();
    if (existingAgents.length > 0) {
      console.log("Database already seeded");
      return { seeded: false, message: "Already has data" };
    }

    // Criar agentes
    for (const agent of INITIAL_AGENTS) {
      await ctx.db.insert("agents", {
        ...agent,
        isActive: true,
        quotaUsed: 0,
        lastResetAt: Date.now(),
        config: {},
      });
      console.log(`Created agent: ${agent.name}`);
    }

    // Criar políticas
    for (const policy of INITIAL_POLICIES) {
      await ctx.db.insert("policies", {
        ...policy,
        appliesTo: undefined,
      });
      console.log(`Created policy: ${policy.policyKey}`);
    }

    return {
      seeded: true,
      agentsCreated: INITIAL_AGENTS.length,
      policiesCreated: INITIAL_POLICIES.length,
    };
  },
});
