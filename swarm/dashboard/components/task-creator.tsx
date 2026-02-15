"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Send, Sparkles } from "lucide-react";

interface TaskCreatorProps {
  onSubmit?: (task: string, priority: string) => void;
}

export function TaskCreator({ onSubmit }: TaskCreatorProps) {
  const [task, setTask] = useState("");
  const [priority, setPriority] = useState<"low" | "medium" | "high">("medium");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!task.trim()) return;
    onSubmit?.(task, priority);
    setTask("");
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <Card className="border-primary/20">
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-primary" />
            New Mission
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-3">
            <div className="flex gap-2">
              <Input
                value={task}
                onChange={(e) => setTask(e.target.value)}
                placeholder="Deploy a new landing page with dark mode..."
                className="flex-1"
              />
              <Button type="submit" disabled={!task.trim()}>
                <Send className="h-4 w-4 mr-2" />
                Execute
              </Button>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-muted-foreground">Priority:</span>
              {(["low", "medium", "high"] as const).map((p) => (
                <Badge
                  key={p}
                  variant={priority === p ? "default" : "outline"}
                  className="cursor-pointer text-xs capitalize"
                  onClick={() => setPriority(p)}
                >
                  {p}
                </Badge>
              ))}
            </div>
          </form>
        </CardContent>
      </Card>
    </motion.div>
  );
}
