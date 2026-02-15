import { NextResponse } from "next/server";
import { fetchMutation, fetchQuery } from "convex/nextjs";

const CONVEX_URL = process.env.NEXT_PUBLIC_CONVEX_URL || "";

// Webhook endpoints for external integrations (Python backend)

export async function POST(request: Request, { params }: { params: { path: string } }) {
  try {
    const body = await request.json();
    const path = params.path;

    switch (path) {
      case "agent-status":
        // Find agent by slug
        const agent = await fetchQuery(CONVEX_URL, "agents:get", { slug: body.slug });
        if (agent) {
          await fetchMutation(CONVEX_URL, "agents:updateStatus", {
            id: agent._id,
            status: body.status,
            currentTask: body.currentTask,
            progress: body.progress || 0,
          });
          return NextResponse.json({ success: true });
        }
        return NextResponse.json({ error: "Agent not found" }, { status: 404 });

      case "task":
        const taskId = await fetchMutation(CONVEX_URL, "tasks:create", {
          title: body.code,
          description: body.description,
          priority: body.priority || "medium",
        });
        return NextResponse.json({ success: true, taskId });

      case "activity":
        await fetchMutation(CONVEX_URL, "activityLogs:create", {
          timestamp: new Date().toISOString(),
          agent: body.agentSlug || "system",
          action: body.message,
          metadata: {
            type: body.type,
            taskId: body.taskId,
            ...body.metadata,
          },
        });
        return NextResponse.json({ success: true });

      case "cost":
        await fetchMutation(CONVEX_URL, "costs:createLog", {
          agent: body.agent,
          model: body.model,
          tokensIn: body.tokensIn,
          tokensOut: body.tokensOut,
          costUsd: body.costUsd,
          durationMs: body.durationMs,
          success: body.success,
          timestamp: new Date().toISOString(),
        });
        return NextResponse.json({ success: true });

      default:
        return NextResponse.json({ error: "Unknown webhook path" }, { status: 404 });
    }
  } catch (error) {
    console.error(`Webhook error (${params.path}):`, error);
    return NextResponse.json(
      { error: "Webhook failed", details: String(error) },
      { status: 500 }
    );
  }
}
