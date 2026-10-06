"use client";

import React, { useState, useEffect } from "react";
import { ProtectedLayout } from "@/components/layout/protected-layout";
import { aiProviderService } from "@/lib/services/ai-provider";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";
import { Check, Trash2, Key, AlertCircle } from "lucide-react";
import type { ProviderResponse } from "@/types";

export default function AIProviderPage() {
  const [providers, setProviders] = useState<ProviderResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [providerName, setProviderName] = useState("gemini");
  const [apiKey, setApiKey] = useState("");
  const [adding, setAdding] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadProviders = async () => {
    setLoading(true);
    try {
      const data = await aiProviderService.listProviders();
      setProviders(data);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProviders();
  }, []);

  const handleAdd = async () => {
    if (!apiKey) return;
    setAdding(true);
    setError(null);
    try {
      await aiProviderService.addProvider(providerName, apiKey);
      setApiKey("");
      await loadProviders();
    } catch (err: any) {
      setError(err.message || "Failed to add provider");
    } finally {
      setAdding(false);
    }
  };

  const handleActivate = async (pName: string) => {
    try {
      await aiProviderService.setActiveProvider(pName);
      await loadProviders();
    } catch {}
  };

  const handleDelete = async (pName: string) => {
    try {
      await aiProviderService.removeProvider(pName);
      await loadProviders();
    } catch {}
  };

  if (loading) {
    return (
      <ProtectedLayout title="AI Provider Settings">
        <div className="flex h-[50vh] items-center justify-center">
          <Spinner className="text-primary" />
        </div>
      </ProtectedLayout>
    );
  }

  return (
    <ProtectedLayout title="AI Provider Settings">
      <div className="max-w-2xl mx-auto p-4 sm:p-6 lg:p-8 space-y-6 fade-in">
        
        <Card>
          <CardHeader>
            <CardTitle>Add AI Provider</CardTitle>
            <CardDescription>
              We securely encrypt and store your API key. Aarogya uses this key to communicate with Aaryu.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {error && (
              <div className="p-3 rounded bg-red-500/10 border border-red-500/20 flex items-center gap-2 text-sm text-red-500">
                <AlertCircle className="w-4 h-4" />
                {error}
              </div>
            )}
            <div className="grid gap-2">
              <label className="text-xs font-medium text-muted-foreground uppercase">Provider</label>
              <select 
                value={providerName} 
                onChange={e => setProviderName(e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <option value="gemini">Google Gemini (Recommended)</option>
                <option value="openai">OpenAI</option>
                <option value="anthropic">Anthropic</option>
              </select>
            </div>
            <div className="grid gap-2">
              <label className="text-xs font-medium text-muted-foreground uppercase">API Key</label>
              <Input 
                type="password" 
                placeholder="Enter your API key" 
                value={apiKey} 
                onChange={e => setApiKey(e.target.value)} 
              />
            </div>
            <Button onClick={handleAdd} disabled={!apiKey || adding} className="bg-primary text-primary-foreground mt-2">
              {adding ? <Spinner className="w-4 h-4 mr-2" /> : <Key className="w-4 h-4 mr-2" />}
              Save API Key
            </Button>
          </CardContent>
        </Card>

        <h2 className="text-lg font-semibold mt-8 mb-4">Configured Providers</h2>
        <div className="space-y-3">
          {providers.length === 0 ? (
            <div className="text-sm text-muted-foreground bg-muted p-4 rounded-xl text-center">
              No API keys configured yet.
            </div>
          ) : (
            providers.map(p => (
              <Card key={p.id} className={p.is_active ? "border-primary bg-primary/5" : ""}>
                <CardContent className="p-4 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center">
                      <Key className="w-4 h-4 text-muted-foreground" />
                    </div>
                    <div>
                      <div className="text-sm font-medium capitalize">{p.provider}</div>
                      <div className="text-xs text-muted-foreground">
                        Added {new Date(p.created_at).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {p.is_active ? (
                      <div className="flex items-center gap-1.5 px-2 py-1 rounded bg-primary/20 text-primary text-xs font-medium">
                        <Check className="w-3.5 h-3.5" /> Active
                      </div>
                    ) : (
                      <Button variant="outline" size="sm" onClick={() => handleActivate(p.provider)}>
                        Activate
                      </Button>
                    )}
                    <Button variant="ghost" size="icon" onClick={() => handleDelete(p.provider)} className="text-muted-foreground hover:text-red-500">
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>

      </div>
    </ProtectedLayout>
  );
}
