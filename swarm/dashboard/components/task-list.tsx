"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import type { Task } from "@/types";
import { 
  Play, 
  CheckCircle2, 
  Clock, 
  AlertCircle, 
  MoreHorizontal,
  ListTodo 
} from "lucide-react";

interface TaskListProps {
  tasks: Task[];
  onTaskAction?: (taskId: string, action: string) => void;
}

const statusConfig = {
  pending: { icon: Clock, color: "text-yellow-500", bg: "bg-yellow-500/10", label: "Pending" },
  running: { icon: Play, color: "text-blue-500", bg: "bg-blue-500/10", label: "Running" },
  completed: { icon: CheckCircle2, color: "text-green-500", bg: "bg-green-500/10", label: "Completed" },
  failed: { icon: AlertCircle, color: "text-red-500", bg: "bg-red-500/10", label: "Failed" },
};

const priorityConfig = {
  low: { variant: "secondary" as const, label: "Low" },
  medium: { variant: "default" as const, label: "Medium" },
  high: { variant: "destructive" as const, label: "High" },
};

export function TaskList({ tasks, onTaskAction }: TaskListProps) {
  return (
    <Card className="h-[400px]">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base flex items-center gap-2">
            <ListTodo className="h-4 w-4" />
            Recent Tasks
          </CardTitle>
          <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
            <MoreHorizontal className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <ScrollArea className="h-[320px] px-6">
          <div className="space-y-2">
            {tasks.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-40 text-muted-foreground">
                <ListTodo className="h-8 w-8 mb-2 opacity-50" />
                <p className="text-sm">No tasks yet</p>
              </div>
            ) : (
              tasks.map((task, index) => {
                const status = statusConfig[task.status];
                const StatusIcon = status.icon;
                const priority = priorityConfig[task.priority];

                return (
                  <motion.div
                    key={task.id}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.2, delay: index * 0.03 }}
                    className="flex items-center gap-3 p-3 rounded-lg bg-muted/50 hover:bg-muted transition-colors cursor-pointer"
                    onClick={() => onTaskAction?.(task.id, "view")}
                  >
                    <div className={`p-2 rounded-md ${status.bg}`}>
                      <StatusIcon className={`h-4 w-4 ${status.color}`} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="text-sm font-medium truncate">{task.title}</p>
                        <Badge variant={priority.variant} className="text-[10px] h-4">
                          {priority.label}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-2 mt-0.5 text-xs text-muted-foreground">
                        {task.agentName && <span>by {task.agentName}</span>}
                        {task.project && (
                          <>
                            <span>·</span>
                            <span>{task.project}</span>
                          </>
                        )}
                      </div>
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {new Date(task.createdAt).toLocaleTimeString([], { 
                        hour: "2-digit", 
                        minute: "2-digit" 
                      })}
                    </div>
                  </motion.div>
                );
              })
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
