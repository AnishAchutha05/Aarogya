"use client";

import React, { useState, useEffect, useRef } from "react";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { ProtectedLayout } from "@/components/layout/protected-layout";
import { coachService } from "@/lib/services/coach";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Spinner } from "@/components/ui/spinner";
import {
  MessageScrollerProvider,
  MessageScroller,
  MessageScrollerViewport,
  MessageScrollerContent,
  MessageScrollerItem,
  MessageScrollerButton,
} from "@/components/ui/message-scroller";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Send, Map, History, MessageCircle, Plus } from "lucide-react";
import aarogyaLogo from "@/assets/aarogyalogo.png";
import type { ChatSessionResponse, ChatMessageResponse } from "@/types";

export default function CoachPage() {
  const router = useRouter();
  const [sessions, setSessions] = useState<ChatSessionResponse[]>([]);
  const [activeSession, setActiveSession] = useState<ChatSessionResponse | null>(null);
  const [messages, setMessages] = useState<ChatMessageResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [input, setInput] = useState("");
  const [generatingRoadmap, setGeneratingRoadmap] = useState(false);
  const [historyOpen, setHistoryOpen] = useState(false);

  const loadSessions = async () => {
    try {
      const data = await coachService.listSessions();
      setSessions(data);
      if (data.length > 0 && !activeSession) {
        setActiveSession(data[0]);
      }
    } catch {
      // Handle error quietly
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSessions();
  }, []);

  useEffect(() => {
    if (activeSession) {
      loadMessages(activeSession.id);
    } else {
      setMessages([]);
    }
  }, [activeSession]);

  const loadMessages = async (sessionId: string) => {
    try {
      const data = await coachService.getMessages(sessionId);
      setMessages(data);
    } catch {
      // Handle error quietly
    }
  };

  const handleSend = async () => {
    if (!input.trim() || sending) return;
    
    let currentSession = activeSession;
    
    // Create session if none exists
    if (!currentSession) {
      try {
        currentSession = await coachService.createSession("New Conversation");
        setSessions((prev) => [currentSession!, ...prev]);
        setActiveSession(currentSession);
      } catch {
        return;
      }
    }

    const messageText = input.trim();
    setInput("");
    setSending(true);

    // Optimistically add user message
    const tempId = Date.now().toString();
    const newMsg: ChatMessageResponse = {
      id: tempId,
      session_id: currentSession.id,
      role: "user",
      content: messageText,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, newMsg]);

    try {
      const response = await coachService.sendMessage(currentSession.id, messageText);
      setMessages((prev) => [...prev, response]);
    } catch (err) {
      // Revert on error
      setMessages((prev) => prev.filter((m) => m.id !== tempId));
    } finally {
      setSending(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const createNewSession = async () => {
    setHistoryOpen(false);
    setActiveSession(null);
    setMessages([]);
  };

  const generateRoadmap = async () => {
    if (!activeSession) return;
    setGeneratingRoadmap(true);
    try {
      // We will redirect to roadmap page with session ID or handle state there
      router.push(`/roadmap?session=${activeSession.id}`);
    } finally {
      setGeneratingRoadmap(false);
    }
  };

  if (loading) {
    return (
      <ProtectedLayout title="Aaryu">
        <div className="flex h-full items-center justify-center">
          <Spinner className="text-primary" />
        </div>
      </ProtectedLayout>
    );
  }

  return (
    <ProtectedLayout title="Aaryu">
      <div className="flex flex-col h-[calc(100vh-3.5rem)] max-w-4xl mx-auto w-full">
        {/* Header toolbar */}
        <div className="flex items-center justify-between p-4 border-b border-border flex-shrink-0">
          <div className="flex items-center gap-3">
            <Image src={aarogyaLogo} alt="" width={48} height={48} className="h-10 w-10 rounded-full object-contain" />
            <span className="text-sm font-semibold tracking-tight text-foreground">Aarogya</span>
            <div>
              <h2 className="text-sm font-semibold text-foreground">Aaryu</h2>
              <p className="text-xs text-muted-foreground">Your Wellness Mentor</p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setHistoryOpen(true)}
              className="text-xs h-8 border-border hover:bg-muted"
            >
              <History className="w-3.5 h-3.5 mr-1.5" />
              History
            </Button>
            {messages.length > 2 && (
              <Button
                variant="outline"
                size="sm"
                onClick={generateRoadmap}
                disabled={generatingRoadmap || sending}
                className="text-xs h-8 border-primary/20 text-primary hover:bg-primary/10"
              >
                {generatingRoadmap ? (
                  <Spinner className="w-3 h-3 mr-1.5" />
                ) : (
                  <Map className="w-3.5 h-3.5 mr-1.5" />
                )}
                Roadmap
              </Button>
            )}
          </div>
        </div>

        {/* Chat Area */}
        <div className="flex-1 min-h-0 relative">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full p-6 text-center text-muted-foreground fade-in">
              <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                <MessageCircle className="w-6 h-6 text-primary" />
              </div>
              <h3 className="text-foreground font-medium mb-2">Start a conversation</h3>
              <p className="text-sm max-w-sm text-balance">
                Ask Aaryu to help you build a routine, review your progress, or plan your week.
              </p>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-8 w-full max-w-md">
                {["Build a morning routine", "Quick 15m workout plan", "Help me sleep better", "Review my progress"].map((suggestion) => (
                  <button
                    key={suggestion}
                    onClick={() => setInput(suggestion)}
                    className="p-3 text-left text-sm border border-border rounded-lg hover:border-primary/50 hover:bg-primary/5 transition-colors"
                  >
                    "{suggestion}"
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <MessageScrollerProvider>
              <MessageScroller className="bg-background">
                <MessageScrollerViewport className="p-4 sm:p-6">
                  <MessageScrollerContent>
                  {messages.map((msg, idx) => {
                    const isUser = msg.role === "user";
                    const isLast = idx === messages.length - 1;
                    return (
                      <MessageScrollerItem
                        key={msg.id}
                        scrollAnchor={isLast && !sending}
                        className={`flex w-full ${isUser ? "justify-end" : "justify-start"}`}
                      >
                        <div
                          className={`max-w-[85%] sm:max-w-[75%] rounded-2xl px-4 py-3 text-sm ${
                            isUser
                              ? "bg-primary text-primary-foreground rounded-br-sm"
                              : "bg-muted text-foreground rounded-bl-sm border border-border"
                          }`}
                        >
                          {msg.content.split('\n').map((line, i) => (
                            <React.Fragment key={i}>
                              {line}
                              {i < msg.content.split('\n').length - 1 && <br />}
                            </React.Fragment>
                          ))}
                        </div>
                      </MessageScrollerItem>
                    );
                  })}
                  
                  {sending && (
                    <MessageScrollerItem scrollAnchor className="flex w-full justify-start">
                      <div className="max-w-[85%] rounded-2xl rounded-bl-sm px-5 py-4 text-sm bg-muted text-foreground border border-border flex items-center gap-1">
                        <span className="typing-dot"></span>
                        <span className="typing-dot"></span>
                        <span className="typing-dot"></span>
                      </div>
                    </MessageScrollerItem>
                  )}
                  </MessageScrollerContent>
                </MessageScrollerViewport>
                <MessageScrollerButton />
              </MessageScroller>
            </MessageScrollerProvider>
          )}
        </div>

        {/* Input Area */}
        <div className="p-4 bg-background border-t border-border flex-shrink-0">
          <div className="relative flex items-end gap-2 max-w-4xl mx-auto">
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Message Aaryu..."
              className="min-h-[44px] max-h-32 resize-none py-3 px-4 rounded-xl border-border focus-visible:ring-primary/20 bg-muted/50"
              rows={1}
            />
            <Button
              onClick={handleSend}
              disabled={!input.trim() || sending}
              size="icon"
              className="h-11 w-11 rounded-xl bg-primary text-primary-foreground flex-shrink-0"
            >
              <Send className="w-5 h-5" />
            </Button>
          </div>
          <p className="text-[10px] text-center text-muted-foreground mt-2">
            Aaryu can make mistakes. Verify important information.
          </p>
        </div>
      </div>

      {/* History Sheet */}
      <Sheet open={historyOpen} onOpenChange={setHistoryOpen}>
        <SheetContent side="left" className="w-[300px] sm:w-[340px] p-0 flex flex-col border-border bg-card">
          <SheetHeader className="p-4 border-b border-border">
            <SheetTitle className="text-foreground">Conversations</SheetTitle>
          </SheetHeader>
          <div className="p-4">
            <Button
              onClick={createNewSession}
              className="w-full bg-primary/10 text-primary hover:bg-primary/20 justify-start mb-4"
              variant="ghost"
            >
              <Plus className="w-4 h-4 mr-2" />
              New Conversation
            </Button>
            
            <div className="flex flex-col gap-1 overflow-y-auto max-h-[calc(100vh-140px)] scrollbar-aarogya pr-1">
              {sessions.map((session) => (
                <button
                  key={session.id}
                  onClick={() => {
                    setActiveSession(session);
                    setHistoryOpen(false);
                  }}
                  className={`flex flex-col items-start p-3 rounded-lg text-left transition-colors ${
                    activeSession?.id === session.id
                      ? "bg-muted border border-border"
                      : "hover:bg-muted/50 border border-transparent"
                  }`}
                >
                  <span className="text-sm font-medium text-foreground truncate w-full">
                    {session.title || "Conversation"}
                  </span>
                  <span className="text-xs text-muted-foreground mt-1">
                    {new Date(session.created_at).toLocaleDateString()}
                  </span>
                </button>
              ))}
              {sessions.length === 0 && (
                <p className="text-sm text-muted-foreground text-center py-8">
                  No previous conversations
                </p>
              )}
            </div>
          </div>
        </SheetContent>
      </Sheet>
    </ProtectedLayout>
  );
}
