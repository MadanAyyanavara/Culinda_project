"use client";

import { useState } from "react";
import { NewsItem } from "@/lib/types";
import { formatDate, truncateText } from "@/lib/utils";
import { BroadcastModal } from "./BroadcastModal";
import {
  Star,
  ExternalLink,
  Share2,
  Calendar,
  User,
  Tag,
  Sparkles,
  Clock,
  Bookmark,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface NewsCardProps {
  news: NewsItem;
  onFavorite: (newsId: number, isFavorited: boolean) => void;
}

export function NewsCard({ news, onFavorite }: NewsCardProps) {
  const [showBroadcast, setShowBroadcast] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [imageLoaded, setImageLoaded] = useState(false);
  const [isFavoriting, setIsFavoriting] = useState(false);

  const handleFavoriteClick = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (isFavoriting) return;
    
    setIsFavoriting(true);
    await onFavorite(news.id, news.is_favorited);
    setIsFavoriting(false);
  };

  const isNew = () => {
    if (!news.published_at) return false;
    const published = new Date(news.published_at);
    const hoursAgo = (Date.now() - published.getTime()) / (1000 * 60 * 60);
    return hoursAgo < 24;
  };

  return (
    <>
      <div
        className={cn(
          "group relative overflow-hidden rounded-2xl bg-card border border-border/50",
          "transition-all duration-300 ease-out cursor-pointer",
          "hover:shadow-2xl hover:shadow-primary/10 hover:border-primary/30",
          "hover:-translate-y-1"
        )}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        {/* Image */}
        <div className="relative h-48 overflow-hidden">
          {news.image_url ? (
            <>
              {!imageLoaded && (
                <div className="absolute inset-0 shimmer" />
              )}
              <img
                src={news.image_url}
                alt={news.title}
                className={cn(
                  "w-full h-full object-cover transition-all duration-500",
                  isHovered ? "scale-110" : "scale-100",
                  imageLoaded ? "opacity-100" : "opacity-0"
                )}
                onLoad={() => setImageLoaded(true)}
                onError={(e) => {
                  (e.target as HTMLImageElement).style.display = "none";
                }}
              />
            </>
          ) : (
            <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-primary/10 to-blue-500/5 flex items-center justify-center">
              <div className="text-center">
                <Sparkles className="w-12 h-12 text-primary/30 mx-auto mb-2" />
                <span className="text-xs text-muted-foreground">AI News</span>
              </div>
            </div>
          )}
          
          {/* Overlays */}
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
          
          {/* New badge */}
          {isNew() && (
            <div className="absolute top-3 left-3 flex items-center gap-1.5 px-3 py-1.5 bg-gradient-to-r from-emerald-400 to-teal-500 text-white text-xs font-bold rounded-full shadow-lg shadow-emerald-500/30">
              <Clock className="w-3 h-3" />
              New
            </div>
          )}

          {/* AI Summary badge */}
          {news.ai_summary && (
            <div className="absolute top-3 right-3 px-2.5 py-1 bg-gradient-to-r from-violet-500 to-purple-600 text-white text-[10px] font-bold rounded-lg backdrop-blur-sm shadow-lg shadow-purple-500/30">
              AI Summary
            </div>
          )}

          {/* Hover actions */}
          <div className="absolute bottom-3 left-3 right-3 flex items-center justify-between opacity-0 group-hover:opacity-100 transition-all duration-300 translate-y-2 group-hover:translate-y-0">
            <div className="flex gap-2">
              {/* Favorite Button */}
              <button
                onClick={handleFavoriteClick}
                disabled={isFavoriting}
                className={cn(
                  "p-2.5 rounded-xl backdrop-blur-md transition-all duration-200 shadow-lg",
                  news.is_favorited
                    ? "bg-gradient-to-br from-amber-400 to-orange-500 text-white shadow-orange-500/30"
                    : "bg-white/95 text-amber-500 hover:bg-white hover:shadow-xl hover:shadow-amber-500/20 hover:scale-105"
                )}
              >
                <Star className={cn("w-4 h-4", news.is_favorited && "fill-current")} />
              </button>
              {/* Share Button */}
              <button
                onClick={() => setShowBroadcast(true)}
                className="p-2.5 rounded-xl bg-gradient-to-br from-primary to-blue-600 text-white backdrop-blur-md transition-all duration-200 shadow-lg shadow-primary/30 hover:shadow-xl hover:shadow-primary/40 hover:scale-105"
              >
                <Share2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        <div className="p-5">
          {/* Source & Category */}
          <div className="flex items-center gap-2 mb-3">
            <span className="px-2.5 py-1 text-xs font-semibold bg-gradient-to-r from-primary/10 to-blue-500/10 text-primary rounded-lg border border-primary/20">
              {news.source?.name || "Unknown"}
            </span>
            {news.source?.category && (
              <span className="flex items-center gap-1 text-xs text-muted-foreground">
                <Tag className="w-3 h-3" />
                {news.source.category}
              </span>
            )}
          </div>

          {/* Title */}
          <h3 className="font-bold text-lg mb-3 line-clamp-2 group-hover:text-primary transition-colors duration-200">
            {news.title}
          </h3>

          {/* Summary */}
          {news.summary && (
            <p className="text-muted-foreground text-sm mb-4 line-clamp-2 leading-relaxed">
              {truncateText(news.summary, 140)}
            </p>
          )}

          {/* AI Summary */}
          {news.ai_summary && (
            <div className="mb-4 p-3 rounded-xl bg-gradient-to-r from-primary/5 to-blue-500/5 border border-primary/10">
              <div className="flex items-center gap-1.5 mb-1">
                <Sparkles className="w-3.5 h-3.5 text-primary" />
                <span className="text-xs font-semibold text-primary">AI Summary</span>
              </div>
              <p className="text-xs text-muted-foreground line-clamp-2">
                {news.ai_summary}
              </p>
            </div>
          )}

          {/* Meta */}
          <div className="flex items-center gap-4 text-xs text-muted-foreground">
            <span className="flex items-center gap-1.5">
              <Calendar className="w-3.5 h-3.5" />
              {formatDate(news.published_at)}
            </span>
            {news.author && (
              <span className="flex items-center gap-1.5 truncate">
                <User className="w-3.5 h-3.5" />
                {truncateText(news.author, 15)}
              </span>
            )}
          </div>

          {/* Read more link */}
          <a
            href={news.url}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-4 flex items-center justify-center gap-2 w-full py-2.5 rounded-xl bg-muted hover:bg-primary hover:text-primary-foreground transition-all duration-200 text-sm font-medium group/link"
          >
            Read Article
            <ExternalLink className="w-4 h-4 transition-transform group-hover/link:translate-x-0.5 group-hover/link:-translate-y-0.5" />
          </a>
        </div>
      </div>

      <BroadcastModal
        news={news}
        open={showBroadcast}
        onClose={() => setShowBroadcast(false)}
      />
    </>
  );
}
