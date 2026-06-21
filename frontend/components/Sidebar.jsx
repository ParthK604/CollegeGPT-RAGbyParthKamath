"use client";

import UploadButton from "./UploadButton";

export default function Sidebar({ chats, currentChatId, disabled, onNewChat, onUpload, onSelectChat }) {
  return (
    <aside className="flex h-full w-full flex-col border-r border-white/10 bg-slate-950/80 backdrop-blur-xl lg:w-80">
      <div className="border-b border-white/10 p-4">
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className="text-xs uppercase tracking-[0.35em] text-cyan-300/80">CollegeGPT</p>
            <h2 className="mt-1 text-xl font-semibold text-white">Your chats</h2>
          </div>
          <button
            onClick={onNewChat}
            className="rounded-full border border-white/10 px-4 py-2 text-sm font-medium text-white transition hover:bg-white/10"
          >
            New Chat
          </button>
        </div>
        <div className="mt-4">
          <UploadButton disabled={disabled} onUpload={onUpload} />
        </div>
      </div>
      <div className="flex-1 overflow-y-auto p-3">
        <div className="space-y-2">
          {chats.length ? (
            chats.map((chat) => {
              const isActive = chat._id === currentChatId;

              return (
                <button
                  key={chat._id}
                  onClick={() => onSelectChat(chat)}
                  className={`w-full rounded-2xl border px-4 py-3 text-left transition ${
                    isActive
                      ? "border-cyan-400/30 bg-cyan-400/10"
                      : "border-white/10 bg-white/5 hover:bg-white/10"
                  }`}
                >
                  <p className="truncate text-sm font-medium text-white">{chat.title || chat.filename || "Untitled Chat"}</p>
                  <p className="mt-1 truncate text-xs text-slate-400">{chat.filename || chat.document_id || "Conversation"}</p>
                  <p className="mt-1 text-[11px] uppercase tracking-[0.2em] text-slate-500">
                    {chat.created_at ? new Date(chat.created_at).toLocaleDateString() : "Recent"}
                  </p>
                </button>
              );
            })
          ) : (
            <div className="rounded-2xl border border-dashed border-white/10 bg-white/5 p-4 text-sm text-slate-400">
              Upload a PDF to start chatting.
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}