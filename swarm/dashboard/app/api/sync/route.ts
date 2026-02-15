import { NextResponse } from "next/server";
import { fetchMutation } from "convex/nextjs";

const CONVEX_URL = process.env.NEXT_PUBLIC_CONVEX_URL || "";

// This endpoint receives data from the OpenClaw Python backend
// and forwards it to Convex

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { type, data } = body;

    switch (type) {
      case "cost_log":
        // Forward cost log to Convex
        await fetchMutation(CONVEX_URL, "costs:createLog", {
          agent: data.agent,
          model: data.model,
          tokensIn: data.tokens_in,
          tokensOut: data.tokens_out,
          costUsd: data.cost_usd,
          durationMs: data.duration_ms,
          success: data.success,
          error: data.error,
          timestamp: new Date().toISOString(),
        });
        break;

      case "task_update":
        // Forward task update to Convex
        await fetchMutation(CONVEX_URL, "tasks:updateStatus", {
          id: data.task_id,
          status: data.status,
          cost: data.cost,
          tokens: data.tokens,
          duration: data.duration,
        });
        break;

      case "agent_status":
        // Forward agent status to Convex
        // First, find the agent by slug
        const agent = await fetchQuery(CONVEX_URL, "agents:get", { slug: data.slug });
        if (agent) {
          await fetchMutation(CONVEX_URL, "agents:updateStatus", {
            id: agent._id,
            status: data.status,
            currentTask: data.current_task,
            progress: data.progress || 0,
          });
        }
        break;

      case "activity":
        // Log activity to dashboard
        await fetchMutation(CONVEX_URL, "activityLogs:create", {
          timestamp: new Date().toISOString(),
          agent: data.agent_slug || "system",
          action: data.message,
          metadata: {
            type: data.type,
            level: data.level,
            ...data.metadata,
          },
        });
        break;

      default:
        return NextResponse.json({ error: "Unknown type" }, { status: 400 });
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("Sync error:", error);
    return NextResponse.json(
      { error: "Internal server error", details: String(error) },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({
    status: "ok",
    message: "OpenClaw Dashboard Sync API",
  });
}
