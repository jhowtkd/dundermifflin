"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LucideIcon } from "lucide-react";
import { formatCurrency, formatNumber } from "@/lib/utils";

interface StatsCardProps {
  title: string;
  value: number;
  icon: LucideIcon;
  formatter?: "number" | "currency" | "duration";
  trend?: { value: number; positive: boolean };
  index?: number;
  color?: string;
}

export function StatsCard({
  title,
  value,
  icon: Icon,
  formatter = "number",
  trend,
  index = 0,
  color = "hsl(var(--primary))",
}: StatsCardProps) {
  const formattedValue =
    formatter === "currency"
      ? formatCurrency(value)
      : formatter === "number"
      ? formatNumber(value)
      : value;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3, delay: index * 0.05 }}
    >
      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            {title}
          </CardTitle>
          <div
            className="rounded-md p-2"
            style={{ backgroundColor: `${color}20`, color }}
          >
            <Icon className="h-4 w-4" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{formattedValue}</div>
          {trend && (
            <p
              className={`text-xs ${
                trend.positive ? "text-green-500" : "text-red-500"
              }`}
            >
              {trend.positive ? "+" : "-"}
              {trend.value}% from last hour
            </p>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
