"use client";

export default function ChatInput({ disabled, value, onChange, onSubmit, placeholder }) {
  return (
    <form onSubmit={onSubmit} className="flex items-end gap-3 rounded-[1.75rem] border border-white/10 bg-white/5 p-3 shadow-2xl shadow-black/20 backdrop-blur-xl">
      <textarea
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        rows={1}
        disabled={disabled}
        className="max-h-40 flex-1 resize-none bg-transparent px-2 py-3 text-sm text-white outline-none placeholder:text-slate-400 disabled:cursor-not-allowed"
      />
      <button
        type="submit"
        disabled={disabled}
        className="rounded-2xl bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400"
      >
        Send
      </button>
    </form>
  );
}