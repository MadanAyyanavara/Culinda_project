"use client";

import { useState, useEffect } from "react";
import { NewsCard } from "@/components/news/NewsCard";
import { FilterBar } from "@/components/news/FilterBar";
import { StatsCards } from "@/components/dashboard/StatsCards";
import { NewsCardSkeleton, StatsCardSkeleton } from "@/components/ui/skeleton";
import { api } from "@/lib/api";
import { NewsItem, Source, DashboardStats } from "@/lib/types";
import { RefreshCw, Newspaper, TrendingUp, Sparkles, ArrowRight } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";

export default function Home() {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [sources, setSources] = useState<Source[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [filters, setFilters] = useState({
    search: "",
    sourceIds: [] as number[],
    sortBy: "published_at",
    sortOrder: "desc",
  });
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const { toast } = useToast();

  useEffect(() => {
    fetchData();
    fetchSources();
    fetchStats();
  }, []);

  useEffect(() => {
    fetchData();
  }, [filters, page]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await api.getNews({
        page,
        page_size: 20,
        search: filters.search || undefined,
        source_ids: filters.sourceIds.length > 0 ? filters.sourceIds.join(",") : undefined,
        sort_by: filters.sortBy,
        sort_order: filters.sortOrder,
      });
      setNews(response.items);
      setTotalPages(response.total_pages);
    } catch (error) {
      console.error("Failed to fetch news:", error);
      toast({
        title: "Error",
        description: "Failed to fetch news. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchSources = async () => {
    try {
      const data = await api.getSources();
      setSources(data);
    } catch (error) {
      console.error("Failed to fetch sources:", error);
    }
  };

  const fetchStats = async () => {
    try {
      const data = await api.getStats();
      setStats(data);
    } catch (error) {
      console.error("Failed to fetch stats:", error);
    }
  };

  const handleRefresh = async () => {
    try {
      setRefreshing(true);
      await api.refreshNews();
      toast({
        title: "Success",
        description: "News feed refreshed successfully!",
        variant: "success",
      });
      fetchData();
      fetchStats();
    } catch (error) {
      console.error("Failed to refresh:", error);
      toast({
        title: "Error",
        description: "Failed to refresh news feed.",
        variant: "destructive",
      });
    } finally {
      setRefreshing(false);
    }
  };

  const handleFavorite = async (newsId: number, isFavorited: boolean) => {
    try {
      if (isFavorited) {
        await api.removeFavoriteByNewsId(newsId);
        toast({ 
          title: "Removed from favorites",
          description: "The article has been removed from your favorites.",
          variant: "default",
        });
      } else {
        await api.addFavorite(newsId);
        toast({ 
          title: "Added to favorites",
          description: "The article has been saved to your favorites.",
          variant: "success",
        });
      }
      setNews(prev =>
        prev.map(item =>
          item.id === newsId ? { ...item, is_favorited: !isFavorited } : item
        )
      );
      fetchStats();
    } catch (error) {
      console.error("Failed to update favorite:", error);
      toast({
        title: "Error",
        description: "Failed to update favorites.",
        variant: "destructive",
      });
    }
  };

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "r") {
        e.preventDefault();
        handleRefresh();
      }
      if (e.key === "/" && !e.ctrlKey && !e.metaKey) {
        e.preventDefault();
        const searchInput = document.querySelector('input[type="text"]') as HTMLInputElement;
        searchInput?.focus();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-primary/10 via-primary/5 to-blue-500/10 border border-primary/10">
        {/* Background decorative elements */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-primary/20 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3" />
        <div className="absolute bottom-0 left-0 w-64 h-64 bg-blue-500/20 rounded-full blur-3xl translate-y-1/2 -translate-x-1/3" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full bg-gradient-to-r from-transparent via-primary/5 to-transparent" />
        
        {/* Content */}
        <div className="relative px-8 py-10 md:px-12 md:py-12">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-8">
            {/* Left side - Text content */}
            <div className="flex-1 max-w-2xl">
              {/* Badges */}
              <div className="flex flex-wrap items-center gap-2 mb-4">
                <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-green-500/10 text-green-600 dark:text-green-400 text-xs font-semibold border border-green-500/20">
                  <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
                  Live Feed
                </span>
                <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-primary/10 text-primary text-xs font-medium border border-primary/20">
                  <Sparkles className="w-3 h-3" />
                  AI Powered
                </span>
                <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-blue-500/10 text-blue-600 dark:text-blue-400 text-xs font-medium border border-blue-500/20">
                  <Newspaper className="w-3 h-3" />
                  {sources.length}+ Sources
                </span>
              </div>
              
              {/* Title */}
              <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold tracking-tight mb-3">
                <span className="bg-gradient-to-r from-primary via-primary to-blue-500 bg-clip-text text-transparent">
                  AI News
                </span>{" "}
                <span className="text-foreground">Dashboard</span>
              </h1>
              
              {/* Description */}
              <p className="text-base md:text-lg text-muted-foreground max-w-xl leading-relaxed">
                Stay ahead with the latest AI news from {sources.length}+ curated sources. 
                Aggregated, deduplicated, and delivered to you in real-time.
              </p>
            </div>
            
            {/* Right side - Action button */}
            <div className="flex items-center gap-4 lg:pl-8">
              <button
                onClick={handleRefresh}
                disabled={refreshing}
                className="group flex items-center gap-3 px-8 py-4 bg-primary text-primary-foreground rounded-2xl hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 shadow-xl shadow-primary/25 hover:shadow-2xl hover:shadow-primary/30 hover:-translate-y-1 active:translate-y-0"
              >
                <RefreshCw className={`w-5 h-5 ${refreshing ? "animate-spin" : "group-hover:rotate-180 transition-transform duration-500"}`} />
                <span className="font-semibold">Refresh Feed</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Stats */}
      {stats ? (
        <StatsCards stats={stats} />
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          {[...Array(6)].map((_, i) => (
            <StatsCardSkeleton key={i} />
          ))}
        </div>
      )}

      {/* Filters */}
      <FilterBar
        sources={sources}
        filters={filters}
        onFilterChange={setFilters}
      />

      {/* News Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <NewsCardSkeleton key={i} />
          ))}
        </div>
      ) : news.length === 0 ? (
        <div className="text-center py-20">
          <div className="inline-flex items-center justify-center w-24 h-24 rounded-3xl bg-gradient-to-br from-muted to-muted/50 mb-6">
            <Newspaper className="w-12 h-12 text-muted-foreground/50" />
          </div>
          <h3 className="text-xl font-semibold mb-2">No news found</h3>
          <p className="text-muted-foreground max-w-md mx-auto mb-6">
            Try adjusting your filters or refresh the feed to get the latest news from our sources.
          </p>
          <button
            onClick={handleRefresh}
            className="inline-flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh Now
          </button>
        </div>
      ) : (
        <>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-lg bg-primary/10">
                <TrendingUp className="w-5 h-5 text-primary" />
              </div>
              <div>
                <span className="font-semibold">{news.length}</span>
                <span className="text-muted-foreground ml-1">articles found</span>
              </div>
            </div>
            <button
              onClick={() => setPage(1)}
              className="text-sm text-muted-foreground hover:text-foreground transition-colors flex items-center gap-1"
            >
              View latest
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {news.map((item, index) => (
              <div
                key={item.id}
                className="animate-in"
                style={{ animationDelay: `${index * 50}ms` }}
              >
                <NewsCard
                  news={item}
                  onFavorite={handleFavorite}
                />
              </div>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-10">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-5 py-2.5 border rounded-xl disabled:opacity-50 hover:bg-accent transition-colors font-medium"
              >
                Previous
              </button>
              <div className="flex items-center gap-1">
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  const pageNum = i + 1;
                  return (
                    <button
                      key={pageNum}
                      onClick={() => setPage(pageNum)}
                      className={`w-10 h-10 rounded-xl transition-all duration-200 font-medium ${
                        page === pageNum
                          ? "bg-primary text-primary-foreground shadow-lg shadow-primary/25"
                          : "hover:bg-accent"
                      }`}
                    >
                      {pageNum}
                    </button>
                  );
                })}
                {totalPages > 5 && (
                  <span className="px-2 text-muted-foreground">...</span>
                )}
              </div>
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="px-5 py-2.5 border rounded-xl disabled:opacity-50 hover:bg-accent transition-colors font-medium"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}

      {/* Keyboard shortcuts hint */}
      <div className="fixed bottom-4 right-4 hidden lg:flex items-center gap-4 text-xs text-muted-foreground glass px-4 py-2.5 rounded-xl">
        <span className="flex items-center gap-1">
          <kbd className="px-1.5 py-0.5 bg-muted rounded-md text-[10px] font-mono">Ctrl</kbd>
          <span>+</span>
          <kbd className="px-1.5 py-0.5 bg-muted rounded-md text-[10px] font-mono">R</kbd>
          <span className="ml-1">Refresh</span>
        </span>
        <span className="w-px h-3 bg-border" />
        <span className="flex items-center gap-1">
          <kbd className="px-1.5 py-0.5 bg-muted rounded-md text-[10px] font-mono">/</kbd>
          <span className="ml-1">Search</span>
        </span>
      </div>
    </div>
  );
}
