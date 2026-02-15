"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Activity, CheckCircle2, AlertCircle, PauseCircle } from "lucide-react";
import type { Agent } from "@/types";
import { cn } from "@/lib/utils";

interface AgentCardProps {
  agent: Agent;
  index?: number;
}

const statusConfig = {
  idle: { icon: PauseCircle, label: "Idle", variant: "secondary" as const },
  working: { icon: Activity, label: "Working", variant: "default" as const },
  error: { icon: AlertCircle, label: "Error", variant: "destructive" as const },
  offline: { icon: PauseCircle, label: "Offline", variant: "outline" as const },
};

export function AgentCard({ agent, index = 0 }: AgentCardProps) {
  const status = statusConfig[agent.status];
  const StatusIcon = status.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.05 }}
    >
      <Card className="overflow-hidden">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div
                className="flex h-10 w-10 items-center justify-center rounded-full text-lg"
                style={{ backgroundColor: `${agent.color}20` }}
              >
                {agent.emoji}
              </div>
              <div>
                <CardTitle className="text-base">{agent.name}</CardTitle>
                <p className="text-xs text-muted-foreground">{agent.role}</p>
              </div>
            </div>
            <Badge variant={status.variant} className="gap-1">
              <StatusIcon className="h-3 w-3" />
              {status.label}
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          {agent.status === "working" && agent.currentTask && (
            <div className="space-y-1">
              <p className="text-xs text-muted-foreground truncate">
                {agent.currentTask}
              </p>
              <Progress value={agent.progress} className="h-1" />
            </div>
          )}
          
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <div className="flex items-center gap-1">
              <CheckCircle2 className="h-3 w-3" />
              <span>{agent.tasksCompleted} tasks</span>
            </div>
            <span>Last active: {new Date(agent.lastActive).toLocaleTimeString()}</span>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
