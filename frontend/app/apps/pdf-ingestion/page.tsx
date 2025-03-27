"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Breadcrumb } from "@/components/ui/breadcrumb"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { JsonViewer } from "@/components/ui/json-viewer"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Progress } from "@/components/ui/progress"
import { FileUp, AlertCircle, Upload, FileJson, X, Clock } from "lucide-react"

export default function PdfIngestionPage() {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [result, setResult] = useState<string>("")
  const [error, setError] = useState<string>("")

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile && selectedFile.type === "application/pdf") {
      setFile(selectedFile)
      setError("")
    } else {
      setFile(null)
      setError("Please select a valid PDF file")
    }
  }

  const handleUpload = async () => {
    if (!file) return

    setLoading(true)
    setError("")
    setResult("")
    setProgress(0)

    const formData = new FormData()
    formData.append("file", file)

    try {
      // Start progress simulation
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 95) {
            clearInterval(progressInterval)
            return prev
          }
          return prev + 1
        })
      }, 1000)

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/apps/pdf-ingestion/process`, {
        method: "POST",
        body: formData,
      })

      clearInterval(progressInterval)
      setProgress(100)

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`)
      }

      const data = await response.json()
      
      if (data.success) {
        // Try to format the JSON response
        try {
          const parsedJson = JSON.parse(data.response)
          setResult(JSON.stringify(parsedJson, null, 2))
        } catch {
          // If parsing fails, show the raw response
          setResult(data.response)
        }
      } else {
        throw new Error(data.error || "Failed to process PDF")
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred")
    } finally {
      setLoading(false)
    }
  }

  const renderFileInfo = () => {
    if (!file) return null

    return (
      <div className="flex items-center gap-4">
        <FileJson className="h-8 w-8 text-primary" />
        <div>
          <p className="font-medium">{file.name}</p>
          <p className="text-sm text-muted-foreground">
            {(file.size / 1024 / 1024).toFixed(2)} MB
          </p>
        </div>
        <Button
          variant="ghost"
          size="icon"
          className="ml-4"
          onClick={(e) => {
            e.stopPropagation()
            setFile(null)
            setResult("")
          }}
        >
          <X className="h-4 w-4" />
        </Button>
      </div>
    )
  }

  const renderLoadingState = () => {
    if (!file) return null

    return (
      <div className="w-full space-y-4">
        <div className="flex items-center gap-4">
          <Clock className="h-8 w-8 text-primary animate-pulse" />
          <div className="flex-1">
            <p className="font-medium">Processing {file.name}</p>
            <Progress value={progress} className="mt-2" />
          </div>
        </div>
        <p className="text-sm text-center text-muted-foreground">
          This may take a few minutes depending on the side of the file. Please don't close this page.
        </p>
      </div>
    )
  }

  return (
    <div className="container py-8 space-y-8">
      {/* Header */}
      <div className="space-y-2">
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
        </div>
      </div>

      {/* Upload Section */}
      <Card>
        <CardHeader>
          <CardTitle>Upload PDF</CardTitle>
          <CardDescription>
            Upload your HVAC documentation PDF to extract structured information.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {/* File Drop Zone */}
            <div 
              className={`
                border-2 border-dashed rounded-lg p-8
                flex flex-col items-center justify-center gap-4
                transition-colors
                ${file ? 'border-primary bg-primary/5' : 'border-muted-foreground/25'}
                ${!loading && 'hover:border-primary hover:bg-primary/5 cursor-pointer'}
              `}
              onClick={() => !loading && document.getElementById('file-input')?.click()}
            >
              {!file && (
                <>
                  <Upload className="h-12 w-12 text-muted-foreground" />
                  <div className="text-center">
                    <p className="text-lg font-medium">Drop your PDF here or click to browse</p>
                    <p className="text-sm text-muted-foreground mt-1">Only PDF files are supported</p>
                  </div>
                </>
              )}
              {file && !loading && renderFileInfo()}
              {loading && renderLoadingState()}
              <input
                id="file-input"
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                className="hidden"
              />
            </div>

            {/* Action Buttons */}
            <div className="flex justify-end gap-4">
              <Button
                variant="outline"
                onClick={() => {
                  setFile(null)
                  setResult("")
                }}
                disabled={!file || loading}
              >
                Clear
              </Button>
              <Button
                onClick={handleUpload}
                disabled={!file || loading}
              >
                {loading ? "Processing..." : "Process PDF"}
              </Button>
            </div>

            {error && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Results Dialog */}
      {result && (
        <Dialog>
          <DialogTrigger asChild>
            <Card className="hover:bg-accent/50 cursor-pointer transition-colors">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileJson className="h-6 w-6 text-primary" />
                  View Extracted Information
                </CardTitle>
                <CardDescription>
                  Click to view the structured data extracted from your PDF
                </CardDescription>
              </CardHeader>
            </Card>
          </DialogTrigger>
          <DialogContent className="max-w-4xl h-[80vh]">
            <DialogHeader>
              <DialogTitle>Extracted Information</DialogTitle>
            </DialogHeader>
            <div className="flex-1 min-h-0">
              <JsonViewer content={result} height="calc(80vh - 4rem)" />
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  )
}
