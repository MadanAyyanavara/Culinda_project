"use client";

import { useState } from "react";
import { Source } from "@/lib/types";
import { Search, Filter, SortAsc, SortDesc, X, ChevronDown, SlidersHorizontal } from "lucide-react";

interface FilterBarProps {
  sources: Source[];
  filters: {
    search: string;
    sourceIds: number[];
    sortBy: string;
    sortOrder: string;
  };
  onFilterChange: (filters: any) => void;
}

export function FilterBar({ sources, filters, onFilterChange }: FilterBarProps) {
  const [showAllSources, setShowAllSources] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onFilterChange({ ...filters, search: e.target.value });
  };

  const handleSourceToggle = (sourceId: number) => {
    const newSourceIds = filters.sourceIds.includes(sourceId)
      ? filters.sourceIds.filter((id) => id !== sourceId)
      : [...filters.sourceIds, sourceId];
    onFilterChange({ ...filters, sourceIds: newSourceIds });
  };

  const handleSortChange = (sortBy: string) => {
    if (filters.sortBy === sortBy) {
      onFilterChange({
        ...filters,
        sortOrder: filters.sortOrder === "desc" ? "asc" : "desc",
      });
    } else {
      onFilterChange({ ...filters, sortBy, sortOrder: "desc" });
    }
  };

  const clearFilters = () => {
    onFilterChange({
      search: "",
      sourceIds: [],
      sortBy: "published_at",
      sortOrder: "desc",
    });
  };

  const hasActiveFilters =
    filters.search || filters.sourceIds.length > 0;

  const displayedSources = showAllSources ? sources : sources.slice(0, 6);

  return (
    <div className="bg-card border border-border rounded-xl overflow-hidden">
      {/* Search bar - always visible */}
      <div className="p-4 border-b border-border">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search news articles... (Press / to focus)"
            value={filters.search}
            onChange={handleSearchChange}
            className="w-full pl-12 pr-4 py-3 bg-background border border-input rounded-xl focus:outline-none focus:ring-2 focus:ring-ring focus:border-primary transition-all"
          />
          {filters.search && (
            <button
              onClick={() => onFilterChange({ ...filters, search: "" })}
              className="absolute right-4 top-1/2 -translate-y-1/2 p-1 hover:bg-accent rounded-full transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Expandable filters */}
      <div className={`transition-all duration-300 ${isExpanded ? "max-h-[500px]" : "max-h-0"} overflow-hidden`}>
        <div className="p-4 space-y-4 border-b border-border">
          {/* Source filter */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Filter className="w-4 h-4 text-muted-foreground" />
                <span className="text-sm font-semibold">Filter by Source</span>
                {filters.sourceIds.length > 0 && (
                  <span className="px-2 py-0.5 bg-primary text-primary-foreground text-xs rounded-full">
                    {filters.sourceIds.length}
                  </span>
                )}
              </div>
              {filters.sourceIds.length > 0 && (
                <button
                  onClick={() => onFilterChange({ ...filters, sourceIds: [] })}
                  className="text-xs text-muted-foreground hover:text-foreground transition-colors"
                >
                  Clear
                </button>
              )}
            </div>
            <div className="flex flex-wrap gap-2">
              {displayedSources.map((source) => (
                <button
                  key={source.id}
                  onClick={() => handleSourceToggle(source.id)}
                  className={`px-3 py-1.5 text-sm rounded-full transition-all duration-200 ${
                    filters.sourceIds.includes(source.id)
                      ? "bg-primary text-primary-foreground shadow-md shadow-primary/20"
                      : "bg-secondary hover:bg-secondary/80 border border-transparent hover:border-border"
                  }`}
                >
                  {source.name}
                </button>
              ))}
              {sources.length > 6 && (
                <button
                  onClick={() => setShowAllSources(!showAllSources)}
                  className="px-3 py-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  {showAllSources ? "Show less" : `+${sources.length - 6} more`}
                </button>
              )}
            </div>
          </div>

          {/* Sort options */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <SlidersHorizontal className="w-4 h-4 text-muted-foreground" />
              <span className="text-sm font-semibold">Sort by</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {[
                { value: "published_at", label: "Date Published" },
                { value: "fetched_at", label: "Date Fetched" },
                { value: "title", label: "Title" },
              ].map((option) => (
                <button
                  key={option.value}
                  onClick={() => handleSortChange(option.value)}
                  className={`flex items-center gap-2 px-4 py-2 text-sm rounded-xl transition-all duration-200 ${
                    filters.sortBy === option.value
                      ? "bg-primary text-primary-foreground shadow-md shadow-primary/20"
                      : "bg-secondary hover:bg-secondary/80"
                  }`}
                >
                  {option.label}
                  {filters.sortBy === option.value &&
                    (filters.sortOrder === "desc" ? (
                      <SortDesc className="w-4 h-4" />
                    ) : (
                      <SortAsc className="w-4 h-4" />
                    ))}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Filter bar footer */}
      <div className="flex items-center justify-between px-4 py-3">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          <SlidersHorizontal className="w-4 h-4" />
          {isExpanded ? "Hide filters" : "Show filters"}
          <ChevronDown className={`w-4 h-4 transition-transform ${isExpanded ? "rotate-180" : ""}`} />
        </button>

        <div className="flex items-center gap-3">
          {hasActiveFilters && (
            <button
              onClick={clearFilters}
              className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-destructive hover:bg-destructive/10 rounded-lg transition-colors"
            >
              <X className="w-4 h-4" />
              Clear all
            </button>
          )}
          <span className="text-sm text-muted-foreground">
            {sources.length} sources available
          </span>
        </div>
      </div>
    </div>
  );
}
