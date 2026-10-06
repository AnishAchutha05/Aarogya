"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { ProtectedLayout } from "@/components/layout/protected-layout";
import { roadmapService } from "@/lib/services/roadmap";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { Card, CardContent } from "@/components/ui/card";
import { Map, ArrowLeft, RefreshCw, AlertCircle, Copy, Check } from "lucide-react";
import ReactMarkdown from "react-markdown";

function RoadmapContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const sessionId = searchParams.get("session");
  
  const [markdown, setMarkdown] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (sessionId) {
      generateRoadmap(sessionId);
    }
  }, [sessionId]);

  const generateRoadmap = async (id: string) => {
    setLoading(true);
    setError(null);
    setCopied(false);
    try {
      const result = await roadmapService.generateFromSession(id);
      setMarkdown(result.markdown);
    } catch (err) {
      setError("Failed to generate roadmap. Please try again or chat more with Aaryu first.");
    } finally {
      setLoading(false);
    }
  };

  const copyRoadmap = async () => {
    if (!markdown) return;
    try {
      await navigator.clipboard.writeText(markdown);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1800);
    } catch {
      setError("Could not copy the roadmap. Please select and copy the text instead.");
    }
  };

  if (!sessionId && !markdown) {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh] text-center px-4 fade-in">
        <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center mb-4">
          <Map className="w-8 h-8 text-primary" />
        </div>
        <h2 className="text-xl font-semibold text-foreground mb-2">Your Wellness Roadmap</h2>
        <p className="text-muted-foreground text-sm max-w-md text-balance mb-6">
          Aaryu can generate a structured, personalized roadmap based on your conversations.
        </p>
        <Button onClick={() => router.push("/coach")} className="bg-primary text-primary-foreground">
          Chat with Aaryu
        </Button>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh] text-center px-4 fade-in">
        <div className="relative mb-6">
          <div className="absolute inset-0 bg-primary/20 blur-xl rounded-full" />
          <Spinner className="w-8 h-8 text-primary relative" />
        </div>
        <h2 className="text-lg font-medium text-foreground mb-2">Analyzing your conversation...</h2>
        <p className="text-muted-foreground text-sm max-w-sm">
          Aaryu is building a personalized wellness roadmap based on your goals and context.
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh] text-center px-4 fade-in">
        <div className="w-12 h-12 rounded-full bg-red-500/10 flex items-center justify-center mb-4 text-red-500">
          <AlertCircle className="w-6 h-6" />
        </div>
        <p className="text-foreground font-medium mb-4">{error}</p>
        <Button variant="outline" onClick={() => router.push("/coach")}>
          Return to Chat
        </Button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 fade-in">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <Button variant="ghost" size="sm" onClick={() => router.back()} className="text-muted-foreground -ml-2">
          <ArrowLeft className="w-4 h-4 mr-1.5" />
          Back to Aaryu
        </Button>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={copyRoadmap}
            disabled={!markdown}
            className="text-xs"
          >
            {copied ? <Check className="w-3.5 h-3.5 mr-1.5" /> : <Copy className="w-3.5 h-3.5 mr-1.5" />}
            {copied ? "Copied" : "Copy roadmap"}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => sessionId && generateRoadmap(sessionId)}
            disabled={loading || !sessionId}
            className="text-xs"
          >
            <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${loading ? "animate-spin" : ""}`} />
            Regenerate
          </Button>
        </div>
      </div>

      <header className="space-y-2 border-b border-border pb-5">
        <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-[0.16em] text-primary">
          <Map className="w-3.5 h-3.5" />
          Aaryu&apos;s plan
        </div>
        <h1 className="text-2xl sm:text-3xl font-semibold tracking-tight text-foreground">
          Your wellness roadmap
        </h1>
        <p className="max-w-2xl text-sm leading-6 text-muted-foreground">
          A practical plan shaped around what you discussed. Your conversation stays available in Aaryu.
        </p>
      </header>

      <Card className="border-border bg-card shadow-sm overflow-hidden">
        <CardContent className="p-5 sm:p-8 lg:p-10 prose prose-invert prose-aarogya max-w-none">
          {markdown && <ReactMarkdown>{markdown}</ReactMarkdown>}
        </CardContent>
      </Card>
      <p className="text-center text-xs text-muted-foreground" role="status" aria-live="polite">
        {copied ? "Roadmap copied to clipboard." : "Use Copy roadmap to save this plan for later."}
      </p>
    </div>
  );
}

export default function RoadmapPage() {
  return (
    <ProtectedLayout title="Roadmap">
      <div className="p-4 sm:p-6 lg:p-8 min-h-[calc(100vh-3.5rem)]">
        <Suspense fallback={
          <div className="flex h-[60vh] items-center justify-center">
            <Spinner className="text-primary" />
          </div>
        }>
          <RoadmapContent />
        </Suspense>
      </div>
    </ProtectedLayout>
  );
}
