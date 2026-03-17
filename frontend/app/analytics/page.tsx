"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { DashboardStats } from "@/lib/types";
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown, 
  Activity,
  Calendar,
  Clock,
  Newspaper,
  Share2,
  Star
} from "lucide-react";
import { StatsCardSkeleton } from "@/components/ui/skeleton";

export default function AnalyticsPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const data = await api.getStats();
      setStats(data);
    } catch (error) {
      console.error("Failed to fetch stats:", error);
    } finally {
      setLoading(false);
    }
  };

  const statCards = [
    {
      title: "Total Articles",
      value: stats?.total_news || 0,
      icon: Newspaper,
      trend: "+12%",
      trendUp: true,
      color: "from-blue-500 to-cyan-500",
    },
    {
      title: "This Week",
      value: stats?.news_this_week || 0,
      icon: Calendar,
      trend: "+23%",
      trendUp: true,
      color: "from-green-500 to-emerald-500",
    },
    {
      title: "Today",
      value: stats?.news_today || 0,
      icon: Clock,
      trend: "+5%",
      trendUp: true,
      color: "from-orange-500 to-red-500",
    },
    {
      title: "Favorites",
      value: stats?.total_favorites || 0,
      icon: Star,
      trend: "+8%",
      trendUp: true,
      color: "from-yellow-500 to-orange-500",
    },
    {
      title: "Broadcasts",
      value: stats?.total_broadcasts || 0,
      icon: Share2,
      trend: "+15%",
      trendUp: true,
      color: "from-purple-500 to-pink-500",
    },
    {
      title: "Active Sources",
      value: stats?.active_sources || 0,
      icon: Activity,
      trend: "100%",
      trendUp: true,
      color: "from-pink-500 to-rose-500",
    },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2">Analytics</h1>
        <p className="text-muted-foreground">
          Insights and statistics about your AI news consumption
        </p>
      </div>

      {/* Stats Grid */}
      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <StatsCardSkeleton key={i} />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {statCards.map((card, index) => (
            <div
              key={card.title}
              className="relative overflow-hidden rounded-2xl bg-card border border-border/50 p-6 transition-all duration-300 hover:shadow-lg hover:scale-[1.02]"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <div className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-br ${card.color} opacity-5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2`} />
              
              <div className="relative">
                <div className="flex items-start justify-between mb-4">
                  <div className={`p-3 rounded-xl bg-gradient-to-br ${card.color} shadow-lg`}>
                    <card.icon className="w-5 h-5 text-white" />
                  </div>
                  <div className={`flex items-center gap-1 text-sm font-medium ${card.trendUp ? 'text-green-500' : 'text-red-500'}`}>
                    {card.trendUp ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                    {card.trend}
                  </div>
                </div>
                
                <div>
                  <p className="text-3xl font-bold tracking-tight">{card.value.toLocaleString()}</p>
                  <p className="text-sm text-muted-foreground mt-1">{card.title}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Charts Placeholder */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="rounded-2xl bg-card border border-border/50 p-6">
          <div className="flex items-center gap-2 mb-6">
            <BarChart3 className="w-5 h-5 text-primary" />
            <h3 className="font-semibold">News Volume Over Time</h3>
          </div>
          <div className="h-64 flex items-center justify-center bg-muted/50 rounded-xl">
            <p className="text-muted-foreground">Chart coming soon</p>
          </div>
        </div>

        <div className="rounded-2xl bg-card border border-border/50 p-6">
          <div className="flex items-center gap-2 mb-6">
            <Activity className="w-5 h-5 text-primary" />
            <h3 className="font-semibold">Top Sources</h3>
          </div>
          <div className="h-64 flex items-center justify-center bg-muted/50 rounded-xl">
            <p className="text-muted-foreground">Chart coming soon</p>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="rounded-2xl bg-card border border-border/50 p-6">
        <h3 className="font-semibold mb-4">Recent Activity</h3>
        <div className="space-y-4">
          {[
            { action: "Added to favorites", item: "OpenAI Announces GPT-5", time: "2 hours ago" },
            { action: "Broadcasted via Email", item: "Google DeepMind's AlphaFold 3", time: "5 hours ago" },
            { action: "Viewed article", item: "Microsoft Copilot Surpasses 10M Users", time: "8 hours ago" },
            { action: "Added to favorites", item: "Anthropic's Claude 3 Opus", time: "1 day ago" },
          ].map((activity, i) => (
            <div key={i} className="flex items-center justify-between py-3 border-b border-border/50 last:border-0">
              <div>
                <p className="font-medium text-sm">{activity.action}</p>
                <p className="text-sm text-muted-foreground">{activity.item}</p>
              </div>
              <span className="text-xs text-muted-foreground">{activity.time}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
