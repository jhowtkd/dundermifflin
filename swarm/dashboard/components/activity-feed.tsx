"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { getAgentEmoji, formatDuration } from "@/lib/utils";
import type { CostEntry } from "@/types";
import { Activity, Clock, DollarSign, CheckCircle2, XCircle } from "lucide-react";

interface ActivityFeedProps {
  logs: CostEntry[];
}

export function ActivityFeed({ logs }: ActivityFeedProps) {
  return (
    <Card className="h-[400px]">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base flex items-center gap-2">
            <Activity className="h-4 w-4" />
            Live Activity
          </CardTitle>
          <div className="flex items-center gap-2">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
            </span>
            <span className="text-xs text-muted-foreground">Live</span>
          </div>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <ScrollArea className="h-[320px] px-6">
          <AnimatePresence initial={false}>
            {logs.length === 0 ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex flex-col items-center justify-center h-40 text-muted-foreground"
              >
                <Activity className="h-8 w-8 mb-2 opacity-50" />
                <p className="text-sm">No recent activity</p>
              </motion.div>
            ) : (
              <div className="space-y-3">
                {logs.map((log, index) => (
                  <motion.div
                    key={`${log.timestamp}-${index}`}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    transition={{ duration: 0.2, delay: index * 0.03 }}
                    className="flex items-start gap-3 p-3 rounded-lg bg-muted/50 hover:bg-muted transition-colors"
                  >
                    <div className="text-lg">{getAgentEmoji(log.agent)}</div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-sm capitalize">
                          {log.agent}
                        </span>
                        <Badge
                          variant={log.success ? "success" : "destructive"}
                          className="text-[10px] h-4 px-1"
                        >
                          {log.success ? (
                            <CheckCircle2 className="h-2 w-2 mr-0.5" />
                          ) : (
                            <XCircle className="h-2 w-2 mr-0.5" />
                          )}
                          {log.success ? "Success" : "Failed"}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-3 mt-1 text-xs text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <DollarSign className="h-3 w-3" />
                          ${log.costUsd.toFixed(4)}
                        </span>
                        <span className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          {formatDuration(log.durationMs)}
                        </span>
                        <span>{log.tokensIn + log.tokensOut} tokens</span>
                      </div>
                      <p className="text-[10px] text-muted-foreground mt-1">
                        {new Date(log.timestamp).toLocaleTimeString()} · {log.model}
                      </p>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </AnimatePresence>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
