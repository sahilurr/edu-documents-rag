"use client";

import { useEffect, useRef, useState } from "react";
import { Send, Square } from "lucide-react";
import { streamChat, SourceCitation } from "@/lib/api";
import MessageBubble, { Message } from "./MessageBubble";

function uid() {
  return Math.random().toString(36).slice(2);
}

export default function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const scrollRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages]);

  async function handleSend() {
    const query = input.trim();
    if (!query || busy) return;
    setError(null);
    setInput("");

    const userMsg: Message = { id: uid(), role: "user", content: query };
    const assistantId = uid();
    const assistantMsg: Message = {
      id: assistantId,
      role: "assistant",
      content: "",
      sources: [],
      streaming: true,
    };
    setMessages((m) => [...m, userMsg, assistantMsg]);

    const controller = new AbortController();
    abortRef.current = controller;
    setBusy(true);

    try {
      await streamChat(
        query,
        (ev) => {
          if (ev.type === "sources") {
            setMessages((m) =>
              m.map((msg) =>
                msg.id === assistantId
                  ? { ...msg, sources: ev.sources as SourceCitation[] }
                  : msg
              )
            );
          } else if (ev.type === "token") {
            setMessages((m) =>
              m.map((msg) =>
                msg.id === assistantId
                  ? { ...msg, content: msg.content + ev.token }
                  : msg
              )
            );
          } else if (ev.type === "done") {
            setMessages((m) =>
              m.map((msg) =>
                msg.id === assistantId
                  ? { ...msg, content: ev.answer, streaming: false }
                  : msg
              )
            );
          } else if (ev.type === "error") {
            setError(ev.message);
          }
        },
        controller.signal
      );
    } catch (err: any) {
      if (err?.name !== "AbortError") {
        setError(err?.message ?? "Stream failed");
      }
    } finally {
      setBusy(false);
      abortRef.current = null;
      setMessages((m) =>
        m.map((msg) =>
          msg.id === assistantId ? { ...msg, streaming: false } : msg
        )
      );
    }
  }

  function handleStop() {
    abortRef.current?.abort();
  }

  function handleKey(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <section className="flex-1 flex flex-col min-w-0">
      <header className="px-6 py-4 border-b">
        <h1 className="font-semibold">Research Chat</h1>
        <p className="text-xs text-foreground/60">
          Answers are grounded in your uploaded documents. Citations show the
          exact source and page.
        </p>
      </header>

      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto scrollbar-thin px-6 py-6 space-y-6"
      >
        {messages.length === 0 && (
          <div className="text-center text-sm text-foreground/60 mt-20">
            Ask a question about your uploaded documents.
            <div className="mt-3 text-xs text-foreground/40">
              Example: "Summarize chapter 2 of CS3002"
            </div>
          </div>
        )}
        {messages.map((m) => (
          <MessageBubble key={m.id} message={m} />
        ))}
      </div>

      {error && (
        <div className="mx-6 mb-2 text-xs text-red-400 bg-red-500/10 border border-red-500/20 rounded-md px-3 py-2">
          {error}
        </div>
      )}

      <footer className="border-t px-6 py-4">
        <div className="flex items-end gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKey}
            rows={1}
            placeholder="Ask a question grounded in the uploaded documents..."
            className="flex-1 resize-none rounded-md bg-muted/40 border px-3 py-2 text-sm max-h-40"
          />
          {busy ? (
            <button
              onClick={handleStop}
              className="bg-muted border text-foreground px-3 py-2 rounded-md text-sm flex items-center gap-1"
            >
              <Square className="w-4 h-4" /> Stop
            </button>
          ) : (
            <button
              onClick={handleSend}
              disabled={!input.trim()}
              className="bg-accent text-white px-3 py-2 rounded-md text-sm flex items-center gap-1 disabled:opacity-60"
            >
              <Send className="w-4 h-4" /> Send
            </button>
          )}
        </div>
      </footer>
    </section>
  );
}
