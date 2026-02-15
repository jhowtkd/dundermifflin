"use client";

import { motion } from "framer-motion";
import { SwarmState, Agent, AGENT_CONFIG } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  Cpu, 
  Users, 
  Target, 
  Activity,
  Zap,
  Timer
} from "lucide-react";

interface SwarmStatusProps {
  swarmState: SwarmState | null;
  agents: Agent[];
}

export function SwarmStatus({ swarmState, agents }: SwarmStatusProps) {
  const activeAgents = agents.filter((a) => a.status !== "offline");
  const workingAgents = agents.filter((a) => a.status === "working");
  
  const uptime = swarmState?.startedAt 
    ? Math.floor((Date.now() - swarmState.startedAt) / 1000 / 60) 
    : 0;
  
  const hours = Math.floor(uptime / 60);
  const minutes = uptime % 60;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
    >
      <Card className={`${swarmState?.isActive ? 'border-yellow-500/30' : ''}`}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Cpu className="h-5 w-5" />
            Swarm Status
            {swarmState?.isActive && (
              <Badge className="ml-auto bg-yellow-500/20 text-yellow-500 border-yellow-500/30 animate-pulse">
                <Zap className="h-3 w-3 mr-1" />
                Active
              </Badge>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {swarmState?.currentMission && (
            <div className="p-3 rounded-lg bg-muted">
              <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
                <Target className="h-4 w-4" />
                Current Mission
              </div>
              <p className="font-medium">{swarmState.currentMission}</p>
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div className="p-3 rounded-lg bg-muted">
              <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
                <Users className="h-4 w-4" />
                Active Agents
              </div>
              <div className="text-2xl font-bold">{activeAgents.length}</div>
              <div className="text-xs text-muted-foreground">
                {workingAgents.length} working
              </div>
            </div>

            <div className="p-3 rounded-lg bg-muted">
              <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
                <Timer className="h-4 w-4" />
                Uptime
              </div>
              <div className="text-2xl font-bold">
                {hours > 0 ? `${hours}h ${minutes}m` : `${minutes}m`}
              </div>
              <div className="text-xs text-muted-foreground">
                Since last restart
              </div>
            </div>
          </div>

          {swarmState?.participatingAgents && swarmState.participatingAgents.length > 0 && (
            <div>
              <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
                <Activity className="h-4 w-4" />
                Participating Agents
              </div>
              <div className="flex flex-wrap gap-2">
                {swarmState.participatingAgents.map((slug) => {
                  const config = AGENT_CONFIG[slug];
                  return (
                    <Badge key={slug} variant="secondary" className="gap-1">
                      <span>{config?.emoji || "🤖"}</span>
                      <span>{config?.name || slug}</span>
                    </Badge>
                  );
                })}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
