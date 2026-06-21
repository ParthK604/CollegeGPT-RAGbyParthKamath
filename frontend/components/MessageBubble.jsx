"use client";

export default function MessageBubble({ role, content }) {
  const isUser = role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[90%] rounded-3xl px-4 py-3 text-sm leading-6 shadow-lg sm:max-w-[75%] ${
          isUser
            ? "bg-cyan-400 text-slate-950"
            : "border border-white/10 bg-white/5 text-slate-100"
        }`}
      >
        <p className="whitespace-pre-wrap">{content}</p>
      </div>
    </div>
  );
}