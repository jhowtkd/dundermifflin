"use client";

import { motion } from "framer-motion";
import { Play, Pause, CheckCircle, XCircle, AlertCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { getStatusColor, formatDate } from "@/lib/utils";

interface Mission {
  _id: string;
  title: string;
  description: string;
  status: "pending" | "running" | "completed" | "failed";
  priority: "low" | "medium" | "high" | "critical";
  progress: number;
  startedAt?: number;
  completedAt?: number;
}

interface MissionCardProps {
  mission: Mission;
  index: number;
}

export function MissionCard({ mission, index }: MissionCardProps) {
  const statusIcons = {
    pending: <Pause className="w-4 h-4" />,
    running: <Play className="w-4 h-4" />,
    completed: <CheckCircle className="w-4 h-4" />,
    failed: <XCircle className="w-4 h-4" />,
  };

  const priorityVariants = {
    low: "secondary",
    medium: "info",
    high: "warning",
    critical: "destructive",
  } as const;

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.05, duration: 0.3 }}
    >
      <Card className="group hover:border-primary/30 transition-all duration-300 overflow-hidden">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="flex-1 min-w-0">
              <CardTitle className="text-base font-medium truncate pr-4">
                {mission.title}
              </CardTitle>
              <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                {mission.description}
              </p>
            </div>
            <div className="flex gap-2">
              <Badge variant={priorityVariants[mission.priority]}>
                {mission.priority}
              </Badge>
              <Badge
                variant={
                  mission.status === "completed"
                    ? "success"
                    : mission.status === "failed"
                    ? "destructive"
                    : mission.status === "running"
                    ? "info"
                    : "secondary"
                }
                className="gap-1"
              >
                {statusIcons[mission.status]}
                {mission.status}
              </Badge>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-3">
          {/* Progress bar */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs">
              <span className="text-muted-foreground">Progress</span>
              <span className="font-medium">{mission.progress}%</span>
            </div>
            <div className="h-2 bg-muted rounded-full overflow-hidden">
              <motion.div
                className="h-full rounded-full transition-all duration-500"
                style={{
                  backgroundColor: getStatusColor(mission.status),
                  width: `${mission.progress}%`,
                }}
                initial={{ width: 0 }}
                animate={{ width: `${mission.progress}%` }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              />
            </div>
          </div>

          {/* Timestamps */}
          <div className="flex justify-between text-xs text-muted-foreground">
            {mission.startedAt && (
              <span>Started: {formatDate(mission.startedAt)}</span>
            )}
            {mission.completedAt && (
              <span>Completed: {formatDate(mission.completedAt)}</span>
            )}
          </div>

          {/* Action buttons */}
          {mission.status === "pending" && (
            <div className="flex gap-2 pt-1">
              <Button size="sm" variant="default" className="flex-1">
                <Play className="w-3.5 h-3.5 mr-1" />
                Start
              </Button>
              <Button size="sm" variant="outline" className="flex-1">
                Edit
              </Button>
            </div>
          )}
          {mission.status === "running" && (
            <Button size="sm" variant="destructive" className="w-full">
              <XCircle className="w-3.5 h-3.5 mr-1" />
              Cancel
            </Button>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
