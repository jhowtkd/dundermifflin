"use client";

import { motion } from "framer-motion";
import { Activity, Cpu, Zap } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface HeaderProps {
  isConnected: boolean;
}

export function Header({ isConnected }: HeaderProps) {
  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60"
    >
      <div className="container flex h-16 items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-gradient-to-br from-yellow-500/20 to-amber-600/20 border border-yellow-500/30">
            <span className="text-2xl">🐝</span>
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-yellow-500 to-amber-500 bg-clip-text text-transparent">
              OpenClaw Mission Control
            </h1>
            <p className="text-xs text-muted-foreground">
              Ralph Swarm v5.0 — Autonomous Agent System
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="hidden md:flex items-center gap-2 text-sm text-muted-foreground">
            <Cpu className="h-4 w-4" />
            <span>Mac Mini M4</span>
            <span className="text-border">|</span>
            <Zap className="h-4 w-4 text-yellow-500" />
            <span>24/7 Active</span>
          </div>

          <Badge
            variant={isConnected ? "default" : "destructive"}
            className="gap-1.5"
          >
            <Activity className="h-3 w-3" />
            <span className="relative flex h-2 w-2">
              {isConnected && (
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75" />
              )}
              <span
                className={`relative inline-flex rounded-full h-2 w-2 ${
                  isConnected ? "bg-green-500" : "bg-red-500"
                }`}
              />
            </span>
            {isConnected ? "Live" : "Offline"}
          </Badge>
        </div>
      </div>
    </motion.header>
  );
}
