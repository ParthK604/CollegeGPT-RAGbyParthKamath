import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { ClerkProvider } from "@clerk/nextjs";
import { Toaster } from "react-hot-toast";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata = {
  title: "CollegeGPT",
  description: "ChatGPT-style document assistant for CollegeGPT",
};

export default function RootLayout({ children }) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-[#0a0f1c] text-slate-100">
        <ClerkProvider>
          {children}
          <Toaster
            position="top-right"
            toastOptions={{
              style: {
                background: "#111827",
                color: "#f8fafc",
                border: "1px solid rgba(148, 163, 184, 0.2)",
              },
            }}
          />
        </ClerkProvider>
      </body>
    </html>
  );
}
