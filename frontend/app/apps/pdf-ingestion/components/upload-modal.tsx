"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Progress } from "@/components/ui/progress"
import { JsonViewer } from "@/components/ui/json-viewer"
import { Upload, FileJson, X, Clock, AlertCircle } from "lucide-react"

interface UploadModalProps {
  open: boolean
  onClose: () => void
  manufacturers: { id: string; name: string }[]
  onSave: (manufacturer: string, jsonData: string) => Promise<void>
}

export function UploadModal({ open, onClose, manufacturers, onSave }: UploadModalProps) {
  const [files, setFiles] = useState<File[]>([])
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [result, setResult] = useState<string>("")
  const [error, setError] = useState<string>("")
  const [selectedManufacturer, setSelectedManufacturer] = useState<string>("")
  const [step, setStep] = useState<"upload" | "edit">("upload")

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files || [])
    const validFiles = selectedFiles.filter(file => file.type === "application/pdf")
    
    if (validFiles.length === 0) {
      setError("Please select valid PDF files")
      return
    }
    
    if (validFiles.length !== selectedFiles.length) {
      setError("Some files were skipped. Only PDF files are supported.")
    } else {
      setError("")
    }
    
    setFiles(prev => [...prev, ...validFiles])
  }

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
    setError("")
  }

  const handleUpload = async () => {
    if (files.length === 0 || !selectedManufacturer) return

    setLoading(true)
    setError("")
    setResult("")
    setProgress(0)

    const formData = new FormData()
    files.forEach((file, index) => {
      formData.append("files", file)
    })
    formData.append("manufacturer", selectedManufacturer)

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
          setStep("edit")
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

  const handleSave = async () => {
    try {
      await onSave(selectedManufacturer, result)
      handleClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save")
    }
  }

  const handleClose = () => {
    setFiles([])
    setLoading(false)
    setProgress(0)
    setResult("")
    setError("")
    setSelectedManufacturer("")
    setStep("upload")
    onClose()
  }

  const renderFileList = () => {
    if (files.length === 0) return null

    return (
      <div className="space-y-2">
        {files.map((file, index) => (
          <div key={index} className="flex items-center gap-4 p-2 bg-background/50 rounded-lg">
            <FileJson className="h-6 w-6 text-primary" />
            <div className="flex-1">
              <p className="font-medium">{file.name}</p>
              <p className="text-sm text-muted-foreground">
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={(e) => {
                e.stopPropagation()
                removeFile(index)
              }}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        ))}
      </div>
    )
  }

  const renderLoadingState = () => {
    if (files.length === 0) return null

    return (
      <div className="w-full space-y-4">
        <div className="flex items-center gap-4">
          <Clock className="h-8 w-8 text-primary animate-pulse" />
          <div className="flex-1">
            <p className="font-medium">Processing {files.length} file(s)</p>
            <Progress value={progress} className="mt-2" />
          </div>
        </div>
        <p className="text-sm text-center text-muted-foreground">
          This may take up to 2 minutes. Please don't close this page.
        </p>
      </div>
    )
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-4xl">
        <DialogHeader>
          <DialogTitle>Upload HVAC Documentation</DialogTitle>
        </DialogHeader>

        {step === "upload" ? (
          <div className="space-y-6">
            {/* Manufacturer Selection */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Select Manufacturer</label>
              <div className="flex gap-4">
                <select
                  className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                  value={selectedManufacturer}
                  onChange={(e) => setSelectedManufacturer(e.target.value)}
                >
                  <option value="">Select a manufacturer</option>
                  {manufacturers.map((item) => (
                    <option key={item.id} value={item.name}>
                      {item.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* File Drop Zone */}
            <Card>
              <CardContent className="pt-6">
                <div 
                  className={`
                    border-2 border-dashed rounded-lg p-8
                    flex flex-col items-center justify-center gap-4
                    transition-colors
                    ${files.length > 0 ? 'border-primary bg-primary/5' : 'border-muted-foreground/25'}
                    ${!loading && 'hover:border-primary hover:bg-primary/5 cursor-pointer'}
                  `}
                  onClick={() => !loading && document.getElementById('file-input')?.click()}
                >
                  {files.length === 0 && (
                    <>
                      <Upload className="h-12 w-12 text-muted-foreground" />
                      <div className="text-center">
                        <p className="text-lg font-medium">Drop your PDF here or click to browse</p>
                        <p className="text-sm text-muted-foreground mt-1">Only PDF files are supported</p>
                      </div>
                    </>
                  )}
                  {files.length > 0 && !loading && renderFileList()}
                  {loading && renderLoadingState()}
                  <input
                    id="file-input"
                    type="file"
                    accept=".pdf"
                    multiple
                    onChange={handleFileChange}
                    className="hidden"
                  />
                </div>
              </CardContent>
            </Card>

            {/* Action Buttons */}
            <div className="flex justify-end gap-4">
              <Button
                variant="outline"
                onClick={handleClose}
              >
                Cancel
              </Button>
              <Button
                onClick={handleUpload}
                disabled={files.length === 0 || !selectedManufacturer || loading}
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
        ) : (
          <div className="space-y-6">
            <div className="h-[60vh]">
              <JsonViewer content={result} height="100%" />
            </div>

            <div className="flex justify-end gap-4">
              <Button
                variant="outline"
                onClick={() => setStep("upload")}
              >
                Back
              </Button>
              <Button onClick={handleSave}>
                Save to Storage
              </Button>
            </div>

            {error && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
