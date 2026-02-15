import { httpRouter } from "convex/server";
import { httpAction } from "./_generated/server";

// HTTP actions for external integration with OpenClaw Python backend
const http = httpRouter();

// Webhook endpoint for agent status updates
http.route({
  path: "/webhook/agent-status",
  method: "POST",
  handler: httpAction(async (ctx, request) => {
    const body = await request.json();
    
    // Update agent status in Convex
    const { slug, status, currentTask } = body;
    
    const agent = await ctx.runQuery(async (ctx) => {
      return await ctx.db
        .query("agents")
        .withIndex("by_slug", (q) => q.eq("slug", slug))
        .first();
    });
    
    if (agent) {
      await ctx.runMutation(async (ctx) => {
        await ctx.db.patch(agent._id, {
          status,
          currentTask,
          lastHeartbeat: Date.now(),
        });
      });
    }
    
    return new Response(JSON.stringify({ success: true }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  }),
});

// Webhook endpoint for new tasks
http.route({
  path: "/webhook/task",
  method: "POST",
  handler: httpAction(async (ctx, request) => {
    const body = await request.json();
    
    const { code, description, priority, complexity, agentsRequired } = body;
    
    const taskId = await ctx.runMutation(async (ctx) => {
      return await ctx.db.insert("tasks", {
        code,
        description,
        priority: priority || "medium",
        complexity: complexity || "medium",
        agentsRequired: agentsRequired || [],
        status: "pending",
        createdAt: Date.now(),
      });
    });
    
    // Create activity
    await ctx.runMutation(async (ctx) => {
      await ctx.db.insert("activities", {
        type: "task_created",
        taskId,
        message: `New task created: ${description}`,
        timestamp: Date.now(),
      });
    });
    
    return new Response(JSON.stringify({ success: true, taskId }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  }),
});

// Webhook endpoint for activities
http.route({
  path: "/webhook/activity",
  method: "POST",
  handler: httpAction(async (ctx, request) => {
    const body = await request.json();
    
    const { type, agentSlug, taskId, message, metadata } = body;
    
    await ctx.runMutation(async (ctx) => {
      await ctx.db.insert("activities", {
        type,
        agentSlug,
        taskId,
        message,
        metadata,
        timestamp: Date.now(),
      });
    });
    
    return new Response(JSON.stringify({ success: true }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  }),
});

// Health check endpoint
http.route({
  path: "/health",
  method: "GET",
  handler: httpAction(async () => {
    return new Response(JSON.stringify({ status: "ok", timestamp: Date.now() }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  }),
});

export default http;
