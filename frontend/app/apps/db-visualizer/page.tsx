"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useGraphData } from "./hooks/useGraphData"
import { useTableDetails } from "./hooks/useTableDetails"
import { useTableData } from "./hooks/useTableData"
import { ForceGraph } from "./components/ForceGraph"
import { TableDetailsPanel } from "./components/TableDetails"
import { TableDataView } from "./components/TableDataView"
import { Skeleton } from "@/components/ui/skeleton"
import { Node } from "./hooks/useGraphData"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"

export default function DatabaseVisualizerPage() {
  const { data, loading, error } = useGraphData()
  const { details, loading: detailsLoading, error: detailsError, fetchTableDetails } = useTableDetails()
  const { data: tableData, loading: tableLoading, error: tableError, fetchTableData } = useTableData()
  
  const handleNodeClick = (node: Node) => {
    if (node.group === 'table') {
      fetchTableDetails(node.id)
      fetchTableData(node.id)
    }
  }
  
  return (
    <div className="container py-10">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Database Structure Visualization</CardTitle>
          </CardHeader>
          <CardContent>
            {loading && (
              <div className="w-full h-[600px] flex items-center justify-center">
                <Skeleton className="w-full h-full" />
              </div>
            )}
            
            {error && (
              <div className="w-full p-4 text-destructive bg-destructive/10 rounded-lg">
                <p>{error}</p>
              </div>
            )}
            
            {data && (
              <div className="w-full">
                <div className="mb-4 flex gap-4 items-center text-sm text-muted-foreground">
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
                
                <ForceGraph
                  nodes={data.nodes}
                  links={data.links}
                  width={600}
                  height={600}
                  onNodeClick={handleNodeClick}
                />
                
                <div className="mt-4 text-sm text-muted-foreground">
                  <p>
                    Drag nodes to reposition • Scroll to zoom • Drag background to pan • Click table to view details
                  </p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Table Information</CardTitle>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="details" className="w-full">
                <TabsList>
                  <TabsTrigger value="details">Structure</TabsTrigger>
                  <TabsTrigger value="data">Data</TabsTrigger>
                </TabsList>
                <TabsContent value="details" className="min-h-[500px]">
                  <TableDetailsPanel
                    details={details}
                    loading={detailsLoading}
                    error={detailsError}
                  />
                </TabsContent>
                <TabsContent value="data" className="min-h-[500px]">
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
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
