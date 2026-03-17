"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  Newspaper,
  Star,
  Share2,
  Database,
  BarChart3,
  Settings,
  Sparkles,
  Zap,
} from "lucide-react";

const navItems = [
  { href: "/", label: "News Feed", icon: Newspaper, badge: "Live" },
  { href: "/favorites", label: "Favorites", icon: Star },
  { href: "/broadcast", label: "Broadcast", icon: Share2 },
  { href: "/sources", label: "Sources", icon: Database },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/settings", label: "Settings", icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-16 bottom-0 w-64 glass border-r border-border/50 overflow-y-auto z-40">
      {/* Logo area */}
      <div className="p-6 border-b border-border/50">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-blue-500 flex items-center justify-center shadow-lg shadow-primary/25">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <p className="font-bold text-sm">AI News</p>
            <p className="text-xs text-muted-foreground">Dashboard</p>
          </div>
        </div>
      </div>

      <nav className="p-4 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "group flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 relative overflow-hidden",
                isActive
                  ? "bg-primary text-primary-foreground shadow-lg shadow-primary/25"
                  : "hover:bg-accent/80 text-foreground/80 hover:text-foreground"
              )}
            >
              {/* Active indicator */}
              {isActive && (
                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-white/50 rounded-r-full" />
              )}
              
              <div className={cn(
                "p-2 rounded-lg transition-colors",
                isActive ? "bg-white/20" : "bg-muted group-hover:bg-background"
              )}>
                <item.icon className={cn(
                  "w-4 h-4 transition-transform",
                  isActive ? "" : "group-hover:scale-110"
                )} />
              </div>
              
              <span className="font-medium text-sm flex-1">{item.label}</span>
              
              {item.badge && (
                <span className="px-2 py-0.5 text-[10px] font-bold bg-green-500 text-white rounded-full animate-pulse">
                  {item.badge}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Pro upgrade card */}
      <div className="p-4 mt-4">
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-primary/20 to-blue-500/20 border border-primary/20 p-4">
          <div className="absolute top-0 right-0 w-20 h-20 bg-primary/20 rounded-full blur-2xl -translate-y-1/2 translate-x-1/2" />
          <Zap className="w-8 h-8 text-primary mb-2" />
          <p className="font-semibold text-sm mb-1">Pro Features</p>
          <p className="text-xs text-muted-foreground mb-3">Unlock AI summaries & more</p>
          <button className="w-full py-2 text-xs font-semibold bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors">
            Upgrade Now
          </button>
        </div>
      </div>

      {/* Footer */}
      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-border/50">
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          <span>20+ Sources Active</span>
        </div>
      </div>
    </aside>
  );
}
