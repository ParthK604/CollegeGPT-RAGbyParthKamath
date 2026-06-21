"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useUser } from "@clerk/nextjs";
import toast from "react-hot-toast";

import AuthGuard from "@/components/AuthGuard";
import Navbar from "@/components/Navbar";
import Sidebar from "@/components/Sidebar";
import ChatWindow from "@/components/ChatWindow";
import ChatInput from "@/components/ChatInput";
import { getChats, getMessages, queryDocument, syncUser, uploadPdf } from "@/lib/api";

function formatMessages(rawMessages) {
  return (rawMessages || [])
    .map((message, index) => ({
      id: message._id || `${message.chat_id || "msg"}-${index}`,
      role: message.role,
      content: message.content || "",
      createdAt: message.created_at,
    }))
    .sort((left, right) => new Date(left.createdAt || 0) - new Date(right.createdAt || 0));
}

function CollegeGPTApp() {
  const { user, isLoaded } = useUser();
  const [currentUser, setCurrentUser] = useState(null);
  const [chats, setChats] = useState([]);
  const [currentChatId, setCurrentChatId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isHydrating, setIsHydrating] = useState(true);

  const chatListLoaded = useRef(false);

  useEffect(() => {
    async function hydrateUser() {
      if (!isLoaded) {
        return;
      }

      if (!user) {
        setCurrentUser(null);
        setChats([]);
        setCurrentChatId(null);
        setMessages([]);
        setIsHydrating(false);
        return;
      }

      const payload = {
        clerk_id: user.id,
        email: user.primaryEmailAddress?.emailAddress || user.emailAddresses?.[0]?.emailAddress || "",
        name: user.fullName || user.firstName || user.username || "CollegeGPT User",
        provider: "clerk",
      };

      try {
        const response = await syncUser(payload);
        setCurrentUser(response.user || payload);
      } catch (error) {
        setCurrentUser(payload);
        toast.error(error.message || "Unable to sync your account right now.");
      }

      setIsHydrating(false);
    }

    hydrateUser();
  }, [isLoaded, user]);

  useEffect(() => {
    async function loadChats() {
      if (!currentUser?.clerk_id || chatListLoaded.current) {
        return;
      }

      try {
        const response = await getChats(currentUser.clerk_id);
        setChats(Array.isArray(response) ? response : []);
        chatListLoaded.current = true;
      } catch (error) {
        toast.error(error.message || "Failed to load chats.");
      }
    }

    loadChats();
  }, [currentUser]);

  useEffect(() => {
    if (!currentChatId) {
      return;
    }

    async function loadMessages() {
      try {
        const response = await getMessages(currentChatId);
        setMessages(formatMessages(response));
      } catch (error) {
        toast.error(error.message || "Failed to load chat history.");
      }
    }

    loadMessages();
  }, [currentChatId]);

  const currentChat = useMemo(
    () => chats.find((chat) => chat._id === currentChatId) || null,
    [chats, currentChatId]
  );

  async function handleUpload(event) {
    const file = event.target.files?.[0];
    event.target.value = "";

    if (!file) {
      return;
    }

    if (!currentUser?.clerk_id) {
      toast.error("Sign in required to upload a PDF.");
      return;
    }

    try {
      const response = await uploadPdf(file, currentUser.clerk_id);
      toast.success("PDF uploaded successfully. You can start asking questions.");
      setCurrentChatId(response.chat_id);
      chatListLoaded.current = false;
      const updatedChats = await getChats(currentUser.clerk_id);
      setChats(Array.isArray(updatedChats) ? updatedChats : []);
    } catch (error) {
      toast.error(error.message || "Upload failed.");
    }
  }

  async function handleSend(event) {
    event.preventDefault();

    if (!inputValue.trim()) {
      return;
    }

    if (!currentChatId) {
      toast.error("Upload a PDF or open a chat first.");
      return;
    }

    const question = inputValue.trim();
    setInputValue("");
    setMessages((previous) => [
      ...previous,
      {
        id: `user-${Date.now()}`,
        role: "user",
        content: question,
      },
    ]);
    setIsLoading(true);

    try {
      const response = await queryDocument({
        chat_id: currentChatId,
        question,
      });

      setMessages((previous) => [
        ...previous,
        {
          id: `assistant-${Date.now()}`,
          role: "assistant",
          content: response.answer,
        },
      ]);
    } catch (error) {
      toast.error(error.message || "Query failed.");
    } finally {
      setIsLoading(false);
    }
  }

  function handleSelectChat(chat) {
    setCurrentChatId(chat._id);
  }

  function handleNewChat() {
    setCurrentChatId(null);
    setMessages([]);
  }

  const emptyState = currentChat
    ? `Continue chat: ${currentChat.title || currentChat.filename || "Document"}`
    : "Upload a PDF to start chatting.";

  const canInteract = Boolean(currentUser?.clerk_id) && !isHydrating;

  return (
    <div className="flex min-h-screen flex-col bg-transparent">
      <Navbar />
      <AuthGuard>
        <div className="flex min-h-0 flex-1 flex-col lg:flex-row">
          <Sidebar
            chats={chats}
            currentChatId={currentChatId}
            disabled={!canInteract}
            onNewChat={handleNewChat}
            onUpload={handleUpload}
            onSelectChat={handleSelectChat}
          />
          <main className="flex min-h-0 flex-1 flex-col">
            <ChatWindow messages={messages} isLoading={isLoading} emptyState={emptyState} />
            <div className="border-t border-white/10 bg-slate-950/80 px-4 py-4 backdrop-blur-xl sm:px-6">
              <ChatInput
                disabled={!canInteract || !currentChatId || isLoading}
                value={inputValue}
                onChange={(event) => setInputValue(event.target.value)}
                onSubmit={handleSend}
                placeholder={canInteract ? "Ask a question about your uploaded PDF..." : "Sign in to start chatting with your documents."}
              />
            </div>
          </main>
        </div>
      </AuthGuard>
    </div>
  );
}

export default function Home() {
  return <CollegeGPTApp />;
}
