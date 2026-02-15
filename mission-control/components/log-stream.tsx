"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Info, AlertTriangle, AlertCircle, Bug } from "lucide-react";
import { formatTimestamp, getStatusColor } from "@/lib/utils";

interface Log {
  _id: string;
  level: "info" | "warn" | "error" | "debug";
  message: string;
  source: string;
  timestamp: number;
  agentId?: string;
  missionId?: string;
}

interface LogStreamProps {
  logs: Log[];
}

const levelIcons = {
  info: <Info className="w-4 h-4" />,
  warn: <AlertTriangle className="w-4 h-4" />,
  error: <AlertCircle className="w-4 h-4" />,
  debug: <Bug className="w-4 h-4" />,
};

const levelColors = {
  info: "#00d4ff",
  warn: "#ffaa00",
  error: "#ef4444",
  debug: "#64748b",
};

export function LogStream({ logs }: LogStreamProps) {
  return (
    <div className="space-y-1 max-h-[400px] overflow-y-auto font-mono text-sm">
      <AnimatePresence initial={false}>
        {logs.map((log, index) => (
          <motion.div
            key={log._id}
            initial={{ opacity: 0, x: -20, height: 0 }}
            animate={{ opacity: 1, x: 0, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="flex items-start gap-3 py-1.5 px-2 rounded hover:bg-white/5 group"
          >
            <span
              className="flex-shrink-0 mt-0.5"
              style={{ color: levelColors[log.level] }}
            >
              {levelIcons[log.level]}
            </span>
            
            <span className="flex-shrink-0 text-xs text-muted-foreground w-16">
              {formatTimestamp(log.timestamp)}
            </span>
            
            <span
              className="flex-shrink-0 text-xs px-1.5 py-0.5 rounded bg-white/5 w-16 text-center"
              style={{ color: levelColors[log.level] }}
            >
              {log.level.toUpperCase()}
            </span>
            
            <span className="flex-shrink-0 text-xs text-muted-foreground w-24 truncate">
              [{log.source}]
            </span>
            
            <span className="flex-1 text-foreground/90 break-all">
              {log.message}
            </span>
          </motion.div>
        ))}
      </AnimatePresence>
      
      {logs.length === 0 && (
        <div className="text-center text-muted-foreground py-8">
          No logs yet...
        </div>
      )}
    </div>
  );
}
