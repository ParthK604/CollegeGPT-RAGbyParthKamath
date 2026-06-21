"use client";

export default function UploadButton({ disabled, onUpload }) {
  return (
    <label
      className={`flex cursor-pointer items-center justify-center rounded-2xl px-4 py-3 text-sm font-medium transition ${
        disabled
          ? "cursor-not-allowed border border-white/10 bg-white/5 text-slate-500"
          : "border border-cyan-400/30 bg-cyan-400/10 text-cyan-100 hover:bg-cyan-400/20"
      }`}
    >
      <input
        type="file"
        accept="application/pdf"
        className="hidden"
        disabled={disabled}
        onChange={onUpload}
      />
      Upload PDF
    </label>
  );
}