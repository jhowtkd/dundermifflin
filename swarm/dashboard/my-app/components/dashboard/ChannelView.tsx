"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Channel, Message, AGENT_CONFIG } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Hash, MessageSquare } from "lucide-react";

interface ChannelViewProps {
  channels: Channel[];
  messages: Message[];
  selectedChannel: string;
  onSelectChannel: (channelId: string) => void;
}

function getAvatar(authorId: string): string {
  const config = AGENT_CONFIG[authorId.toLowerCase()];
  if (config) return config.emoji;
  
  const avatars: Record<string, string> = {
    ralph: "🎩",
    scout: "🔍",
    max: "🛠️",
    maya: "✍️",
    tracker: "📊",
    watcher: "👁️",
    jeff: "👤",
    system: "⚙️",
  };
  return avatars[authorId.toLowerCase()] || "🤖";
}

function formatTime(timestamp: number): string {
  const date = new Date(timestamp);
  return date.toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
}

function formatDate(timestamp: number): string {
  const date = new Date(timestamp);
  const now = new Date();
  const isToday = date.toDateString() === now.toDateString();
  
  if (isToday) return "Today";
  return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

export function ChannelView({ 
  channels, 
  messages, 
  selectedChannel,
  onSelectChannel 
}: ChannelViewProps) {
  const activeChannels = channels.filter((c) => c.isActive);
  const selectedChannelData = channels.find((c) => c.id === selectedChannel);

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Hash className="h-5 w-5" />
          Channels
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <Tabs value={selectedChannel} onValueChange={onSelectChannel}>
          <div className="px-6 pb-4">
            <TabsList className="flex flex-wrap h-auto gap-1">
              {activeChannels.map((channel) => (
                <TabsTrigger 
                  key={channel.id} 
                  value={channel.id}
                  className="text-xs"
                >
                  #{channel.name}
                  {channel.messageCount > 0 && (
                    <Badge variant="secondary" className="ml-1 text-xs">
                      {channel.messageCount}
                    </Badge>
                  )}
                </TabsTrigger>
              ))}
            </TabsList>
          </div>

          {activeChannels.map((channel) => (
            <TabsContent 
              key={channel.id} 
              value={channel.id}
              className="mt-0"
            >
              <ScrollArea className="h-[300px] px-6">
                <div className="space-y-4">
                  <AnimatePresence mode="popLayout">
                    {messages
                      .filter((m) => m.channelId === channel.id)
                      .map((message) => (
                        <motion.div
                          key={message.id}
                          layout
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, y: -10 }}
                          className="flex gap-3"
                        >
                          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-muted flex items-center justify-center text-lg">
                            {getAvatar(message.authorId)}
                          </div>
                          
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                              <span className="font-semibold text-sm">
                                {message.authorId}
                              </span>
                              <span className="text-xs text-muted-foreground">
                                {formatTime(message.timestamp)}
                              </span>
                            </div>
                            
                            <p className="text-sm mt-0.5 whitespace-pre-wrap">
                              {message.content}
                            </p>
                          </div>
                        </motion.div>
                      ))}
                  </AnimatePresence>

                  {messages.filter((m) => m.channelId === channel.id).length === 0 && (
                    <div className="text-center py-8 text-muted-foreground">
                      <MessageSquare className="h-8 w-8 mx-auto mb-2 opacity-50" />
                      No messages yet
                    </div>
                  )}
                </div>
              </ScrollArea>
            </TabsContent>
          ))}
        </Tabs>
      </CardContent>
    </Card>
  );
}
