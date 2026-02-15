import { v } from "convex/values";
import { query, mutation } from "./_generated/server";

// Get all channels
export const getAll = query({
  handler: async (ctx) => {
    return await ctx.db.query("channels").collect();
  },
});

// Get channel by name
export const getByName = query({
  args: { name: v.string() },
  handler: async (ctx, { name }) => {
    return await ctx.db
      .query("channels")
      .withIndex("by_name", (q) => q.eq("name", name))
      .first();
  },
});

// Get messages for channel
export const getMessages = query({
  args: { 
    channelId: v.id("channels"),
    limit: v.optional(v.number()) 
  },
  handler: async (ctx, { channelId, limit = 50 }) => {
    return await ctx.db
      .query("messages")
      .withIndex("by_channel", (q) => q.eq("channelId", channelId))
      .order("desc")
      .take(limit);
  },
});

// Send message
export const sendMessage = mutation({
  args: {
    channelId: v.id("channels"),
    authorId: v.string(),
    content: v.string(),
    isSystem: v.optional(v.boolean()),
  },
  handler: async (ctx, { channelId, authorId, content, isSystem = false }) => {
    const messageId = await ctx.db.insert("messages", {
      channelId,
      authorId,
      content,
      timestamp: Date.now(),
      isSystem,
    });

    // Update channel last activity
    await ctx.db.patch(channelId, {
      lastActivity: Date.now(),
    });

    return messageId;
  },
});

// Create channel
export const create = mutation({
  args: {
    name: v.string(),
    description: v.string(),
  },
  handler: async (ctx, { name, description }) => {
    const existing = await ctx.db
      .query("channels")
      .withIndex("by_name", (q) => q.eq("name", name))
      .first();
    
    if (existing) return existing._id;

    return await ctx.db.insert("channels", {
      name,
      description,
      messageCount: 0,
      lastActivity: Date.now(),
      isActive: true,
    });
  },
});

// Initialize default channels
export const initialize = mutation({
  handler: async (ctx) => {
    const defaultChannels = [
      { name: "orders", description: "Main command channel" },
      { name: "find-output", description: "Research findings" },
      { name: "build-output", description: "Code & technical output" },
      { name: "create-output", description: "Copy & content output" },
      { name: "track-output", description: "Analytics & metrics" },
      { name: "watch-output", description: "Monitoring alerts" },
      { name: "general", description: "General discussion" },
    ];

    for (const ch of defaultChannels) {
      const existing = await ctx.db
        .query("channels")
        .withIndex("by_name", (q) => q.eq("name", ch.name))
        .first();
      
      if (!existing) {
        await ctx.db.insert("channels", {
          ...ch,
          messageCount: 0,
          lastActivity: Date.now(),
          isActive: true,
        });
      }
    }
  },
});
