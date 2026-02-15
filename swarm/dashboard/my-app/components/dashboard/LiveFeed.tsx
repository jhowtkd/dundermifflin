"use client";

import { useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Activity, AGENT_CONFIG } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { 
  Play, 
  CheckCircle2, 
  XCircle, 
  UserPlus, 
  MessageSquare, 
  Settings,
  Radio
} from "lucide-react";

interface LiveFeedProps {
  activities: Activity[];
}

const activityIcons = {
  task_created: Play,
  task_started: Play,
  task_completed: CheckCircle2,
  task_failed: XCircle,
  agent_assigned: UserPlus,
  agent_message: MessageSquare,
  system_event: Settings,
};

const activityColors = {
  task_created: "text-blue-500",
  task_started: "text-yellow-500",
  task_completed: "text-green-500",
  task_failed: "text-red-500",
  agent_assigned: "text-purple-500",
  agent_message: "text-cyan-500",
  system_event: "text-gray-500",
};

function formatTime(timestamp: number): string {
  const date = new Date(timestamp);
  return date.toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
}

function formatRelativeTime(timestamp: number): string {
  const now = Date.now();
  const diff = now - timestamp;
  
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  
  if (seconds < 60) return `${seconds}s ago`;
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  return formatTime(timestamp);
}

export function LiveFeed({ activities }: LiveFeedProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = 0;
    }
  }, [activities]);

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Radio className="h-5 w-5 text-red-500 animate-pulse" />
          Live Feed
          <Badge variant="outline" className="ml-auto text-xs">
            {activities.length} events
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <ScrollArea className="h-[400px] px-6" ref={scrollRef}>
          <div className="space-y-3">
            <AnimatePresence mode="popLayout">
              {activities.map((activity) => {
                const Icon = activityIcons[activity.type];
                const agentConfig = activity.agentSlug 
                  ? AGENT_CONFIG[activity.agentSlug] 
                  : null;
                
                return (
                  <motion.div
                    key={activity.id}
                    layout
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    className="flex items-start gap-3 p-3 rounded-lg border bg-card/50 hover:bg-card transition-colors"
                  >
                    <div className={`mt-0.5 ${activityColors[activity.type]}`}>
                      <Icon className="h-4 w-4" />
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        {agentConfig && (
                          <span className="text-sm">
                            {agentConfig.emoji} {agentConfig.name}
                          </span>
                        )}
                        <span className="text-xs text-muted-foreground">
                          {formatRelativeTime(activity.timestamp)}
                        </span>
                      </div>
                      
                      <p className="text-sm mt-1">{activity.message}</p>

                      {activity.metadata && Object.keys(activity.metadata).length > 0 && (
                        <div className="mt-2 flex flex-wrap gap-1">
                          {Object.entries(activity.metadata).map(([key, value]) => (
                            <Badge key={key} variant="secondary" className="text-xs">
                              {key}: {String(value)}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </div>
                  </motion.div>
                );
              })}
            </AnimatePresence>

            {activities.length === 0 && (
              <div className="text-center py-8 text-muted-foreground">
                No recent activity
              </div>
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
