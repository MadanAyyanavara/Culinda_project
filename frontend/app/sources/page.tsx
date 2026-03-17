"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { Source } from "@/lib/types";
import { Loader2, Database, RefreshCw, ExternalLink, Check, X } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import { formatDate } from "@/lib/utils";

export default function SourcesPage() {
  const [sources, setSources] = useState<Source[]>([]);
  const [loading, setLoading] = useState(true);
  const [initializing, setInitializing] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    fetchSources();
  }, []);

  const fetchSources = async () => {
    try {
      setLoading(true);
      const data = await api.getSources();
      setSources(data);
    } catch (error) {
      console.error("Failed to fetch sources:", error);
      toast({
        title: "Error",
        description: "Failed to fetch sources.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleInitialize = async () => {
    try {
      setInitializing(true);
      await api.initializeSources();
      toast({ title: "Sources initialized successfully!" });
      fetchSources();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to initialize sources.",
        variant: "destructive",
      });
    } finally {
      setInitializing(false);
    }
  };

  const categories = Array.from(new Set(sources.map((s: Source) => s.category))).filter(Boolean) as string[];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Database className="w-8 h-8 text-primary" />
          <div>
            <h1 className="text-3xl font-bold">News Sources</h1>
            <p className="text-muted-foreground">
              {sources.length} sources configured ({sources.filter((s) => s.active).length} active)
            </p>
          </div>
        </div>
        <button
          onClick={handleInitialize}
          disabled={initializing}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${initializing ? "animate-spin" : ""}`} />
          {initializing ? "Initializing..." : "Initialize Sources"}
        </button>
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
        </div>
      ) : sources.length === 0 ? (
        <div className="text-center py-20">
          <Database className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
          <h2 className="text-xl font-semibold mb-2">No sources configured</h2>
          <p className="text-muted-foreground mb-4">
            Click "Initialize Sources" to add the default 20+ AI news sources.
          </p>
        </div>
      ) : (
        <div className="space-y-8">
          {categories.map((category) => (
            <div key={category}>
              <h2 className="text-xl font-semibold mb-4 capitalize">{category}</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {sources
                  .filter((s) => s.category === category)
                  .map((source) => (
                    <div
                      key={source.id}
                      className="bg-card border border-border rounded-lg p-4"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-center gap-3">
                          {source.icon_url && (
                            <img
                              src={source.icon_url}
                              alt={source.name}
                              className="w-8 h-8 rounded"
                              onError={(e) => {
                                (e.target as HTMLImageElement).style.display = "none";
                              }}
                            />
                          )}
                          <div>
                            <h3 className="font-medium">{source.name}</h3>
                            <span className="text-xs text-muted-foreground capitalize">
                              {source.type}
                            </span>
                          </div>
                        </div>
                        <span
                          className={`flex items-center gap-1 text-xs px-2 py-1 rounded-full ${
                            source.active
                              ? "bg-green-100 text-green-700"
                              : "bg-red-100 text-red-700"
                          }`}
                        >
                          {source.active ? (
                            <Check className="w-3 h-3" />
                          ) : (
                            <X className="w-3 h-3" />
                          )}
                          {source.active ? "Active" : "Inactive"}
                        </span>
                      </div>
                      {source.description && (
                        <p className="text-sm text-muted-foreground mt-2">
                          {source.description}
                        </p>
                      )}
                      <div className="flex items-center justify-between mt-4 pt-3 border-t border-border">
                        <span className="text-xs text-muted-foreground">
                          Last fetched: {formatDate(source.last_fetched)}
                        </span>
                        <a
                          href={source.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-1 text-xs text-primary hover:underline"
                        >
                          Visit
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
