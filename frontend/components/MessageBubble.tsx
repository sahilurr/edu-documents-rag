"use client";

import ReactMarkdown from "react-markdown";
import { SourceCitation } from "@/lib/api";
import { User, Sparkles } from "lucide-react";
import CitationList from "./CitationList";

export type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: SourceCitation[];
  streaming?: boolean;
};

export default function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";
  return (
    <div className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}>
      {!isUser && (
        <div className="shrink-0 w-8 h-8 rounded-full bg-accent/15 flex items-center justify-center">
          <Sparkles className="w-4 h-4 text-accent" />
        </div>
      )}
      <div className={`max-w-[78%] ${isUser ? "order-1" : ""}`}>
        <div
          className={`rounded-2xl px-4 py-3 text-sm whitespace-pre-wrap ${
            isUser
              ? "bg-accent text-white rounded-br-md"
              : "bg-muted/60 rounded-bl-md prose-chat"
          }`}
        >
          {isUser ? (
            message.content
          ) : (
            <ReactMarkdown>{message.content || "..."}</ReactMarkdown>
          )}
          {message.streaming && (
            <span className="inline-block w-1.5 h-3.5 ml-0.5 align-middle bg-foreground/60 animate-pulse" />
          )}
        </div>
        {!isUser && message.sources && message.sources.length > 0 && (
          <CitationList sources={message.sources} />
        )}
      </div>
      {isUser && (
        <div className="shrink-0 w-8 h-8 rounded-full bg-muted/80 flex items-center justify-center">
          <User className="w-4 h-4" />
        </div>
      )}
    </div>
  );
}
