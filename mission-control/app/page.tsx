"use client";

import { motion } from "framer-motion";
import { useQuery } from "convex/react";
import { api } from "@/convex/_generated/api";
import { DashboardHeader } from "@/components/dashboard-header";
import { AgentStatusCard } from "@/components/agent-status-card";
import { MissionCard } from "@/components/mission-card";
import { LogStream } from "@/components/log-stream";
import { StatsOverview } from "@/components/stats-overview";
import { CronJobsPanel } from "@/components/cron-jobs-panel";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Bot, 
  Rocket, 
  Terminal, 
  Clock,
  Activity,
  FileText,
  AlertCircle
} from "lucide-react";

export default function Dashboard() {
  const agents = useQuery(api.agents.list) ?? [];
  const missions = useQuery(api.missions.list) ?? [];
  const logs = useQuery(api.logs.list, { limit: 50 }) ?? [];
  const cronJobs = useQuery(api.cronJobs.list) ?? [];

  const onlineAgents = agents.filter((a) => a.status === "online" || a.status === "busy").length;
  const activeMissions = missions.filter((m) => m.status === "running").length;
  const pendingMissions = missions.filter((m) => m.status === "pending").length;
  const completedMissions = missions.filter((m) => m.status === "completed").length;
  const failedMissions = missions.filter((m) => m.status === "failed").length;

  const recentMissions = missions.slice(0, 10);
  const recentAgents = agents.slice(0, 8);

  return (
    <div className="min-h-screen bg-background">
      <DashboardHeader
        agentCount={agents.length}
        activeMissions={activeMissions}
        onlineAgents={onlineAgents}
      />

      <main className="container mx-auto px-4 py-6 space-y-6">
        {/* Stats Overview */}
        <StatsOverview
          totalAgents={agents.length}
          onlineAgents={onlineAgents}
          activeMissions={activeMissions}
          pendingMissions={pendingMissions}
          completedMissions={completedMissions}
          failedMissions={failedMissions}
        />

        {/* Main Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Agents & Missions */}
          <div className="lg:col-span-2 space-y-6">
            <Tabs defaultValue="missions" className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="missions" className="gap-2">
                  <Rocket className="w-4 h-4" />
                  Missions
                </TabsTrigger>
                <TabsTrigger value="agents" className="gap-2">
                  <Bot className="w-4 h-4" />
                  Agents
                </TabsTrigger>
              </TabsList>

              <TabsContent value="missions" className="space-y-4 mt-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold">Recent Missions</h2>
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className="text-sm text-primary hover:underline"
                  >
                    View All
                  </motion.button>
                </div>
                
                {recentMissions.length === 0 ? (
                  <Card className="border-dashed">
                    <CardContent className="flex flex-col items-center justify-center py-12 text-center">
                      <Rocket className="w-12 h-12 text-muted-foreground/50 mb-4" />
                      <p className="text-muted-foreground">No missions yet</p>
                      <p className="text-sm text-muted-foreground/70 mt-1">
                        Create your first mission to get started
                      </p>
                    </CardContent>
                  </Card>
                ) : (
                  <div className="grid gap-3">
                    {recentMissions.map((mission, index) => (
                      <MissionCard key={mission._id} mission={mission} index={index} />
                    ))}
                  </div>
                )}
              </TabsContent>

              <TabsContent value="agents" className="space-y-4 mt-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold">Agent Status</h2>
                  <div className="flex gap-2 text-sm">
                    <span className="flex items-center gap-1 text-green-400">
                      <span className="w-2 h-2 rounded-full bg-green-400" />
                      {onlineAgents} online
                    </span>
                    <span className="flex items-center gap-1 text-muted-foreground">
                      <span className="w-2 h-2 rounded-full bg-muted-foreground" />
                      {agents.length - onlineAgents} offline
                    </span>
                  </div>
                </div>

                {recentAgents.length === 0 ? (
                  <Card className="border-dashed">
                    <CardContent className="flex flex-col items-center justify-center py-12 text-center">
                      <Bot className="w-12 h-12 text-muted-foreground/50 mb-4" />
                      <p className="text-muted-foreground">No agents connected</p>
                      <p className="text-sm text-muted-foreground/70 mt-1">
                        Agents will appear here when they connect
                      </p>
                    </CardContent>
                  </Card>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {recentAgents.map((agent, index) => (
                      <AgentStatusCard key={agent._id} agent={agent} index={index} />
                    ))}
                  </div>
                )}
              </TabsContent>
            </Tabs>

            {/* Cron Jobs Section */}
            <CronJobsPanel jobs={cronJobs} />
          </div>

          {/* Right Column - Logs & System Info */}
          <div className="space-y-6">
            {/* Live Log Stream */}
            <Card className="border-border/50">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm font-medium flex items-center gap-2">
                    <Terminal className="w-4 h-4 text-cyan-400" />
                    Live Logs
                  </CardTitle>
                  <div className="flex items-center gap-2">
                    <span className="relative flex h-2 w-2">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                    </span>
                    <span className="text-xs text-muted-foreground">LIVE</span>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <LogStream logs={logs} />
              </CardContent>
            </Card>

            {/* System Status */}
            <Card className="border-border/50">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Activity className="w-4 h-4 text-purple-400" />
                  System Status
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">API Status</span>
                    <span className="text-green-400 flex items-center gap-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-green-400" />
                      Operational
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Database</span>
                    <span className="text-green-400 flex items-center gap-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-green-400" />
                      Connected
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">WebSocket</span>
                    <span className="text-green-400 flex items-center gap-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-green-400" />
                      Active
                    </span>
                  </div>
                </div>

                <div className="pt-2 border-t border-border/50">
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <Clock className="w-3.5 h-3.5" />
                    <span>Last updated: {new Date().toLocaleTimeString()}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card className="border-border/50">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="w-full flex items-center gap-3 p-3 rounded-lg bg-secondary/50 hover:bg-secondary transition-colors text-left"
                >
                  <div className="w-8 h-8 rounded-lg bg-cyan-500/20 flex items-center justify-center">
                    <Rocket className="w-4 h-4 text-cyan-400" />
                  </div>
                  <div>
                    <p className="text-sm font-medium">New Mission</p>
                    <p className="text-xs text-muted-foreground">Create a new AI mission</p>
                  </div>
                </motion.button>

                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="w-full flex items-center gap-3 p-3 rounded-lg bg-secondary/50 hover:bg-secondary transition-colors text-left"
                >
                  <div className="w-8 h-8 rounded-lg bg-purple-500/20 flex items-center justify-center">
                    <FileText className="w-4 h-4 text-purple-400" />
                  </div>
                  <div>
                    <p className="text-sm font-medium">View Logs</p>
                    <p className="text-xs text-muted-foreground">Check system logs</p>
                  </div>
                </motion.button>

                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="w-full flex items-center gap-3 p-3 rounded-lg bg-secondary/50 hover:bg-secondary transition-colors text-left"
                >
                  <div className="w-8 h-8 rounded-lg bg-yellow-500/20 flex items-center justify-center">
                    <AlertCircle className="w-4 h-4 text-yellow-400" />
                  </div>
                  <div>
                    <p className="text-sm font-medium">System Health</p>
                    <p className="text-xs text-muted-foreground">Run diagnostics</p>
                  </div>
                </motion.button>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-border/50 mt-12">
        <div className="container mx-auto px-4 py-6">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm text-muted-foreground">
              OpenClaw AI Agent System — Running on Mac Mini M4
            </p>
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <span>Convex Real-time</span>
              <span>•</span>
              <span>Next.js 15</span>
              <span>•</span>
              <span>Tailwind v4</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
