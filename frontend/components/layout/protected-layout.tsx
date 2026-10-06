"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/auth-context";
import { AppSidebar } from "./app-sidebar";
import { TopBar } from "./top-bar";
import { Skeleton } from "@/components/ui/skeleton";

interface ProtectedLayoutProps {
  children: React.ReactNode;
  title?: string;
}

export function ProtectedLayout({ children, title }: ProtectedLayoutProps) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.replace("/login");
    }
  }, [user, loading, router]);

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="flex flex-col gap-4 w-full max-w-sm px-6">
          <Skeleton className="h-8 w-24 rounded-lg" />
          <Skeleton className="h-4 w-full rounded" />
          <Skeleton className="h-4 w-3/4 rounded" />
        </div>
      </div>
    );
  }

  if (!user) return null;

  return (
    <AppSidebar>
      <TopBar title={title} />
      <main className="flex-1 overflow-y-auto scrollbar-aarogya">
        {children}
      </main>
    </AppSidebar>
  );
}
