"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Breadcrumb } from "@/components/ui/breadcrumb"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { TreeView } from "@/components/ui/tree-view"
import { JsonViewer } from "@/components/ui/json-viewer"
import { PdfViewer } from "@/components/ui/pdf-viewer"
import { FileUp, Plus, Upload } from "lucide-react"
import { UploadModal } from "./components/upload-modal"
import { AddManufacturerModal } from "./components/add-manufacturer-modal"

interface TreeItem {
  id: string
  name: string
  children?: TreeItem[]
  type: 'folder' | 'file' | 'directory' | 'divider'
  manufacturer?: string
  path?: string
}

interface DeviceInfo {
  name: string
  manufacturer: string
  type: 'file' | 'directory'
  path: string
}

interface DeviceFile {
  name: string
  type: 'file' | 'directory'
  path: string
}

export default function PdfIngestionPage() {
  const [treeItems, setTreeItems] = useState<TreeItem[]>([])
  const [error, setError] = useState<string>("")
  const [addingManufacturer, setAddingManufacturer] = useState(false)
  const [uploadModalOpen, setUploadModalOpen] = useState(false)
  const [selectedDevice, setSelectedDevice] = useState<{ manufacturer: string; name: string } | null>(null)
  const [deviceJson, setDeviceJson] = useState<string>("")
  const [selectedPdfUrl, setSelectedPdfUrl] = useState<string>("")

  // Load manufacturers and devices
  const loadTreeData = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/apps/pdf-ingestion/manufacturers`)
      const manufacturers = await response.json()

      const items: TreeItem[] = []
      
      // Filter out 'xeto' from manufacturers list
      const regularManufacturers = manufacturers.filter((m: string) => m !== 'xeto')
      
      // Add regular manufacturers
      for (const manufacturer of regularManufacturers) {
        const devicesResponse = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/apps/pdf-ingestion/manufacturers/${manufacturer}/devices`
        )
        const { devices } = await devicesResponse.json()

        const children: TreeItem[] = []
        
        for (const device of devices) {
          // Add device directory
          const deviceNode: TreeItem = {
            id: `${device.manufacturer}-${device.name}`,
            name: device.name,
            type: 'directory',
            manufacturer: device.manufacturer,
            path: device.path,
            children: []
          }

          // Add device files
          if (device.type === 'directory') {
            // Add productInfo.json if it exists
            const jsonFile = devices.find((f: DeviceInfo) => 
              f.type === 'file' && 
              f.path === `${device.name}/productInfo.json`
            )
            if (jsonFile) {
              deviceNode.children?.push({
                id: `${device.manufacturer}-${device.name}-json`,
                name: 'productInfo.json',
                type: 'file',
                manufacturer: device.manufacturer,
                path: jsonFile.path
              })
            }

            // Add raw_docs directory if it exists
            const rawDocsDir = devices.find((f: DeviceInfo) =>
              f.type === 'directory' &&
              f.path === `${device.name}/raw_docs`
            )
            if (rawDocsDir) {
              // Add PDF files
              const pdfFiles = devices.filter((f: DeviceInfo) =>
                f.type === 'file' &&
                f.path.startsWith(`${device.name}/raw_docs/`) &&
                f.path.endsWith('.pdf')
              )

              if (pdfFiles.length > 0) {
                const rawDocsNode: TreeItem = {
                  id: `${device.manufacturer}-${device.name}-raw_docs`,
                  name: 'raw_docs',
                  type: 'directory',
                  manufacturer: device.manufacturer,
                  path: rawDocsDir.path,
                  children: pdfFiles.map((pdf: DeviceInfo) => ({
                    id: `${device.manufacturer}-${pdf.path}`,
                    name: pdf.name,
                    type: 'file',
                    manufacturer: device.manufacturer,
                    path: pdf.path
                  }))
                }
                deviceNode.children?.push(rawDocsNode)
              }
            }
          }

          if (deviceNode.children?.length) {
            children.push(deviceNode)
          }
        }

        items.push({
          id: manufacturer,
          name: manufacturer,
          type: 'folder',
          children
        })
      }

        // Add xeto directory as a special section with a divider
      if (manufacturers.includes('xeto')) {
        items.push({
          id: 'xeto-divider',
          name: '──────────',
          type: 'divider',
          children: []
        })
        
        // Load xeto directory contents
        const xetoResponse = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/apps/pdf-ingestion/manufacturers/xeto/devices`
        )
        const { devices: xetoDevices } = await xetoResponse.json()
        
        // Create xeto libraries node
        const xetoNode: TreeItem = {
          id: 'xeto',
          name: 'Xeto Libraries',
          type: 'folder',
          children: []
        }

        // Build tree structure from flat list of files/directories
        const buildTree = (devices: DeviceInfo[]) => {
          const tree: { [key: string]: TreeItem } = {}
          
          devices.forEach(device => {
            const parts = device.path.split('/')
            let currentPath = ''
            let currentNode = xetoNode.children
            
            parts.forEach((part, i) => {
              currentPath = currentPath ? `${currentPath}/${part}` : part
              
              if (!tree[currentPath]) {
                const newNode: TreeItem = {
                  id: `xeto-${currentPath}`,
                  name: part,
                  type: device.type,
                  manufacturer: 'xeto',
                  path: currentPath,
                  children: []
                }
                
                tree[currentPath] = newNode
                if (currentNode) {
                  currentNode.push(newNode)
                }
              }
              
              currentNode = tree[currentPath].children
            })
          })
        }
        
        if (xetoDevices) {
          buildTree(xetoDevices)
        }
        
        items.push(xetoNode)
      }
      
      setTreeItems(items)
    } catch (err) {
      console.error("Error loading tree data:", err)
    }
  }

  useEffect(() => {
    loadTreeData()
  }, [])

  const loadDeviceInfo = async (manufacturer: string, path: string) => {
    try {
      setDeviceJson("")
      setSelectedPdfUrl("")

      if (path.endsWith('.pdf')) {
        setSelectedPdfUrl(`${process.env.NEXT_PUBLIC_API_URL}/apps/pdf-ingestion/manufacturers/${manufacturer}/${path}`)
        return
      }

      if (path.endsWith('.xeto') || path.endsWith('.xetolib')) {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/apps/pdf-ingestion/manufacturers/${manufacturer}/${path}`
        )
        if (!response.ok) {
          throw new Error("Failed to load xeto file")
        }
        const content = await response.text()
        setDeviceJson(content)
        return
      }

      if (!path.endsWith('productInfo.json')) {
        return
      }

      // Extract device name from path (it's the parent directory of productInfo.json)
      const device = path.split('/')[0]

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/apps/pdf-ingestion/manufacturers/${manufacturer}/devices/${device}/info`
      )
      
      if (!response.ok) {
        throw new Error("Failed to load device information")
      }

      const data = await response.json()
      setDeviceJson(JSON.stringify(data, null, 2))
      setError("")
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load device information")
      setDeviceJson("")
    }
  }

  const handleSaveJson = async (manufacturer: string, jsonData: string) => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/apps/pdf-ingestion/save`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          manufacturer,
          data: jsonData
        })
      })

      if (!response.ok) {
        throw new Error("Failed to save file")
      }

      // Reload the tree to show the new file
      loadTreeData()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save file")
      throw err
    }
  }

  return (
    <div className="container py-6 flex flex-col h-screen">
      {/* Header */}
      <div className="space-y-2 mb-6">
        <Breadcrumb
          items={[
            { label: "Apps", href: "/apps" },
            { label: "PDF Ingestion" }
          ]}
        />
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-2">
              <FileUp className="h-8 w-8 text-primary" />
              HVAC PDF Ingestion
            </h1>
            <p className="text-muted-foreground mt-1">
              Extract device properties, BACnet objects, and Modbus registers from HVAC documentation
            </p>
          </div>
          <Button onClick={() => setUploadModalOpen(true)}>
            <Upload className="h-4 w-4 mr-2" />
            Upload Document
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-6 flex-1 min-h-0">
        {/* Tree View */}
        <div className="col-span-3">
          <Card className="h-full">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Manufacturers</CardTitle>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setAddingManufacturer(true)}
              >
                <Plus className="h-4 w-4" />
              </Button>
            </CardHeader>
            <CardContent>
              <TreeView
                items={treeItems}
                onSelect={(item) => {
                  if (item.type === 'divider') return
                  
                  if (item.type === 'file') {
                    if (item.manufacturer && item.path) {
                      setSelectedDevice({ manufacturer: item.manufacturer, name: item.name })
                      loadDeviceInfo(item.manufacturer, item.path)
                    }
                  }
                  
                  // Handle directory clicks for xeto directories
                  if (item.type === 'directory' && item.manufacturer === 'xeto') {
                    if (item.path) {
                      setSelectedDevice({ manufacturer: item.manufacturer, name: item.name })
                      loadDeviceInfo(item.manufacturer, item.path)
                    }
                  }
                }}
              />
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <div className="col-span-9 flex flex-col space-y-4">
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          <Card className="flex-1">
            <CardContent className="p-0 h-full">
              {deviceJson && (
                <div className="h-[calc(100vh-180px)]">
                  <JsonViewer content={deviceJson} />
                </div>
              )}
              {selectedPdfUrl && (
                <div className="h-[calc(100vh-180px)]">
                  <PdfViewer url={selectedPdfUrl} height="100%" />
                </div>
              )}
              {!deviceJson && !selectedPdfUrl && (
                <div className="h-[calc(100vh-180px)] flex items-center justify-center text-muted-foreground">
                  Select a file from the tree to view its contents
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Modals */}
      <UploadModal
        open={uploadModalOpen}
        onClose={() => setUploadModalOpen(false)}
        manufacturers={treeItems.map(item => ({ id: item.id, name: item.name }))}
        onSave={handleSaveJson}
      />
      <AddManufacturerModal
        open={addingManufacturer}
        onClose={() => setAddingManufacturer(false)}
        onAdd={loadTreeData}
      />
    </div>
  )
}
