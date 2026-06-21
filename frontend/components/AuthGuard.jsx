"use client";

import { SignedIn, SignedOut, SignInButton, SignUpButton } from "@clerk/nextjs";

export default function AuthGuard({ children }) {
  return (
    <>
      <SignedIn>{children}</SignedIn>
      <SignedOut>
        <div className="flex min-h-screen items-center justify-center px-4">
          <div className="w-full max-w-lg rounded-4xl border border-white/10 bg-white/5 p-8 text-center shadow-2xl shadow-cyan-950/20 backdrop-blur-xl">
            <p className="text-sm uppercase tracking-[0.35em] text-cyan-300/80">CollegeGPT</p>
            <h1 className="mt-4 text-3xl font-semibold text-white">Sign in to start chatting with your documents.</h1>
            <p className="mt-3 text-sm leading-6 text-slate-300">
              Upload PDFs, ask questions, and continue previous conversations from one workspace.
            </p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:justify-center">
              <SignInButton mode="modal">
                <button className="rounded-full bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300">
                  Sign In
                </button>
              </SignInButton>
              <SignUpButton mode="modal">
                <button className="rounded-full border border-white/15 bg-white/5 px-5 py-3 text-sm font-semibold text-white transition hover:bg-white/10">
                  Sign Up
                </button>
              </SignUpButton>
            </div>
          </div>
        </div>
      </SignedOut>
    </>
  );
}