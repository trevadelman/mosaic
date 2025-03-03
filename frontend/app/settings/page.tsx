"use client"

import { useState } from "react"
import { Settings as SettingsIcon, Moon, Sun, Monitor } from "lucide-react"
import { useTheme } from "next-themes"

export default function SettingsPage() {
  const { theme, setTheme } = useTheme()
  const [notifications, setNotifications] = useState(true)
  const [telemetry, setTelemetry] = useState(false)
  
  return (
    <div className="container mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Settings</h1>
        <p className="text-muted-foreground">
          Customize your MOSAIC experience
        </p>
      </div>

      <div className="space-y-10">
        {/* Appearance */}
        <div className="rounded-lg border bg-card p-6 shadow-sm">
          <h2 className="text-xl font-semibold">Appearance</h2>
          <p className="text-sm text-muted-foreground mb-4">
            Customize how MOSAIC looks
          </p>

          <div className="space-y-4">
            <div>
              <h3 className="font-medium mb-2">Theme</h3>
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => setTheme("light")}
                  className={`flex items-center gap-2 rounded-md border px-3 py-2 text-sm ${
                    theme === "light" ? "bg-primary text-primary-foreground" : "bg-background"
                  }`}
                >
                  <Sun className="h-4 w-4" />
                  Light
                </button>
                <button
                  onClick={() => setTheme("dark")}
                  className={`flex items-center gap-2 rounded-md border px-3 py-2 text-sm ${
                    theme === "dark" ? "bg-primary text-primary-foreground" : "bg-background"
                  }`}
                >
                  <Moon className="h-4 w-4" />
                  Dark
                </button>
                <button
                  onClick={() => setTheme("system")}
                  className={`flex items-center gap-2 rounded-md border px-3 py-2 text-sm ${
                    theme === "system" ? "bg-primary text-primary-foreground" : "bg-background"
                  }`}
                >
                  <Monitor className="h-4 w-4" />
                  System
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Notifications */}
        <div className="rounded-lg border bg-card p-6 shadow-sm">
          <h2 className="text-xl font-semibold">Notifications</h2>
          <p className="text-sm text-muted-foreground mb-4">
            Manage how you receive notifications
          </p>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium">Enable notifications</h3>
                <p className="text-sm text-muted-foreground">
                  Receive notifications about agent activities
                </p>
              </div>
              <label className="relative inline-flex cursor-pointer items-center">
                <input
                  type="checkbox"
                  checked={notifications}
                  onChange={() => setNotifications(!notifications)}
                  className="peer sr-only"
                />
                <div className="peer h-6 w-11 rounded-full bg-muted after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:bg-white after:transition-all after:content-[''] peer-checked:bg-primary peer-checked:after:translate-x-full peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-primary/50"></div>
              </label>
            </div>
          </div>
        </div>

        {/* Privacy */}
        <div className="rounded-lg border bg-card p-6 shadow-sm">
          <h2 className="text-xl font-semibold">Privacy</h2>
          <p className="text-sm text-muted-foreground mb-4">
            Manage your privacy settings
          </p>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium">Usage telemetry</h3>
                <p className="text-sm text-muted-foreground">
                  Help improve MOSAIC by sending anonymous usage data
                </p>
              </div>
              <label className="relative inline-flex cursor-pointer items-center">
                <input
                  type="checkbox"
                  checked={telemetry}
                  onChange={() => setTelemetry(!telemetry)}
                  className="peer sr-only"
                />
                <div className="peer h-6 w-11 rounded-full bg-muted after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:bg-white after:transition-all after:content-[''] peer-checked:bg-primary peer-checked:after:translate-x-full peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-primary/50"></div>
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
