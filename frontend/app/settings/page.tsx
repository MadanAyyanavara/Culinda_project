"use client";

import { useState } from "react";
import { useTheme } from "@/components/ui/theme-provider";
import { 
  Bell, 
  Mail, 
  Shield, 
  User, 
  Globe, 
  Database,
  Check,
  Moon,
  Sun,
  Monitor
} from "lucide-react";
import { useToast } from "@/components/ui/use-toast";

export default function SettingsPage() {
  const { theme, setTheme } = useTheme();
  const { toast } = useToast();
  
  const [settings, setSettings] = useState({
    emailNotifications: true,
    pushNotifications: false,
    digestFrequency: "daily",
    autoRefresh: true,
    compactView: false,
  });

  const handleSave = () => {
    toast({
      title: "Settings saved",
      description: "Your preferences have been updated successfully.",
      variant: "success",
    });
  };

  const SettingSection = ({ title, description, children }: { title: string; description?: string; children: React.ReactNode }) => (
    <div className="rounded-2xl bg-card border border-border/50 p-6">
      <h3 className="font-semibold text-lg mb-1">{title}</h3>
      {description && <p className="text-sm text-muted-foreground mb-4">{description}</p>}
      {children}
    </div>
  );

  return (
    <div className="space-y-8 max-w-4xl">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2">Settings</h1>
        <p className="text-muted-foreground">
          Manage your account preferences and application settings
        </p>
      </div>

      {/* Appearance */}
      <SettingSection 
        title="Appearance" 
        description="Customize how the dashboard looks"
      >
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium mb-3 block">Theme</label>
            <div className="grid grid-cols-3 gap-3">
              {[
                { value: "light", label: "Light", icon: Sun },
                { value: "dark", label: "Dark", icon: Moon },
                { value: "system", label: "System", icon: Monitor },
              ].map((option) => {
                const Icon = option.icon;
                const isActive = theme === option.value;
                return (
                  <button
                    key={option.value}
                    onClick={() => setTheme(option.value as any)}
                    className={`flex flex-col items-center gap-2 p-4 rounded-xl border-2 transition-all ${
                      isActive 
                        ? "border-primary bg-primary/5" 
                        : "border-border hover:border-primary/50"
                    }`}
                  >
                    <Icon className={`w-5 h-5 ${isActive ? "text-primary" : "text-muted-foreground"}`} />
                    <span className={`text-sm font-medium ${isActive ? "text-primary" : ""}`}>
                      {option.label}
                    </span>
                    {isActive && <Check className="w-4 h-4 text-primary" />}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="flex items-center justify-between py-3 border-t border-border/50">
            <div className="flex items-center gap-3">
              <Database className="w-5 h-5 text-muted-foreground" />
              <div>
                <p className="font-medium text-sm">Compact View</p>
                <p className="text-xs text-muted-foreground">Show more content with less spacing</p>
              </div>
            </div>
            <button
              onClick={() => setSettings(s => ({ ...s, compactView: !s.compactView }))}
              className={`w-11 h-6 rounded-full transition-colors relative ${
                settings.compactView ? "bg-primary" : "bg-muted"
              }`}
            >
              <span className={`absolute top-1 left-1 w-4 h-4 rounded-full bg-white transition-transform ${
                settings.compactView ? "translate-x-5" : ""
              }`} />
            </button>
          </div>
        </div>
      </SettingSection>

      {/* Notifications */}
      <SettingSection 
        title="Notifications" 
        description="Configure how you want to be notified"
      >
        <div className="space-y-4">
          <div className="flex items-center justify-between py-3">
            <div className="flex items-center gap-3">
              <Mail className="w-5 h-5 text-muted-foreground" />
              <div>
                <p className="font-medium text-sm">Email Notifications</p>
                <p className="text-xs text-muted-foreground">Receive updates about new articles</p>
              </div>
            </div>
            <button
              onClick={() => setSettings(s => ({ ...s, emailNotifications: !s.emailNotifications }))}
              className={`w-11 h-6 rounded-full transition-colors relative ${
                settings.emailNotifications ? "bg-primary" : "bg-muted"
              }`}
            >
              <span className={`absolute top-1 left-1 w-4 h-4 rounded-full bg-white transition-transform ${
                settings.emailNotifications ? "translate-x-5" : ""
              }`} />
            </button>
          </div>

          <div className="flex items-center justify-between py-3 border-t border-border/50">
            <div className="flex items-center gap-3">
              <Bell className="w-5 h-5 text-muted-foreground" />
              <div>
                <p className="font-medium text-sm">Push Notifications</p>
                <p className="text-xs text-muted-foreground">Browser notifications for important updates</p>
              </div>
            </div>
            <button
              onClick={() => setSettings(s => ({ ...s, pushNotifications: !s.pushNotifications }))}
              className={`w-11 h-6 rounded-full transition-colors relative ${
                settings.pushNotifications ? "bg-primary" : "bg-muted"
              }`}
            >
              <span className={`absolute top-1 left-1 w-4 h-4 rounded-full bg-white transition-transform ${
                settings.pushNotifications ? "translate-x-5" : ""
              }`} />
            </button>
          </div>

          {settings.emailNotifications && (
            <div className="pt-3 border-t border-border/50">
              <label className="text-sm font-medium mb-2 block">Digest Frequency</label>
              <select 
                value={settings.digestFrequency}
                onChange={(e) => setSettings(s => ({ ...s, digestFrequency: e.target.value }))}
                className="w-full px-4 py-2 rounded-xl bg-background border border-input focus:outline-none focus:ring-2 focus:ring-ring"
              >
                <option value="realtime">Real-time</option>
                <option value="hourly">Hourly</option>
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
              </select>
            </div>
          )}
        </div>
      </SettingSection>

      {/* Data & Privacy */}
      <SettingSection 
        title="Data & Privacy" 
        description="Manage your data and privacy settings"
      >
        <div className="space-y-4">
          <div className="flex items-center justify-between py-3">
            <div className="flex items-center gap-3">
              <Globe className="w-5 h-5 text-muted-foreground" />
              <div>
                <p className="font-medium text-sm">Auto Refresh</p>
                <p className="text-xs text-muted-foreground">Automatically refresh news feed</p>
              </div>
            </div>
            <button
              onClick={() => setSettings(s => ({ ...s, autoRefresh: !s.autoRefresh }))}
              className={`w-11 h-6 rounded-full transition-colors relative ${
                settings.autoRefresh ? "bg-primary" : "bg-muted"
              }`}
            >
              <span className={`absolute top-1 left-1 w-4 h-4 rounded-full bg-white transition-transform ${
                settings.autoRefresh ? "translate-x-5" : ""
              }`} />
            </button>
          </div>

          <div className="flex items-center justify-between py-3 border-t border-border/50">
            <div className="flex items-center gap-3">
              <Shield className="w-5 h-5 text-muted-foreground" />
              <div>
                <p className="font-medium text-sm">Data Export</p>
                <p className="text-xs text-muted-foreground">Download all your data</p>
              </div>
            </div>
            <button className="px-4 py-2 text-sm font-medium bg-secondary rounded-lg hover:bg-secondary/80 transition-colors">
              Export
            </button>
          </div>
        </div>
      </SettingSection>

      {/* Account */}
      <SettingSection 
        title="Account" 
        description="Manage your account information"
      >
        <div className="space-y-4">
          <div className="flex items-center gap-4 p-4 bg-muted/50 rounded-xl">
            <div className="w-12 h-12 rounded-full bg-primary flex items-center justify-center">
              <User className="w-6 h-6 text-primary-foreground" />
            </div>
            <div>
              <p className="font-medium">Demo User</p>
              <p className="text-sm text-muted-foreground">demo@ainews.com</p>
            </div>
          </div>

          <div className="flex gap-3 pt-2">
            <button className="flex-1 px-4 py-2.5 text-sm font-medium bg-secondary rounded-xl hover:bg-secondary/80 transition-colors">
              Change Password
            </button>
            <button className="flex-1 px-4 py-2.5 text-sm font-medium bg-destructive/10 text-destructive rounded-xl hover:bg-destructive/20 transition-colors">
              Delete Account
            </button>
          </div>
        </div>
      </SettingSection>

      {/* Save Button */}
      <div className="flex justify-end">
        <button
          onClick={handleSave}
          className="px-8 py-3 bg-primary text-primary-foreground font-medium rounded-xl hover:bg-primary/90 transition-colors shadow-lg shadow-primary/25"
        >
          Save Changes
        </button>
      </div>
    </div>
  );
}
