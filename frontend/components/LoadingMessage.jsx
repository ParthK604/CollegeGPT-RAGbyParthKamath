"use client";

export default function LoadingMessage() {
  return (
    <div className="flex justify-start">
      <div className="flex items-center gap-2 rounded-3xl border border-white/10 bg-white/5 px-4 py-3">
        <span className="h-2.5 w-2.5 animate-bounce rounded-full bg-cyan-300 [animation-delay:-0.2s]" />
        <span className="h-2.5 w-2.5 animate-bounce rounded-full bg-cyan-300 [animation-delay:-0.1s]" />
        <span className="h-2.5 w-2.5 animate-bounce rounded-full bg-cyan-300" />
      </div>
    </div>
  );
}