"use client";

import React from "react";
import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/contexts/auth-context";
import {
  SidebarProvider,
  Sidebar,
  SidebarContent,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarSeparator,
  useSidebar,
} from "@/components/ui/sidebar";
import {
  Sun,
  MessageCircle,
  Map,
  TrendingUp,
  Settings,
  User,
  LogOut,
  ChevronRight,
} from "lucide-react";
import {
  Sheet,
  SheetContent,
} from "@/components/ui/sheet";
import { getRefreshToken } from "@/lib/api";
import aarogyaLogo from "@/assets/aarogyalogo.png";

const navMain = [
  { title: "Today", href: "/today", icon: Sun },
  { title: "Aaryu", href: "/coach", icon: MessageCircle },
  { title: "Roadmap", href: "/roadmap", icon: Map },
  { title: "Progress", href: "/progress", icon: TrendingUp },
];

const navSecondary = [
  { title: "Account", href: "/account", icon: User },
  { title: "Settings", href: "/settings", icon: Settings },
];

function SidebarInner() {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const { isMobile } = useSidebar();

  const isActive = (href: string) => pathname === href || pathname.startsWith(href + "/");

  const handleLogout = async () => {
    await logout();
  };

  const userInitials = user?.name
    ? user.name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2)
    : user?.email?.[0]?.toUpperCase() ?? "A";

  return (
    <Sidebar collapsible={isMobile ? "offcanvas" : "icon"} variant="sidebar">
      {/* Logo */}
      <div className="flex h-14 items-center gap-2.5 px-3 border-b border-sidebar-border">
        <Image
          src={aarogyaLogo}
          alt=""
          width={48}
          height={48}
          className="h-9 w-9 flex-shrink-0 rounded-full object-contain"
        />
        <span className="text-sidebar-foreground font-semibold text-sm tracking-tight group-data-[collapsible=icon]:hidden">
          Aarogya
        </span>
      </div>

      <SidebarContent className="py-3">
        {/* Primary nav */}
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {navMain.map((item) => {
                const active = isActive(item.href);
                return (
                  <SidebarMenuItem key={item.title}>
                    <SidebarMenuButton
                      isActive={active}
                      onClick={() => window.location.href = item.href}
                      tooltip={item.title}
                      className={`group/nav-item relative transition-all duration-150 rounded-lg mx-2 flex items-center gap-3 px-3 py-2.5 ${
                        active
                          ? "bg-primary/10 text-primary"
                          : "text-sidebar-foreground/70 hover:text-sidebar-foreground hover:bg-sidebar-accent"
                      }`}
                    >
                      <item.icon
                        className={`w-4 h-4 flex-shrink-0 ${active ? "text-primary" : ""}`}
                      />
                      <span className="text-sm font-medium group-data-[collapsible=icon]:hidden">
                        {item.title}
                      </span>
                      {active && (
                        <div className="ml-auto w-1 h-4 bg-primary rounded-full group-data-[collapsible=icon]:hidden" />
                      )}
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarSeparator className="my-2 mx-4 bg-sidebar-border" />

        {/* Secondary nav */}
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {navSecondary.map((item) => {
                const active = isActive(item.href);
                return (
                  <SidebarMenuItem key={item.title}>
                    <SidebarMenuButton
                      isActive={active}
                      onClick={() => window.location.href = item.href}
                      tooltip={item.title}
                      className={`transition-all duration-150 rounded-lg mx-2 flex items-center gap-3 px-3 py-2.5 ${
                        active
                          ? "bg-primary/10 text-primary"
                          : "text-sidebar-foreground/50 hover:text-sidebar-foreground/80 hover:bg-sidebar-accent"
                      }`}
                    >
                      <item.icon className="w-4 h-4 flex-shrink-0" />
                      <span className="text-sm group-data-[collapsible=icon]:hidden">{item.title}</span>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      {/* Footer / user section */}
      <SidebarFooter className="border-t border-sidebar-border p-3">
        <div className="flex items-center gap-3 rounded-lg px-2 py-2 group-data-[collapsible=icon]:justify-center">
          <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-white text-xs font-semibold flex-shrink-0">
            {userInitials}
          </div>
          <div className="min-w-0 flex-1 group-data-[collapsible=icon]:hidden">
            <div className="text-sidebar-foreground text-xs font-medium truncate">
              {user?.name || "User"}
            </div>
            <div className="text-sidebar-foreground/40 text-xs truncate">
              {user?.email}
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="text-sidebar-foreground/30 hover:text-red-400 transition-colors p-1 rounded group-data-[collapsible=icon]:hidden"
            title="Sign out"
            aria-label="Sign out"
          >
            <LogOut className="w-3.5 h-3.5" />
          </button>
        </div>
      </SidebarFooter>
    </Sidebar>
  );
}

export function AppSidebar({ children }: { children: React.ReactNode }) {
  return (
    <SidebarProvider defaultOpen>
      <div className="flex h-screen w-full overflow-hidden">
        <SidebarInner />
        <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
          {children}
        </div>
      </div>
    </SidebarProvider>
  );
}
