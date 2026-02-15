"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { 
  Clock, 
  Play, 
  Pause, 
  AlertCircle,
  Calendar,
  ChevronRight
} from "lucide-react";
import { formatDate, getStatusColor } from "@/lib/utils";

interface CronJob {
  _id: string;
  name: string;
  schedule: string;
  status: "active" | "paused" | "error";
  lastRun?: number;
  nextRun?: number;
}

interface CronJobsPanelProps {
  jobs: CronJob[];
}

const scheduleLabels: Record<string, string> = {
  "0 */6 * * *": "Every 6 hours",
  "0 */12 * * *": "Every 12 hours",
  "0 0 * * *": "Daily at midnight",
  "0 9 * * 1": "Weekly (Mon 9am)",
  "*/30 * * * *": "Every 30 minutes",
  "0 * * * *": "Hourly",
};

export function CronJobsPanel({ jobs }: CronJobsPanelProps) {
  if (jobs.length === 0) {
    return (
      <Card className="border-dashed border-border/50">
        <CardContent className="flex flex-col items-center justify-center py-8 text-center">
          <Clock className="w-10 h-10 text-muted-foreground/50 mb-3" />
          <p className="text-muted-foreground">No scheduled jobs</p>
          <p className="text-sm text-muted-foreground/70 mt-1">
            Cron jobs will appear here when scheduled
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-border/50">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base font-medium flex items-center gap-2">
            <Clock className="w-4 h-4 text-yellow-400" />
            Scheduled Jobs
          </CardTitle>
          <Badge variant="outline">{jobs.length} jobs</Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {jobs.map((job, index) => (
            <motion.div
              key={job._id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              className="flex items-center justify-between p-3 rounded-lg bg-secondary/30 hover:bg-secondary/50 transition-colors group"
            >
              <div className="flex items-center gap-3">
                <div
                  className="w-2 h-2 rounded-full"
                  style={{ backgroundColor: getStatusColor(job.status) }}
                />
                <div>
                  <p className="text-sm font-medium">{job.name}</p>
                  <div className="flex items-center gap-2 text-xs text-muted-foreground mt-0.5">
                    <Calendar className="w-3 h-3" />
                    <span>{scheduleLabels[job.schedule] || job.schedule}</span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-4">
                <div className="text-right hidden sm:block">
                  {job.nextRun && (
                    <p className="text-xs text-muted-foreground">
                      Next: {formatDate(job.nextRun)}
                    </p>
                  )}
                  {job.lastRun && (
                    <p className="text-xs text-muted-foreground/70">
                      Last: {formatDate(job.lastRun)}
                    </p>
                  )}
                </div>

                <div className="flex items-center gap-1">
                  {job.status === "active" ? (
                    <Button size="icon" variant="ghost" className="h-8 w-8">
                      <Pause className="w-4 h-4" />
                    </Button>
                  ) : job.status === "paused" ? (
                    <Button size="icon" variant="ghost" className="h-8 w-8">
                      <Play className="w-4 h-4" />
                    </Button>
                  ) : (
                    <Button size="icon" variant="ghost" className="h-8 w-8 text-destructive">
                      <AlertCircle className="w-4 h-4" />
                    </Button>
                  )}
                  <Button size="icon" variant="ghost" className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity">
                    <ChevronRight className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
