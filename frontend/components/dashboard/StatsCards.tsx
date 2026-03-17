"use client";

import { DashboardStats } from "@/lib/types";
import {
  Newspaper,
  Database,
  Star,
  Share2,
  TrendingUp,
  Calendar,
  ArrowUpRight,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface StatsCardsProps {
  stats: DashboardStats;
}

export function StatsCards({ stats }: StatsCardsProps) {
  const cards = [
    {
      title: "Total News",
      value: stats.total_news.toLocaleString(),
      icon: Newspaper,
      gradient: "from-blue-500 to-cyan-500",
      shadowColor: "shadow-blue-500/20",
      trend: "+12%",
    },
    {
      title: "Active Sources",
      value: `${stats.active_sources}/${stats.total_sources}`,
      icon: Database,
      gradient: "from-green-500 to-emerald-500",
      shadowColor: "shadow-green-500/20",
      trend: "Live",
    },
    {
      title: "Favorites",
      value: stats.total_favorites.toLocaleString(),
      icon: Star,
      gradient: "from-yellow-500 to-orange-500",
      shadowColor: "shadow-yellow-500/20",
      trend: "+5",
    },
    {
      title: "Broadcasts",
      value: stats.total_broadcasts.toLocaleString(),
      icon: Share2,
      gradient: "from-purple-500 to-pink-500",
      shadowColor: "shadow-purple-500/20",
      trend: "+8%",
    },
    {
      title: "Today",
      value: stats.news_today.toLocaleString(),
      icon: Calendar,
      gradient: "from-orange-500 to-red-500",
      shadowColor: "shadow-orange-500/20",
      trend: "New",
    },
    {
      title: "This Week",
      value: stats.news_this_week.toLocaleString(),
      icon: TrendingUp,
      gradient: "from-pink-500 to-rose-500",
      shadowColor: "shadow-pink-500/20",
      trend: "+23%",
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
      {cards.map((card, index) => (
        <div
          key={card.title}
          className={cn(
            "group relative overflow-hidden rounded-2xl bg-card border border-border/50 p-5",
            "transition-all duration-300 hover:scale-[1.02] hover:shadow-xl",
            card.shadowColor
          )}
          style={{
            animationDelay: `${index * 50}ms`,
          }}
        >
          {/* Background gradient on hover */}
          <div className={cn(
            "absolute inset-0 bg-gradient-to-br opacity-0 group-hover:opacity-5 transition-opacity duration-300",
            card.gradient
          )} />
          
          {/* Content */}
          <div className="relative">
            <div className="flex items-start justify-between mb-3">
              <div className={cn(
                "p-2.5 rounded-xl bg-gradient-to-br",
                card.gradient,
                "shadow-lg"
              )}>
                <card.icon className="w-4 h-4 text-white" />
              </div>
              {card.trend && (
                <div className="flex items-center gap-0.5 text-[10px] font-medium text-green-500 bg-green-500/10 px-2 py-1 rounded-full">
                  <ArrowUpRight className="w-3 h-3" />
                  {card.trend}
                </div>
              )}
            </div>
            
            <div>
              <p className="text-2xl font-bold tracking-tight">{card.value}</p>
              <p className="text-xs text-muted-foreground mt-0.5">{card.title}</p>
            </div>
          </div>
          
          {/* Decorative corner */}
          <div className={cn(
            "absolute -bottom-4 -right-4 w-16 h-16 rounded-full bg-gradient-to-br opacity-10 blur-2xl",
            card.gradient
          )} />
        </div>
      ))}
    </div>
  );
}
