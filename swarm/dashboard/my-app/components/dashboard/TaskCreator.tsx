"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Send, Sparkles, Terminal } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface TaskCreatorProps {
  onCreateTask: (task: string) => Promise<void>;
}

const quickTasks = [
  "Research competitors for",
  "Build a landing page for",
  "Write copy for",
  "Analyze metrics for",
  "Monitor trends in",
];

export function TaskCreator({ onCreateTask }: TaskCreatorProps) {
  const [task, setTask] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!task.trim() || isSubmitting) return;

    setIsSubmitting(true);
    try {
      await onCreateTask(task);
      setTask("");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleQuickTask = (prefix: string) => {
    setTask(prefix + " ");
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <Card className="border-2 border-yellow-500/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Terminal className="h-5 w-5" />
            Command Center
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="flex gap-2">
              <div className="relative flex-1">
                <Sparkles className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-yellow-500" />
                <Input
                  value={task}
                  onChange={(e) => setTask(e.target.value)}
                  placeholder="Enter mission command (e.g., Research AI competitors and build a comparison landing page)..."
                  className="pl-10 h-12"
                  disabled={isSubmitting}
                />
              </div>
              <Button 
                type="submit" 
                disabled={!task.trim() || isSubmitting}
                className="h-12 px-6"
              >
                {isSubmitting ? (
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  >
                    <Send className="h-4 w-4" />
                  </motion.div>
                ) : (
                  <>
                    <Send className="h-4 w-4 mr-2" />
                    Execute
                  </>
                )}
              </Button>
            </div>

            <div className="flex flex-wrap gap-2">
              {quickTasks.map((quickTask) => (
                <Badge
                  key={quickTask}
                  variant="secondary"
                  className="cursor-pointer hover:bg-accent transition-colors"
                  onClick={() => handleQuickTask(quickTask)}
                >
                  {quickTask}...
                </Badge>
              ))}
            </div>
          </form>
        </CardContent>
      </Card>
    </motion.div>
  );
}
