"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { BroadcastResponse } from "@/lib/types";
import { Loader2, Share2, Mail, Linkedin, MessageCircle, FileText, Newspaper, CheckCircle, XCircle, Clock } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import { formatDate } from "@/lib/utils";

const platformIcons: Record<string, any> = {
  email: Mail,
  linkedin: Linkedin,
  whatsapp: MessageCircle,
  blog: FileText,
  newsletter: Newspaper,
};

const statusIcons: Record<string, any> = {
  sent: CheckCircle,
  failed: XCircle,
  pending: Clock,
};

const statusColors: Record<string, string> = {
  sent: "text-green-500",
  failed: "text-red-500",
  pending: "text-yellow-500",
};

export default function BroadcastPage() {
  const [logs, setLogs] = useState<BroadcastResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const response = await api.getBroadcastLogs();
      setLogs(response.items);
    } catch (error) {
      console.error("Failed to fetch broadcast logs:", error);
      toast({
        title: "Error",
        description: "Failed to fetch broadcast history.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Share2 className="w-8 h-8 text-primary" />
        <div>
          <h1 className="text-3xl font-bold">Broadcast History</h1>
          <p className="text-muted-foreground">
            Your recent broadcasts and shares ({logs.length} total)
          </p>
        </div>
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
        </div>
      ) : logs.length === 0 ? (
        <div className="text-center py-20">
          <Share2 className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
          <h2 className="text-xl font-semibold mb-2">No broadcasts yet</h2>
          <p className="text-muted-foreground">
            Start sharing news by clicking the share button on any news card.
          </p>
        </div>
      ) : (
        <div className="bg-card border border-border rounded-lg overflow-hidden">
          <table className="w-full">
            <thead className="bg-muted/50">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium">Platform</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Status</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Recipient</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Date</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Content Preview</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {logs.map((log) => {
                const PlatformIcon = platformIcons[log.platform] || Share2;
                const StatusIcon = statusIcons[log.status] || Clock;
                const statusColor = statusColors[log.status] || "text-gray-500";

                return (
                  <tr key={log.id} className="hover:bg-muted/30">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <PlatformIcon className="w-4 h-4" />
                        <span className="capitalize">{log.platform}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <div className={`flex items-center gap-1 ${statusColor}`}>
                        <StatusIcon className="w-4 h-4" />
                        <span className="capitalize">{log.status}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm text-muted-foreground">
                      {log.recipient || "-"}
                    </td>
                    <td className="px-4 py-3 text-sm text-muted-foreground">
                      {formatDate(log.created_at)}
                    </td>
                    <td className="px-4 py-3 text-sm text-muted-foreground max-w-xs truncate">
                      {log.content?.slice(0, 50) || "-"}
                      {log.content && log.content.length > 50 && "..."}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
