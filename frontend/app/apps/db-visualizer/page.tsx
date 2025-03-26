"use client"

import { Card, CardContent } from "@/components/ui/card"
import { useGraphData } from "./hooks/useGraphData"
import { useTableDetails } from "./hooks/useTableDetails"
import { useTableData } from "./hooks/useTableData"
import { ForceGraph } from "./components/ForceGraph"
import { TableDetailsPanel } from "./components/TableDetails"
import { TableDataView } from "./components/TableDataView"
import { Skeleton } from "@/components/ui/skeleton"
import { Node } from "./hooks/useGraphData"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import { Breadcrumb } from "@/components/ui/breadcrumb"
import { Database } from "lucide-react"
import { FloatingPanel } from "@/components/ui/floating-panel"
import { useState, useEffect } from "react"
import { useWindowSize } from "./hooks/useWindowSize"

export default function DatabaseVisualizerPage() {
  const { data, loading, error } = useGraphData()
  const { details, loading: detailsLoading, error: detailsError, fetchTableDetails } = useTableDetails()
  const { data: tableData, loading: tableLoading, error: tableError, fetchTableData } = useTableData()
  const [showDetails, setShowDetails] = useState(false)
  const { width, height } = useWindowSize()
  
  const handleNodeClick = (node: Node) => {
    if (node.group === 'table') {
      fetchTableDetails(node.id)
      fetchTableData(node.id)
      setShowDetails(true)
    }
  }
  
  return (
    <div className="container py-8 space-y-8">
      {/* Header */}
      <div className="space-y-2">
        <Breadcrumb
          items={[
            { label: "Apps", href: "/apps" },
            { label: "Database Visualizer" }
          ]}
        />
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-2">
              <Database className="h-8 w-8 text-primary" />
              Database Visualizer
            </h1>
            <p className="text-muted-foreground mt-1">
              Interactive visualization and exploration of your database structure
            </p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="relative -mx-8">
        <Card className="border-0 shadow-none rounded-none">
          <CardContent className="p-0 min-h-[calc(100vh-12rem)]">
            {loading && (
              <div className="w-full h-[calc(100vh-12rem)] flex items-center justify-center">
                <Skeleton className="w-full h-full" />
              </div>
            )}
            
            {error && (
              <div className="w-full p-4 text-destructive bg-destructive/10 rounded-lg">
                <p>{error}</p>
              </div>
            )}
            
            {data && (
              <div className="relative w-full h-[calc(100vh-12rem)]">
                <ForceGraph
                  nodes={data.nodes}
                  links={data.links}
                  width={width - 64}
                  height={height - 192}
                  onNodeClick={handleNodeClick}
                />
                
                <div className="absolute bottom-4 left-4 p-2 rounded-lg bg-background/80 backdrop-blur-sm border shadow-sm">
                  <div className="flex gap-4 items-center text-sm text-muted-foreground">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-[#0ea5e9]" />
                      <span>Tables</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-[#6366f1]" />
                      <span>Columns</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="h-[2px] w-8 bg-[#999]" />
                      <span>Contains</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="h-[2px] w-8 bg-[#0ea5e9] [stroke-dasharray:5,5]" />
                      <span>References</span>
                    </div>
                  </div>
                </div>

                <div className="absolute bottom-4 right-4 p-2 rounded-lg bg-background/80 backdrop-blur-sm border shadow-sm">
                  <p className="text-sm text-muted-foreground">
                    Drag nodes • Scroll to zoom • Drag background to pan • Click table to view details
                  </p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <FloatingPanel open={showDetails} onClose={() => setShowDetails(false)}>
          <Tabs defaultValue="details" className="w-full">
            <TabsList>
              <TabsTrigger value="details">Structure</TabsTrigger>
              <TabsTrigger value="data">Data</TabsTrigger>
            </TabsList>
            <TabsContent value="details">
              <TableDetailsPanel
                details={details}
                loading={detailsLoading}
                error={detailsError}
              />
            </TabsContent>
            <TabsContent value="data">
              <TableDataView
                data={tableData}
                loading={tableLoading}
                error={tableError}
                onPageChange={(page) => {
                  if (details) {
                    fetchTableData(details.name, page)
                  }
                }}
              />
            </TabsContent>
          </Tabs>
        </FloatingPanel>
      </div>
    </div>
  )
}
