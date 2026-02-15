"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Task, AGENT_CONFIG } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { 
  ListTodo, 
  Clock, 
  CheckCircle2, 
  AlertCircle,
  ChevronRight,
  Layers
} from "lucide-react";

interface TaskQueueProps {
  tasks: Task[];
  limit?: number;
}

const statusIcons = {
  pending: Clock,
  in_progress: ListTodo,
  completed: CheckCircle2,
  failed: AlertCircle,
};

const statusColors = {
  pending: "text-yellow-500 bg-yellow-500/10",
  in_progress: "text-blue-500 bg-blue-500/10",
  completed: "text-green-500 bg-green-500/10",
  failed: "text-red-500 bg-red-500/10",
};

const priorityColors = {
  low: "border-l-2 border-l-gray-500",
  medium: "border-l-2 border-l-yellow-500",
  high: "border-l-2 border-l-red-500",
};

function formatTime(timestamp: number): string {
  const date = new Date(timestamp);
  return date.toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
}

export function TaskQueue({ tasks, limit = 10 }: TaskQueueProps) {
  const sortedTasks = [...tasks]
    .sort((a, b) => b.createdAt - a.createdAt)
    .slice(0, limit);

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Layers className="h-5 w-5" />
          Recent Tasks
          <Badge variant="outline" className="ml-auto">
            {tasks.length} total
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <ScrollArea className="h-[400px] px-6">
          <div className="space-y-2">
            <AnimatePresence mode="popLayout">
              {sortedTasks.map((task) => {
                const Icon = statusIcons[task.status];
                const assignedAgent = task.assignedAgent 
                  ? AGENT_CONFIG[task.assignedAgent] 
                  : null;

                return (
                  <motion.div
                    key={task.id}
                    layout
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className={`group relative overflow-hidden rounded-lg border bg-card p-3 transition-all hover:shadow-md ${priorityColors[task.priority]}`}
                  >
                    <div className="flex items-start gap-3">
                      <div className={`p-2 rounded-md ${statusColors[task.status]}`}>
                        <Icon className="h-4 w-4" />
                      </div>

                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-xs text-muted-foreground">
                            #{task.code}
                          </span>
                          <Badge variant="outline" className="text-xs capitalize">
                            {task.priority}
                          </Badge>
                          <Badge variant="outline" className="text-xs capitalize">
                            {task.complexity}
                          </Badge>
                        </div>

                        <p className="text-sm mt-1 line-clamp-2">{task.description}</p>

                        <div className="flex items-center gap-3 mt-2 text-xs text-muted-foreground">
                          <span>{formatTime(task.createdAt)}</span>
                          
                          {assignedAgent && (
                            <span className="flex items-center gap-1">
                              <span>{assignedAgent.emoji}</span>
                              <span>{assignedAgent.name}</span>
                            </span>
                          )}

                          {task.agentsRequired.length > 0 && (
                            <span className="flex items-center gap-1">
                              <span>Agents:</span>
                              <span>{task.agentsRequired.join(", ")}</span>
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </AnimatePresence>

            {sortedTasks.length === 0 && (
              <div className="text-center py-8 text-muted-foreground">
                No tasks yet
              </div>
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
