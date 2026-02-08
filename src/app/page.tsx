"use client";

import { useQuery, useMutation } from "convex/react";
import { api } from "../../convex/_generated/api";
import { useState } from "react";
import { ConvexClientProvider } from "../components/ConvexProvider";

function DashboardContent() {
  const stats = useQuery(api.agents.getDashboardStats);
  const agents = useQuery(api.agents.listAgents);
  const recentEvents = useQuery(api.agents.getRecentEvents, { hours: 24 });
  const proposals = useQuery(api.agents.listProposals, {});
  const [activeTab, setActiveTab] = useState("overview");

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header - Mobile Responsive */}
      <header className="bg-gray-800 border-b border-gray-700 p-3 md:p-4">
        <div className="max-w-7xl mx-auto">
          {/* Logo e Título */}
          <div className="flex items-center gap-2 md:gap-3 mb-3">
            <span className="text-2xl md:text-3xl">📄</span>
            <div>
              <h1 className="text-xl md:text-2xl font-bold">Dunder Mifflin</h1>
              <p className="text-gray-400 text-xs md:text-sm hidden sm:block">Sistema Multi-Agente de IA</p>
            </div>
          </div>
          
          {/* Navegação - Scroll horizontal no mobile */}
          <div className="flex gap-1 md:gap-2 overflow-x-auto pb-2 scrollbar-hide">
            {["overview", "agents", "proposals", "missions", "events"].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-3 py-1.5 md:px-4 md:py-2 rounded-lg capitalize text-sm md:text-base whitespace-nowrap ${
                  activeTab === tab
                    ? "bg-blue-600 text-white"
                    : "bg-gray-700 text-gray-300 hover:bg-gray-600"
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>
      </header>

      {/* Content - Mobile Responsive */}
      <main className="max-w-7xl mx-auto p-3 md:p-6">
        {activeTab === "overview" && (
          <div className="space-y-4 md:space-y-6">
            {/* Stats Cards - 2 cols mobile, 4 cols desktop */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 md:gap-4">
              <StatCard
                title="Agentes Ativos"
                value={stats?.activeAgents || 0}
                total={stats?.totalAgents || 0}
                icon="🤖"
                color="blue"
              />
              <StatCard
                title="Missões em Execução"
                value={stats?.runningMissions || 0}
                icon="🚀"
                color="yellow"
              />
              <StatCard
                title="Concluídas"
                value={stats?.completedMissions || 0}
                icon="✅"
                color="green"
              />
              <StatCard
                title="Falhas"
                value={stats?.failedMissions || 0}
                icon="❌"
                color="red"
              />
            </div>

            {/* Recent Events */}
            <div className="bg-gray-800 rounded-lg p-4 md:p-6">
              <h2 className="text-lg md:text-xl font-bold mb-3 md:mb-4">Eventos Recentes (24h)</h2>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {recentEvents?.slice(0, 10).map((event) => (
                  <div
                    key={event._id}
                    className="flex items-center gap-2 md:gap-3 p-2 md:p-3 bg-gray-700 rounded-lg"
                  >
                    <span className="text-xl md:text-2xl shrink-0">
                      {getEventIcon(event.eventType)}
                    </span>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-sm md:text-base truncate">{event.title}</p>
                      <p className="text-xs md:text-sm text-gray-400">
                        {new Date(event.occurredAt).toLocaleString("pt-BR")}
                      </p>
                    </div>
                    <span
                      className={`px-1.5 py-0.5 md:px-2 md:py-1 rounded text-xs shrink-0 ${
                        event.severity === "error" || event.severity === "critical"
                          ? "bg-red-600"
                          : event.severity === "warning"
                          ? "bg-yellow-600"
                          : "bg-blue-600"
                      }`}
                    >
                      {event.severity}
                    </span>
                  </div>
                )) || <p className="text-gray-400">Nenhum evento recente</p>}
              </div>
            </div>
          </div>
        )}

        {activeTab === "agents" && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 md:gap-4">
            {agents?.map((agent) => (
              <AgentCard key={agent._id} agent={agent} />
            )) || <p>Carregando agentes...</p>}
          </div>
        )}

        {activeTab === "proposals" && <ProposalsTab />}
        {activeTab === "missions" && <MissionsTab />}
        {activeTab === "events" && <EventsTab />}
      </main>
    </div>
  );
}

function StatCard({ title, value, total, icon, color }: any) {
  const colors: Record<string, string> = {
    blue: "bg-blue-600",
    green: "bg-green-600",
    yellow: "bg-yellow-600",
    red: "bg-red-600",
  };

  return (
    <div className={`${colors[color]} bg-opacity-20 border border-${color}-500 rounded-lg p-2 md:p-4`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-400 text-xs md:text-sm truncate">{title}</p>
          <p className="text-xl md:text-3xl font-bold">
            {value}
            {total !== undefined && (
              <span className="text-sm md:text-lg text-gray-400">/{total}</span>
            )}
          </p>
        </div>
        <span className="text-2xl md:text-4xl">{icon}</span>
      </div>
    </div>
  );
}

function AgentCard({ agent }: { agent: any }) {
  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg p-3 md:p-4">
      <div className="flex items-start gap-3 md:gap-4">
        <span className="text-3xl md:text-4xl">{agent.avatarUrl || "🤖"}</span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2">
            <div className="min-w-0">
              <h3 className="text-base md:text-lg font-bold truncate">{agent.name}</h3>
              <p className="text-blue-400 text-xs md:text-sm truncate">{agent.role}</p>
            </div>
            <span
              className={`px-2 py-1 rounded text-xs whitespace-nowrap ${
                agent.isActive ? "bg-green-600" : "bg-gray-600"
              }`}
            >
              {agent.isActive ? "Ativo" : "Inativo"}
            </span>
          </div>
          <p className="text-gray-400 text-xs md:text-sm mt-2 line-clamp-2">{agent.description}</p>
          <div className="mt-2 md:mt-3 flex flex-wrap gap-1 md:gap-2">
            {agent.capabilities?.slice(0, 3).map((cap: string) => (
              <span
                key={cap}
                className="px-1.5 py-0.5 md:px-2 md:py-1 bg-gray-700 rounded text-xs text-gray-300"
              >
                {cap}
              </span>
            ))}
            {agent.capabilities?.length > 3 && (
              <span className="px-1.5 py-0.5 text-xs text-gray-500">+{agent.capabilities.length - 3}</span>
            )}
          </div>
          <div className="mt-2 md:mt-3 text-xs md:text-sm text-gray-400">
            Quota: {agent.quotaUsed || 0}/{agent.dailyQuota}
          </div>
        </div>
      </div>
    </div>
  );
}

function getEventIcon(type: string): string {
  const icons: Record<string, string> = {
    mission_proposed: "📋",
    mission_started: "🚀",
    mission_completed: "✅",
    mission_failed: "❌",
    step_started: "▶️",
    step_completed: "☑️",
    step_failed: "⚠️",
    trigger_fired: "🔫",
    reaction_queued: "📥",
    reaction_executed: "⚡",
    insight_created: "💡",
    memory_stored: "🧠",
    tweet_drafted: "📝",
    tweet_posted: "📱",
    system_alert: "🔔",
    agent_communication: "💬",
  };
  return icons[type] || "📌";
}

function MissionsTab() {
  const missions = useQuery(api.agents.listMissions, { status: "running" });
  
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">Missões em Execução</h2>
      {missions?.map((mission) => (
        <div key={mission._id} className="bg-gray-800 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-bold">{mission.title}</h3>
              <p className="text-sm text-gray-400">{mission.missionCode}</p>
            </div>
            <span className="px-3 py-1 bg-yellow-600 rounded-full text-sm">
              {mission.status}
            </span>
          </div>
        </div>
      )) || <p className="text-gray-400">Nenhuma missão em execução</p>}
    </div>
  );
}

function EventsTab() {
  const events = useQuery(api.agents.listEvents, { limit: 50 });
  
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">Todos os Eventos</h2>
      <div className="space-y-2">
        {events?.map((event) => (
          <div key={event._id} className="bg-gray-800 rounded-lg p-4">
            <div className="flex items-center gap-3">
              <span className="text-2xl">{getEventIcon(event.eventType)}</span>
              <div className="flex-1">
                <p className="font-medium">{event.title}</p>
                <p className="text-sm text-gray-400">{event.eventType}</p>
              </div>
              <span className="text-sm text-gray-500">
                {new Date(event.occurredAt).toLocaleString("pt-BR")}
              </span>
            </div>
          </div>
        )) || <p className="text-gray-400">Nenhum evento</p>}
      </div>
    </div>
  );
}

function ProposalsTab() {
  const proposals = useQuery(api.agents.listProposals, {});
  const agents = useQuery(api.agents.listAgents);
  const createProposal = useMutation(api.agents.createProposal);
  const reviewProposal = useMutation(api.agents.reviewProposal);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    agentId: "",
    priority: 5,
    missionType: "general"
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.agentId) return;
    
    await createProposal({
      agentId: formData.agentId as any,
      title: formData.title,
      description: formData.description,
      missionType: formData.missionType,
      priority: formData.priority,
    });
    
    setFormData({ title: "", description: "", agentId: "", priority: 5, missionType: "general" });
    setShowForm(false);
  };

  const handleReview = async (id: string, status: "accepted" | "rejected") => {
    await reviewProposal({ id: id as any, status });
  };

  return (
    <div className="space-y-3 md:space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <h2 className="text-lg md:text-xl font-bold">Propostas de Missão</h2>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-3 md:px-4 py-1.5 md:py-2 bg-green-600 hover:bg-green-700 rounded-lg text-sm md:text-base"
        >
          {showForm ? "Cancelar" : "+ Nova Proposta"}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="bg-gray-800 rounded-lg p-3 md:p-4 space-y-3 md:space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">Título</label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="w-full px-3 py-2 bg-gray-700 rounded-lg text-white text-sm md:text-base"
              placeholder="Ex: Criar post sobre produtividade"
              required
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">Descrição</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-3 py-2 bg-gray-700 rounded-lg text-white h-20 text-sm md:text-base"
              placeholder="Detalhes da missão..."
            />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 md:gap-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1">Agente</label>
              <select
                value={formData.agentId}
                onChange={(e) => setFormData({ ...formData, agentId: e.target.value })}
                className="w-full px-3 py-2 bg-gray-700 rounded-lg text-white text-sm md:text-base"
                required
              >
                <option value="">Selecione...</option>
                {agents?.map((agent) => (
                  <option key={agent._id} value={agent._id}>
                    {agent.name} ({agent.role})
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Tipo</label>
              <select
                value={formData.missionType}
                onChange={(e) => setFormData({ ...formData, missionType: e.target.value })}
                className="w-full px-3 py-2 bg-gray-700 rounded-lg text-white text-sm md:text-base"
              >
                <option value="general">Geral</option>
                <option value="content">Conteúdo</option>
                <option value="research">Pesquisa</option>
                <option value="social">Social Media</option>
              </select>
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Prioridade (1-10)</label>
              <input
                type="number"
                min={1}
                max={10}
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: parseInt(e.target.value) })}
                className="w-full px-3 py-2 bg-gray-700 rounded-lg text-white text-sm md:text-base"
              />
            </div>
          </div>
          <button type="submit" className="px-4 md:px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm md:text-base">
            Criar Proposta
          </button>
        </form>
      )}

      <div className="space-y-2">
        {proposals?.map((proposal) => (
          <div key={proposal._id} className="bg-gray-800 rounded-lg p-3 md:p-4">
            <div className="flex flex-col md:flex-row md:items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <h3 className="font-bold text-sm md:text-base truncate">{proposal.title}</h3>
                  <span className={`px-2 py-0.5 rounded text-xs ${
                    proposal.status === "pending" ? "bg-yellow-600" :
                    proposal.status === "accepted" ? "bg-green-600" : "bg-red-600"
                  }`}>
                    {proposal.status}
                  </span>
                </div>
                <p className="text-xs md:text-sm text-gray-400 mt-1">{proposal.proposalCode}</p>
                {proposal.description && (
                  <p className="text-xs md:text-sm text-gray-300 mt-2 line-clamp-2">{proposal.description}</p>
                )}
                <div className="flex flex-wrap gap-2 md:gap-4 mt-2 text-xs md:text-sm text-gray-400">
                  <span>🎯 Prioridade: {proposal.priority}/10</span>
                  <span>📁 Tipo: {proposal.missionType}</span>
                </div>
              </div>
              {proposal.status === "pending" && (
                <div className="flex gap-2 shrink-0">
                  <button
                    onClick={() => handleReview(proposal._id, "accepted")}
                    className="px-2 md:px-3 py-1 bg-green-600 hover:bg-green-700 rounded text-xs md:text-sm"
                  >
                    ✅ Aprovar
                  </button>
                  <button
                    onClick={() => handleReview(proposal._id, "rejected")}
                    className="px-2 md:px-3 py-1 bg-red-600 hover:bg-red-700 rounded text-xs md:text-sm"
                  >
                    ❌ Rejeitar
                  </button>
                </div>
              )}
            </div>
          </div>
        )) || <p className="text-gray-400">Nenhuma proposta</p>}
      </div>
    </div>
  );
}

export default function Dashboard() {
  return (
    <ConvexClientProvider>
      <DashboardContent />
    </ConvexClientProvider>
  );
}
