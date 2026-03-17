"use client";

import { useState } from "react";
import { NewsItem, BroadcastPlatform } from "@/lib/types";
import { api } from "@/lib/api";
import { useToast } from "@/components/ui/use-toast";
import {
  X,
  Mail,
  Linkedin,
  MessageCircle,
  FileText,
  Newspaper,
  Loader2,
  Copy,
  ExternalLink,
  Sparkles,
} from "lucide-react";

interface BroadcastModalProps {
  news: NewsItem;
  open: boolean;
  onClose: () => void;
}

const platforms = [
  { id: "email" as BroadcastPlatform, name: "Email", icon: Mail, needsRecipient: true },
  { id: "linkedin" as BroadcastPlatform, name: "LinkedIn", icon: Linkedin, needsRecipient: false },
  { id: "whatsapp" as BroadcastPlatform, name: "WhatsApp", icon: MessageCircle, needsRecipient: false },
  { id: "blog" as BroadcastPlatform, name: "Blog", icon: FileText, needsRecipient: false },
  { id: "newsletter" as BroadcastPlatform, name: "Newsletter", icon: Newspaper, needsRecipient: false },
];

export function BroadcastModal({ news, open, onClose }: BroadcastModalProps) {
  const [selectedPlatform, setSelectedPlatform] = useState<BroadcastPlatform | null>(null);
  const [recipient, setRecipient] = useState("");
  const [customMessage, setCustomMessage] = useState("");
  const [generatedContent, setGeneratedContent] = useState("");
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const { toast } = useToast();

  if (!open) return null;

  const handleGenerateContent = async () => {
    if (!selectedPlatform) return;

    try {
      setGenerating(true);
      const result = await api.generateContent(news.id, selectedPlatform);
      setGeneratedContent(result.content);
      toast({ title: "Content generated!", description: `${result.character_count} characters` });
    } catch (error) {
      toast({ title: "Error", description: "Failed to generate content", variant: "destructive" });
    } finally {
      setGenerating(false);
    }
  };

  const handleBroadcast = async () => {
    if (!selectedPlatform) {
      toast({ title: "Error", description: "Please select a platform", variant: "destructive" });
      return;
    }

    const platform = platforms.find((p) => p.id === selectedPlatform);
    if (platform?.needsRecipient && !recipient) {
      toast({ title: "Error", description: "Please enter a recipient", variant: "destructive" });
      return;
    }

    try {
      setLoading(true);
      const result = await api.broadcast({
        news_item_id: news.id,
        platform: selectedPlatform,
        recipient: recipient || undefined,
        custom_message: customMessage || undefined,
        generate_ai_content: true,
      });

      if (result.status === "sent") {
        toast({ title: "Success!", description: `Broadcast to ${selectedPlatform} completed` });

        // If it's LinkedIn or WhatsApp, we might have a share URL
        if (selectedPlatform === "linkedin" || selectedPlatform === "whatsapp") {
          // Open share URL in new tab
          const shareUrl =
            selectedPlatform === "linkedin"
              ? `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(news.url)}`
              : `https://wa.me/?text=${encodeURIComponent(`${news.title}

${news.summary}

${news.url}`)}`;
          window.open(shareUrl, "_blank");
        }

        onClose();
      } else {
        toast({
          title: "Broadcast initiated",
          description: result.content ? "Content generated. Copy and share!" : "Check your email/platform",
        });
        if (result.content) {
          setGeneratedContent(result.content);
        }
      }
    } catch (error) {
      toast({ title: "Error", description: "Failed to broadcast", variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      toast({ title: "Copied to clipboard!" });
    } catch {
      toast({ title: "Failed to copy", variant: "destructive" });
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />

      {/* Modal */}
      <div className="relative bg-card rounded-lg shadow-xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-border">
          <h2 className="text-lg font-semibold">Broadcast News</h2>
          <button onClick={onClose} className="p-1 hover:bg-accent rounded">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4 space-y-4">
          {/* News preview */}
          <div className="p-3 bg-muted rounded-lg">
            <p className="font-medium text-sm line-clamp-2">{news.title}</p>
            <p className="text-xs text-muted-foreground mt-1">{news.source?.name}</p>
          </div>

          {/* Platform selection */}
          <div>
            <label className="text-sm font-medium mb-2 block">Select Platform</label>
            <div className="grid grid-cols-5 gap-2">
              {platforms.map((platform) => (
                <button
                  key={platform.id}
                  onClick={() => {
                    setSelectedPlatform(platform.id);
                    setGeneratedContent("");
                  }}
                  className={`flex flex-col items-center gap-1 p-3 rounded-lg border transition-colors ${
                    selectedPlatform === platform.id
                      ? "border-primary bg-primary/10"
                      : "border-border hover:border-primary/50"
                  }`}
                >
                  <platform.icon className="w-5 h-5" />
                  <span className="text-xs">{platform.name}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Recipient input for email */}
          {selectedPlatform === "email" && (
            <div>
              <label className="text-sm font-medium mb-2 block">Recipient Email</label>
              <input
                type="email"
                value={recipient}
                onChange={(e) => setRecipient(e.target.value)}
                placeholder="Enter email address"
                className="w-full px-3 py-2 bg-background border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-ring"
              />
            </div>
          )}

          {/* Custom message */}
          <div>
            <label className="text-sm font-medium mb-2 block">Custom Message (Optional)</label>
            <textarea
              value={customMessage}
              onChange={(e) => setCustomMessage(e.target.value)}
              placeholder="Add a personal message..."
              rows={3}
              className="w-full px-3 py-2 bg-background border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-ring resize-none"
            />
          </div>

          {/* Generate AI content button */}
          {selectedPlatform && (
            <button
              onClick={handleGenerateContent}
              disabled={generating}
              className="flex items-center gap-2 px-4 py-2 bg-secondary text-secondary-foreground rounded-lg hover:bg-secondary/80 disabled:opacity-50 w-full justify-center"
            >
              {generating ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Sparkles className="w-4 h-4" />
              )}
              {generating ? "Generating..." : "Generate AI Content"}
            </button>
          )}

          {/* Generated content preview */}
          {generatedContent && (
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium">Generated Content</label>
                <button
                  onClick={() => copyToClipboard(generatedContent)}
                  className="flex items-center gap-1 text-xs text-primary hover:underline"
                >
                  <Copy className="w-3 h-3" />
                  Copy
                </button>
              </div>
              <div className="p-3 bg-muted rounded-lg text-sm whitespace-pre-wrap max-h-40 overflow-y-auto">
                {generatedContent}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-2 p-4 border-t border-border">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-input rounded-lg hover:bg-accent"
          >
            Cancel
          </button>
          <button
            onClick={handleBroadcast}
            disabled={!selectedPlatform || loading}
            className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50"
          >
            {loading && <Loader2 className="w-4 h-4 animate-spin" />}
            {selectedPlatform === "linkedin" || selectedPlatform === "whatsapp" ? (
              <>
                Open {selectedPlatform}
                <ExternalLink className="w-4 h-4" />
              </>
            ) : (
              "Broadcast"
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
