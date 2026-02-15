"use client";

import { motion } from "framer-motion";
import { Terminal, Activity, Zap } from "lucide-react";
import { Badge } from "./ui/badge";

interface DashboardHeaderProps {
  agentCount: number;
  activeMissions: number;
  onlineAgents: number;
}

export function DashboardHeader({
  agentCount,
  activeMissions,
  onlineAgents,
}: DashboardHeaderProps) {
  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className="border-b border-border/50 bg-gradient-to-r from-background via-card to-background"
    >
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          {/* Logo & Title */}
          <div className="flex items-center gap-4">
            <div className="relative">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center">
                <Terminal className="w-6 h-6 text-white" />
              </div>
              <motion.div
                className="absolute inset-0 rounded-xl bg-cyan-500/30 blur-xl"
                animate={{ scale: [1, 1.2, 1], opacity: [0.5, 0.8, 0.5] }}
                transition={{ duration: 3, repeat: Infinity }}
              />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gradient">
                Mission Control
              </h1>
              <p className="text-sm text-muted-foreground">
                OpenClaw AI Agent System
              </p>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              <span className="text-sm text-muted-foreground">
                <span className="text-foreground font-medium">{onlineAgents}</span> online
              </span>
            </div>
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-cyan-400" />
              <span className="text-sm text-muted-foreground">
                <span className="text-foreground font-medium">{activeMissions}</span> active
              </span>
            </div>
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-yellow-400" />
              <span className="text-sm text-muted-foreground">
                <span className="text-foreground font-medium">{agentCount}</span> agents
              </span>
            </div>
            <Badge variant="outline" className="ml-4">
              v2.0.0
            </Badge>
          </div>
        </div>
      </div>
    </motion.header>
  );
}
