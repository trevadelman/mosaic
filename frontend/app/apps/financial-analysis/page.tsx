"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import { Breadcrumb } from "@/components/ui/breadcrumb"
import { AlertCircle, LineChart, Wallet } from "lucide-react"
import { useChat } from "@/lib/hooks/use-chat"
import { useAgents } from "@/lib/hooks/use-agents"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"

export default function FinancialAnalysisPage() {
  const [symbol, setSymbol] = useState("")
  const { agents, loading: agentsLoading } = useAgents()
  const financialAgent = agents.find(a => a.id === "financial_analysis")
  const { messages, sendMessage, isProcessing, clearChat } = useChat(financialAgent?.id)

  const handleAnalyze = async () => {
    if (!symbol || !financialAgent) return
    
    // Clear previous messages
    sendMessage(`Get the current stock price, company information, and technical indicators for ${symbol}`)
  }

  return (
    <div className="container py-8 space-y-8">
      {/* Header */}
      <div className="space-y-2">
        <Breadcrumb
          items={[
            { label: "Apps", href: "/apps" },
            { label: "Financial Analysis" }
          ]}
        />
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-2">
              <Wallet className="h-8 w-8 text-primary" />
              Financial Analysis
            </h1>
            <p className="text-muted-foreground mt-1">
              Analyze stocks with technical and fundamental indicators
            </p>
          </div>
        </div>
      </div>

      {/* Agent Loading State */}
      {agentsLoading && (
        <Alert>
          <Skeleton className="h-4 w-[250px]" />
        </Alert>
      )}

      {/* Agent Not Found Error */}
      {!agentsLoading && !financialAgent && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Financial Analysis agent not found. Please ensure the agent is properly configured.
          </AlertDescription>
        </Alert>
      )}

      {/* Search */}
      <Card>
        <CardHeader>
          <CardTitle>Stock Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex gap-4">
              <form 
                onSubmit={(e) => {
                  e.preventDefault()
                  handleAnalyze()
                }}
                className="flex gap-4"
              >
                <Input
                  placeholder="Enter stock symbol (e.g., AAPL)"
                  value={symbol}
                  onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                  className="max-w-xs"
                />
                <Button type="submit" disabled={!symbol || isProcessing || !financialAgent}>
                  {isProcessing ? "Analyzing..." : "Analyze"}
                </Button>
              </form>
            </div>
            {messages.length > 0 && (
              <div className="flex justify-end">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    clearChat()
                    setSymbol("")
                  }}
                >
                  Clear Results
                </Button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Results */}
      {/* Loading State */}
      {isProcessing && (
        <Card>
          <CardHeader>
            <CardTitle>Analyzing...</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Skeleton className="h-4 w-[300px]" />
            <Skeleton className="h-4 w-[250px]" />
            <Skeleton className="h-4 w-[200px]" />
          </CardContent>
        </Card>
      )}

      {/* Results */}
      {!isProcessing && messages.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Analysis Results</CardTitle>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[500px] pr-4">
              <div className="whitespace-pre-wrap font-mono text-sm">
                {messages[messages.length - 1].content.split('\n').map((line, i) => {
                  // Add spacing around section headers
                  if (line.endsWith(':')) {
                    return (
                      <div key={i} className="mt-4 mb-2 font-semibold">
                        {line}
                      </div>
                    )
                  }
                  return <div key={i}>{line}</div>
                })}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
