"use client";

import { motion } from "framer-motion";
import { Agent, AGENT_CONFIG } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { 
  Bot, 
  CheckCircle2, 
  AlertCircle, 
  Clock, 
  Zap,
  BarChart3,
  XCircle
} from "lucide-react";

interface AgentGridProps {
  agents: Agent[];
}

const containerVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, scale: 0.95 },
  show: { opacity: 1, scale: 1 },
};

function getStatusIcon(status: string) {
  switch (status) {
    case "working":
      return <Zap className="h-3 w-3 animate-pulse" />;
    case "idle":
      return <Clock className="h-3 w-3" />;
    case "offline":
      return <XCircle className="h-3 w-3" />;
    default:
      return <Bot className="h-3 w-3" />;
  }
}

function getStatusColor(status: string) {
  switch (status) {
    case "working":
      return "bg-yellow-500/10 text-yellow-500 border-yellow-500/20";
    case "idle":
      return "bg-green-500/10 text-green-500 border-green-500/20";
    case "offline":
      return "bg-gray-500/10 text-gray-500 border-gray-500/20";
    default:
      return "bg-blue-500/10 text-blue-500 border-blue-500/20";
  }
}

export function AgentGrid({ agents }: AgentGridProps) {
  const sortedAgents = [...agents].sort((a, b) => {
    // Ralph first, then by status (working > idle > offline)
    if (a.slug === "ralph") return -1;
    if (b.slug === "ralph") return 1;
    const statusOrder = { working: 0, idle: 1, offline: 2 };
    return statusOrder[a.status] - statusOrder[b.status];
  });

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Bot className="h-5 w-5" />
          Agent Swarm
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <ScrollArea className="h-[400px] px-6">
          <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="show"
            className="space-y-3"
          >
            {sortedAgents.map((agent) => {
              const config = AGENT_CONFIG[agent.slug];
              return (
                <motion.div
                  key={agent.slug}
                  variants={itemVariants}
                  className="group relative overflow-hidden rounded-lg border bg-card p-4 transition-colors hover:bg-accent/50"
                >
                  <div className="flex items-start gap-4">
                    <div
                      className="flex h-12 w-12 items-center justify-center rounded-full text-2xl"
                      style={{ backgroundColor: `${config?.color}20` }}
                    >
                      {config?.emoji || "🤖"}
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold">{agent.name}</span>
                        <Badge
                          variant="outline"
                          className={`text-xs ${getStatusColor(agent.status)}`}
                        >
                          {getStatusIcon(agent.status)}
                          <span className="ml-1 capitalize">{agent.status}</span>
                        </Badge>
                      </div>

                      <p className="text-sm text-muted-foreground capitalize">
                        {config?.role || agent.role}
                      </p>

                      {agent.currentTask && (
                        <div className="mt-2 text-xs text-muted-foreground truncate">
                          <span className="font-medium">Current:</span>{" "}
                          {agent.currentTask}
                        </div>
                      )}
                    </div>

                    <div className="flex flex-col items-end gap-1 text-xs text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <CheckCircle2 className="h-3 w-3 text-green-500" />
                        <span>{agent.tasksCompleted}</span>
                      </div>
                      {agent.tasksFailed > 0 && (
                        <div className="flex items-center gap-1">
                          <AlertCircle className="h-3 w-3 text-red-500" />
                          <span>{agent.tasksFailed}</span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Progress bar for working agents */}
                  {agent.status === "working" && (
                    <div className="absolute bottom-0 left-0 right-0 h-1 bg-muted">
                      <motion.div
                        className="h-full bg-yellow-500"
                        initial={{ width: "0%" }}
                        animate={{ width: ["0%", "100%", "0%"] }}
                        transition={{
                          duration: 2,
                          repeat: Infinity,
                          ease: "linear",
                        }}
                      />
                    </div>
                  )}
                </motion.div>
              );
            })}
          </motion.div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
