"use client";

import { motion } from "framer-motion";
import { Activity, Cpu, MemoryStick, Clock } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { getStatusColor, formatDuration } from "@/lib/utils";

interface Agent {
  _id: string;
  name: string;
  status: "online" | "busy" | "offline" | "error";
  type: string;
  lastSeen: number;
  currentTask?: string;
}

interface AgentStatusCardProps {
  agent: Agent;
  index: number;
}

export function AgentStatusCard({ agent, index }: AgentStatusCardProps) {
  const statusColor = getStatusColor(agent.status);
  const isOnline = agent.status === "online" || agent.status === "busy";
  const lastSeenAgo = Date.now() - agent.lastSeen;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05, duration: 0.3 }}
    >
      <Card className="relative overflow-hidden border-border/50 bg-gradient-to-br from-card to-card/50 hover:border-primary/30 transition-all duration-300 group">
        {/* Status indicator glow */}
        <div
          className="absolute top-0 right-0 w-32 h-32 opacity-10 blur-3xl rounded-full -translate-y-1/2 translate-x-1/2 group-hover:opacity-20 transition-opacity"
          style={{ backgroundColor: statusColor }}
        />
        
        <CardHeader className="pb-2">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div className="relative">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: statusColor }}
                />
                {isOnline && (
                  <motion.div
                    className="absolute inset-0 rounded-full"
                    style={{ backgroundColor: statusColor }}
                    animate={{ scale: [1, 1.5, 1], opacity: [0.5, 0, 0.5] }}
                    transition={{ duration: 2, repeat: Infinity }}
                  />
                )}
              </div>
              <div>
                <CardTitle className="text-base font-medium">{agent.name}</CardTitle>
                <p className="text-xs text-muted-foreground">{agent.type}</p>
              </div>
            </div>
            <Badge
              variant={
                agent.status === "online"
                  ? "success"
                  : agent.status === "busy"
                  ? "info"
                  : agent.status === "error"
                  ? "destructive"
                  : "secondary"
              }
            >
              {agent.status}
            </Badge>
          </div>
        </CardHeader>

        <CardContent className="space-y-3">
          {agent.currentTask && (
            <div className="text-sm">
              <span className="text-muted-foreground">Current Task:</span>
              <p className="text-foreground truncate mt-0.5">{agent.currentTask}</p>
            </div>
          )}

          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="flex items-center gap-1.5 text-muted-foreground">
              <Clock className="w-3.5 h-3.5" />
              <span>{formatDuration(lastSeenAgo)} ago</span>
            </div>
            <div className="flex items-center gap-1.5 text-muted-foreground">
              <Activity className="w-3.5 h-3.5" />
              <span>{isOnline ? "Active" : "Inactive"}</span>
            </div>
          </div>

          {/* Mini metrics visualization */}
          <div className="flex gap-1 pt-1">
            {[...Array(5)].map((_, i) => (
              <div
                key={i}
                className="flex-1 h-1 rounded-full bg-muted"
                style={{
                  backgroundColor: isOnline ? statusColor : undefined,
                  opacity: isOnline ? 0.3 + i * 0.15 : 0.2,
                }}
              />
            ))}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
