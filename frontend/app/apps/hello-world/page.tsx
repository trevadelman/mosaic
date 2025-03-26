"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

export default function HelloWorldApp() {
  const [name, setName] = useState("")
  const [greeting, setGreeting] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/apps/hello-world/greet`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ name })
      })
      
      if (!response.ok) {
        throw new Error(`Error: ${response.status} ${response.statusText}`)
      }
      
      const data = await response.json()
      setGreeting(data.greeting)
    } catch (error) {
      console.error("Error fetching greeting:", error)
      setError(error instanceof Error ? error.message : "An error occurred")
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <div className="container py-10">
      <Card>
        <CardHeader>
          <CardTitle>Hello World Application</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Input
                type="text"
                placeholder="Enter your name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                disabled={loading}
              />
            </div>
            <Button type="submit" disabled={loading}>
              {loading ? "Getting Greeting..." : "Get Greeting"}
            </Button>
          </form>
          
          {error && (
            <div className="mt-4 p-4 bg-destructive/10 rounded-md text-destructive">
              <p>{error}</p>
            </div>
          )}
          
          {greeting && !error && (
            <div className="mt-4 p-4 bg-primary/10 rounded-md">
              <p className="text-lg">{greeting}</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
