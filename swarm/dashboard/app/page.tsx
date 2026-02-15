"use client";

import { useQuery, useMutation } from "convex/react";
import { api } from "../convex/_generated/api";
import { motion } from "framer-motion";

import { Header } from "@/components/header";
import { TaskCreator } from "@/components/task-creator";
import { StatsCard } from "@/components/stats-card";
import { AgentCard } from "@/components/agent-card";
import { ActivityFeed } from "@/components/activity-feed";
import { TaskList } from "@/components/task-list";
import { CostChart } from "@/components/cost-chart";

import {
  Activity,
  CheckCircle2,
  DollarSign,
  Users,
  Cpu,
  AlertCircle,
} from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function Dashboard() {
  const stats = useQuery(api.stats.getDashboardStats);
  const agents = useQuery(api.agents.list);
  const costs = useQuery(api.costs.stats);
  const createTask = useMutation(api.tasks.create);

  const handleTaskSubmit = async (taskTitle: string, priority: string) => {
    await createTask({
      title: taskTitle,
      description: taskTitle,
      priority: priority as "low" | "medium" | "high",
    });
  };

  const agentStats = costs?.agentStats
    ? Object.entries(costs.agentStats).map(([agent, data]) => ({
        agent,
        cost: data.cost,
        tokens: data.tokens,
      }))
    : [];

  return (
    <div className="min-h-screen bg-background">
      <Header isConnected={!!stats} />
      
      <main className="container mx-auto px-4 py-6 space-y-6">
        {/* Task Creator */}
        <TaskCreator onSubmit={handleTaskSubmit} />

        {/* Stats Grid */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.4, delay: 0.1 }}
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4"
        >
          <StatsCard
            title="Total Tasks"
            value={stats?.tasks.total || 0}
            icon={Activity}
            index={0}
            color="#3b82f6"
          />
          <StatsCard
            title="Completed"
            value={stats?.tasks.completed || 0}
            icon={CheckCircle2}
            index={1}
            color="#22c55e"
          />
          <StatsCard
            title="Active Agents"
            value={stats?.agents.active || 0}
            icon={Users}
            index={2}
            color="#a855f7"
          />
          <StatsCard
            title="Total Cost"
            value={stats?.costs.total || 0}
            icon={DollarSign}
            formatter="currency"
            index={3}
            color="#ef4444"
          />
        </motion.div>

        {/* Tabs for different views */}
        <Tabs defaultValue="overview" className="space-y-4">
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="agents">Agents</TabsTrigger>
            <TabsTrigger value="tasks">Tasks</TabsTrigger>
            <TabsTrigger value="costs">Costs</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <ActivityFeed logs={stats?.costs.recent || []} />
              <TaskList tasks={stats?.recentTasks || []} />
            </div>
            <CostChart data={agentStats} />
          </TabsContent>

          <TabsContent value="agents" className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {agents?.map((agent, index) => (
                <AgentCard
                  key={agent._id}
                  agent={{
                    id: agent._id,
                    name: agent.name,
                    slug: agent.slug,
                    role: agent.role,
                    status: agent.status,
                    emoji: agent.emoji,
                    color: agent.color,
                    lastActive: agent.lastActive,
                    tasksCompleted: agent.tasksCompleted,
                    currentTask: agent.currentTask,
                    progress: agent.progress,
                  }}
                  index={index}
                />
              ))}
            </div>
          </TabsContent>

          <TabsContent value="tasks" className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              <div className="lg:col-span-2">
                <TaskList tasks={stats?.recentTasks || []} />
              </div>
              <div className="space-y-4">
                <StatsCard
                  title="Running"
                  value={stats?.tasks.running || 0}
                  icon={Cpu}
                  color="#3b82f6"
                />
                <StatsCard
                  title="Pending"
                  value={stats?.tasks.pending || 0}
                  icon={Activity}
                  color="#f59e0b"
                />
                <StatsCard
                  title="Failed"
                  value={stats?.tasks.failed || 0}
                  icon={AlertCircle}
                  color="#ef4444"
                />
              </div>
            </div>
          </TabsContent>

          <TabsContent value="costs" className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <CostChart data={agentStats} />
              <div className="space-y-4">
                {costs?.modelStats &&
                  Object.entries(costs.modelStats).map(([model, data]) => (
                    <motion.div
                      key={model}
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      className="p-4 rounded-lg bg-card border"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-medium">{model}</span>
                        <span className="text-sm text-muted-foreground">
                          {data.count} calls
                        </span>
                      </div>
                      <div className="mt-2 text-2xl font-bold">
                        ${data.cost.toFixed(4)}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {data.tokens.toLocaleString()} tokens
                      </div>
                    </motion.div>
                  ))}
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
