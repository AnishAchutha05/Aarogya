"use client";

import React from "react";
import Link from "next/link";
import { ProtectedLayout } from "@/components/layout/protected-layout";
import { useAuth } from "@/contexts/auth-context";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { User, Key, LogOut, ChevronRight } from "lucide-react";
import { useRouter } from "next/navigation";

export default function SettingsPage() {
  const { logout } = useAuth();
  const router = useRouter();

  const handleLogout = async () => {
    await logout();
    router.push("/login");
  };

  const menu = [
    { label: "Account Profile", desc: "Update your personal and biological information", icon: User, href: "/account" },
    { label: "AI Provider", desc: "Manage your API keys for the AI models", icon: Key, href: "/settings/ai-provider" },
  ];

  return (
    <ProtectedLayout title="Settings">
      <div className="max-w-3xl mx-auto p-4 sm:p-6 lg:p-8 space-y-6 fade-in">
        <h1 className="text-2xl font-semibold mb-4">Settings</h1>
        
        <div className="flex flex-col gap-3">
          {menu.map(item => (
            <Link key={item.href} href={item.href}>
              <Card className="hover:border-primary/50 transition-colors group cursor-pointer">
                <CardContent className="p-4 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-full bg-muted flex items-center justify-center group-hover:bg-primary/10 transition-colors">
                      <item.icon className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors" />
                    </div>
                    <div>
                      <div className="text-base font-medium text-foreground">{item.label}</div>
                      <div className="text-sm text-muted-foreground">{item.desc}</div>
                    </div>
                  </div>
                  <ChevronRight className="w-5 h-5 text-muted-foreground group-hover:text-foreground transition-colors" />
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>

        <div className="pt-8">
          <Button variant="outline" className="w-full sm:w-auto text-red-500 hover:text-red-600 hover:bg-red-50" onClick={handleLogout}>
            <LogOut className="w-4 h-4 mr-2" />
            Sign Out
          </Button>
        </div>
      </div>
    </ProtectedLayout>
  );
}
