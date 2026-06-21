"use client";

import { SignedIn, SignedOut, SignInButton, SignUpButton, UserButton } from "@clerk/nextjs";

export default function Navbar() {
  return (
    <header className="flex items-center justify-between border-b border-white/10 bg-slate-950/70 px-4 py-4 backdrop-blur-xl sm:px-6">
      <div>
        <p className="text-xs uppercase tracking-[0.35em] text-cyan-300/80">CollegeGPT</p>
        <h1 className="text-lg font-semibold text-white">Document Chat</h1>
      </div>
      <div className="flex items-center gap-3">
        <SignedOut>
          <SignInButton mode="modal">
            <button className="rounded-full border border-white/10 px-4 py-2 text-sm font-medium text-white transition hover:bg-white/10">
              Sign In
            </button>
          </SignInButton>
          <SignUpButton mode="modal">
            <button className="rounded-full bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300">
              Sign Up
            </button>
          </SignUpButton>
        </SignedOut>
        <SignedIn>
          <UserButton afterSignOutUrl="/" />
        </SignedIn>
      </div>
    </header>
  );
}