"use client";

import { useState, useEffect } from "react";
import { NewsCard } from "@/components/news/NewsCard";
import { api } from "@/lib/api";
import { Favorite } from "@/lib/types";
import { Loader2, Star } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";

export default function FavoritesPage() {
  const [favorites, setFavorites] = useState<Favorite[]>([]);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    fetchFavorites();
  }, []);

  const fetchFavorites = async () => {
    try {
      setLoading(true);
      const response = await api.getFavorites();
      setFavorites(response.items);
    } catch (error) {
      console.error("Failed to fetch favorites:", error);
      toast({
        title: "Error",
        description: "Failed to fetch favorites.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleFavorite = async (newsId: number, isFavorited: boolean) => {
    try {
      if (isFavorited) {
        await api.removeFavoriteByNewsId(newsId);
        // Remove from local state
        setFavorites((prev) =>
          prev.filter((f) => f.news_item.id !== newsId)
        );
        toast({ title: "Removed from favorites" });
      }
    } catch (error) {
      console.error("Failed to update favorite:", error);
      toast({
        title: "Error",
        description: "Failed to update favorites.",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Star className="w-8 h-8 text-yellow-500 fill-yellow-500" />
        <div>
          <h1 className="text-3xl font-bold">Favorites</h1>
          <p className="text-muted-foreground">
            Your saved AI news articles ({favorites.length} items)
          </p>
        </div>
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
        </div>
      ) : favorites.length === 0 ? (
        <div className="text-center py-20">
          <Star className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
          <h2 className="text-xl font-semibold mb-2">No favorites yet</h2>
          <p className="text-muted-foreground">
            Start adding news to your favorites by clicking the star icon on any news card.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {favorites.map((favorite) => (
            <NewsCard
              key={favorite.id}
              news={{ ...favorite.news_item, is_favorited: true }}
              onFavorite={handleFavorite}
            />
          ))}
        </div>
      )}
    </div>
  );
}
