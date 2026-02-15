"use client";

import { motion } from "framer-motion";
import { Card, CardContent } from "./ui/card";
import { 
  Bot, 
  Rocket, 
  CheckCircle, 
  XCircle,
  Clock,
  Activity,
  TrendingUp,
  AlertTriangle
} from "lucide-react";

interface StatsOverviewProps {
  totalAgents: number;
  onlineAgents: number;
  activeMissions: number;
  pendingMissions: number;
  completedMissions: number;
  failedMissions: number;
}

export function StatsOverview({
  totalAgents,
  onlineAgents,
  activeMissions,
  pendingMissions,
  completedMissions,
  failedMissions,
}: StatsOverviewProps) {
  const stats = [
    {
      label: "Online Agents",
      value: onlineAgents,
      total: totalAgents,
      icon: Bot,
      color: "text-green-400",
      bgColor: "bg-green-500/10",
      borderColor: "border-green-500/20",
    },
    {
      label: "Active Missions",
      value: activeMissions,
      icon: Rocket,
      color: "text-cyan-400",
      bgColor: "bg-cyan-500/10",
      borderColor: "border-cyan-500/20",
    },
    {
      label: "Pending",
      value: pendingMissions,
      icon: Clock,
      color: "text-yellow-400",
      bgColor: "bg-yellow-500/10",
      borderColor: "border-yellow-500/20",
    },
    {
      label: "Completed",
      value: completedMissions,
      icon: CheckCircle,
      color: "text-purple-400",
      bgColor: "bg-purple-500/10",
      borderColor: "border-purple-500/20",
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat, index) => (
        <motion.div
          key={stat.label}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1, duration: 0.3 }}
        >
          <Card className={`relative overflow-hidden border ${stat.borderColor} bg-gradient-to-br from-card to-card/50 group hover:shadow-lg transition-all duration-300`}>
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">{stat.label}</p>
                  <div className="flex items-baseline gap-2 mt-1">
                    <span className="text-3xl font-bold">{stat.value}</span>
                    {stat.total && (
                      <span className="text-sm text-muted-foreground">
                        / {stat.total}
                      </span>
                    )}
                  </div>
                </div>
                <div className={`w-10 h-10 rounded-lg ${stat.bgColor} flex items-center justify-center`}>
                  <stat.icon className={`w-5 h-5 ${stat.color}`} />
                </div>
              </div>
              
              {/* Progress indicator for agents */}
              {stat.total && (
                <div className="mt-4">
                  <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                    <motion.div
                      className="h-full rounded-full bg-green-500"
                      initial={{ width: 0 }}
                      animate={{ width: `${(stat.value / stat.total) * 100}%` }}
                      transition={{ duration: 0.5, delay: index * 0.1 }}
                    />
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    {Math.round((stat.value / stat.total) * 100)}% online
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      ))}
    </div>
  );
}
