"use client"

import { useState } from "react"
import { Settings as SettingsIcon, Moon, Sun, Monitor, User, Trash2 } from "lucide-react"
import { useTheme } from "next-themes"
import { UserProfile, useUser } from "@clerk/nextjs"
import { userDataApi } from "@/lib/api"

export default function SettingsPage() {
  const { theme, setTheme } = useTheme()
  const [notifications, setNotifications] = useState(true)
  const [telemetry, setTelemetry] = useState(false)
  const [isClearing, setIsClearing] = useState(false)
  const [clearSuccess, setClearSuccess] = useState<string | null>(null)
  const [clearError, setClearError] = useState<string | null>(null)
  const { user } = useUser()
  
  const handleClearConversations = async () => {
    if (!user?.id || isClearing) return
    
    setIsClearing(true)
    setClearSuccess(null)
    setClearError(null)
    
    try {
      const response = await userDataApi.clearUserConversations(user.id)
      
      if (response.error) {
        setClearError(response.error)
      } else {
        setClearSuccess(response.data?.message || "Conversations cleared successfully")
      }
    } catch (error) {
      setClearError("An unexpected error occurred")
      console.error("Error clearing conversations:", error)
    } finally {
      setIsClearing(false)
    }
  }
  
  return (
    <div className="container mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Settings</h1>
        <p className="text-muted-foreground">
          Customize your MOSAIC experience
        </p>
      </div>

      <div className="space-y-10">
        {/* Account */}
        <div className="rounded-lg border bg-card p-6 shadow-sm">
          <h2 className="text-xl font-semibold">Account</h2>
          <p className="text-sm text-muted-foreground mb-4">
            Manage your account settings
          </p>
          
          <div className="flex justify-center">
            <UserProfile
              routing="hash"
              appearance={{
                elements: {
                  card: "bg-white dark:bg-gray-800 shadow-md",
                  headerTitle: "text-gray-900 dark:text-gray-100",
                  headerSubtitle: "text-gray-600 dark:text-gray-400",
                  formFieldLabel: "text-gray-700 dark:text-gray-300",
                  formFieldInput: "border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100",
                  formButtonPrimary: "bg-blue-600 hover:bg-blue-700 text-sm normal-case",
                  formButtonReset: "text-gray-600 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300",
                },
              }}
            />
          </div>
        </div>

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
        
        {/* Data Management */}
        <div className="rounded-lg border bg-card p-6 shadow-sm">
          <h2 className="text-xl font-semibold">Data Management</h2>
          <p className="text-sm text-muted-foreground mb-4">
            Manage your data and conversations
          </p>

          <div className="space-y-6">
            <div>
              <h3 className="font-medium mb-2">Clear Conversations</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Delete all your conversations with agents. This action cannot be undone.
              </p>
              
              <button
                onClick={handleClearConversations}
                disabled={isClearing || !user}
                className="flex items-center gap-2 rounded-md bg-red-600 px-4 py-2 text-sm text-white hover:bg-red-700 disabled:opacity-50"
              >
                {isClearing ? (
                  <>
                    <span className="animate-spin">⟳</span>
                    Clearing...
                  </>
                ) : (
                  <>
                    <Trash2 className="h-4 w-4" />
                    Clear All Conversations
                  </>
                )}
              </button>
              
              {clearSuccess && (
                <p className="mt-2 text-sm text-green-600 dark:text-green-400">
                  {clearSuccess}
                </p>
              )}
              
              {clearError && (
                <p className="mt-2 text-sm text-red-600 dark:text-red-400">
                  Error: {clearError}
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
