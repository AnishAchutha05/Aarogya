"use client";

import React, { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/auth-context";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { User, Settings, Key, LogOut } from "lucide-react";

export function TopBar({ title }: { title?: string }) {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  const userInitials = user?.name
    ? user.name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2)
    : user?.email?.[0]?.toUpperCase() ?? "A";

  const handleLogout = async () => {
    setMenuOpen(false);
    await logout();
    router.push("/login");
  };

  // Close menu on outside click
  useEffect(() => {
    if (!menuOpen) return;
    const handleClick = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [menuOpen]);

  const menuItems = [
    { label: "Account", icon: User, href: "/account" },
    { label: "Settings", icon: Settings, href: "/settings" },
    { label: "AI Provider", icon: Key, href: "/settings/ai-provider" },
  ];

  return (
    <div className="h-14 flex items-center justify-between px-4 border-b border-border bg-card/30 backdrop-blur-sm flex-shrink-0">
      <div className="flex items-center gap-3">
        <SidebarTrigger className="text-muted-foreground hover:text-foreground transition-colors -ml-1" />
        {title && (
          <h1 className="text-sm font-medium text-foreground/70">{title}</h1>
        )}
      </div>

      {/* Right side */}
      <div className="relative" ref={menuRef}>
        <button
          onClick={() => setMenuOpen(!menuOpen)}
          className={`w-8 h-8 rounded-full bg-primary flex items-center justify-center text-white text-xs font-semibold transition-all duration-150 ${
            menuOpen ? "ring-2 ring-primary/40" : "hover:ring-2 hover:ring-primary/20"
          }`}
          aria-label="Account menu"
          aria-expanded={menuOpen}
        >
          {userInitials}
        </button>

        {menuOpen && (
          <div className="absolute right-0 top-10 w-52 bg-popover rounded-xl border border-border shadow-xl z-50 overflow-hidden fade-in">
            {/* User info */}
            <div className="px-3 py-3 border-b border-border">
              <div className="text-sm font-medium text-foreground truncate">{user?.name || "User"}</div>
              <div className="text-xs text-muted-foreground truncate">{user?.email}</div>
            </div>

            {/* Menu items */}
            <div className="py-1">
              {menuItems.map((item) => (
                <button
                  key={item.label}
                  onClick={() => { setMenuOpen(false); router.push(item.href); }}
                  className="w-full flex items-center gap-2.5 px-3 py-2 text-sm text-foreground/80 hover:bg-muted hover:text-foreground transition-colors"
                >
                  <item.icon className="w-3.5 h-3.5 text-muted-foreground" />
                  {item.label}
                </button>
              ))}
            </div>

            {/* Divider + Logout */}
            <div className="border-t border-border py-1">
              <button
                onClick={handleLogout}
                className="w-full flex items-center gap-2.5 px-3 py-2 text-sm text-red-400 hover:bg-red-500/10 hover:text-red-300 transition-colors"
              >
                <LogOut className="w-3.5 h-3.5" />
                Sign out
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
