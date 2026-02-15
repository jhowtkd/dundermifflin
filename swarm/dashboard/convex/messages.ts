import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

export const listChannels = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db.query("channels").order("desc").take(50);
  },
});

export const getMessages = query({
  args: {
    channelId: v.id("channels"),
    limit: v.optional(v.number()),
  },
  handler: async (ctx, { channelId, limit = 50 }) => {
    return await ctx.db
      .query("messages")
      .withIndex("by_channel", (q) => q.eq("channelId", channelId))
      .order("desc")
      .take(limit);
  },
});

export const addMessage = mutation({
  args: {
    channelId: v.id("channels"),
    authorId: v.string(),
    authorName: v.optional(v.string()),
    content: v.string(),
  },
  handler: async (ctx, { channelId, authorId, authorName, content }) => {
    const now = new Date().toISOString();
    const messageId = await ctx.db.insert("messages", {
      channelId,
      authorId,
      authorName,
      content,
      createdAt: now,
    });

    // Update channel message count
    const channel = await ctx.db.get(channelId);
    if (channel) {
      await ctx.db.patch(channelId, {
        messageCount: channel.messageCount + 1,
        lastMessageAt: now,
      });
    }

    return messageId;
  },
});

export const createChannel = mutation({
  args: {
    name: v.string(),
    description: v.optional(v.string()),
  },
  handler: async (ctx, { name, description }) => {
    const existing = await ctx.db
      .query("channels")
      .withIndex("by_name", (q) => q.eq("name", name))
      .first();

    if (existing) {
      return existing._id;
    }

    return await ctx.db.insert("channels", {
      name,
      description,
      messageCount: 0,
      lastMessageAt: new Date().toISOString(),
    });
  },
});

export const seedChannels = mutation({
  args: {},
  handler: async (ctx) => {
    const channels = [
      { name: "orders", description: "Task orders and coordination" },
      { name: "research", description: "Research findings and sources" },
      { name: "build", description: "Development progress" },
      { name: "copy", description: "Copywriting output" },
      { name: "analytics", description: "Analytics and metrics" },
      { name: "system", description: "System logs and monitoring" },
    ];

    for (const channel of channels) {
      const existing = await ctx.db
        .query("channels")
        .withIndex("by_name", (q) => q.eq("name", channel.name))
        .first();

      if (!existing) {
        await ctx.db.insert("channels", {
          ...channel,
          messageCount: 0,
        });
      }
    }
    return { success: true };
  },
});
