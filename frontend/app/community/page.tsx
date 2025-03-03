"use client"

import { Users } from "lucide-react"

export default function CommunityPage() {
  return (
    <div className="container mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Community</h1>
        <p className="text-muted-foreground">
          Connect with other MOSAIC users and share your experiences
        </p>
      </div>

      <div className="flex flex-col items-center justify-center rounded-lg border bg-card p-12 text-center shadow-sm">
        <Users className="h-12 w-12 text-muted-foreground" />
        <h2 className="mt-4 text-xl font-semibold">Coming Soon</h2>
        <p className="mt-2 text-muted-foreground max-w-md">
          The community features are currently under development. Check back soon for updates!
        </p>
      </div>
    </div>
  )
}
