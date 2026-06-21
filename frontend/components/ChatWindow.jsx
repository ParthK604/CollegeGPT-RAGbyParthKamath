"use client";

import { useEffect, useRef } from "react";
import MessageBubble from "./MessageBubble";
import LoadingMessage from "./LoadingMessage";

export default function ChatWindow({ messages, isLoading, emptyState }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <div className="flex min-h-0 flex-1 flex-col gap-4 overflow-hidden px-4 py-6 sm:px-6">
      <div className="flex-1 overflow-y-auto rounded-4xl border border-white/10 bg-white/5 p-4 shadow-2xl shadow-black/20 backdrop-blur-xl sm:p-6">
        {messages.length ? (
          <div className="space-y-4">
            {messages.map((message) => (
              <MessageBubble key={message.id} role={message.role} content={message.content} />
            ))}
            {isLoading ? <LoadingMessage /> : null}
            <div ref={bottomRef} />
          </div>
        ) : (
          <div className="flex h-full min-h-[50vh] items-center justify-center text-center text-slate-400">
            <div>
              <p className="text-sm uppercase tracking-[0.35em] text-cyan-300/80">CollegeGPT</p>
              <h2 className="mt-3 text-2xl font-semibold text-white">{emptyState}</h2>
              <p className="mt-2 text-sm">Ask questions about your uploaded PDFs and continue the conversation anytime.</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}