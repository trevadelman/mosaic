"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { AlertCircle } from "lucide-react"

interface AddManufacturerModalProps {
  open: boolean
  onClose: () => void
  onAdd: () => Promise<void>
}

export function AddManufacturerModal({ open, onClose, onAdd }: AddManufacturerModalProps) {
  const [name, setName] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  const handleAdd = async () => {
    if (!name.trim()) {
      setError("Manufacturer name is required")
      return
    }

    setLoading(true)
    setError("")

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/apps/pdf-ingestion/manufacturers`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ name: name.trim() })
      })

      const data = await response.json()

      if (data.success) {
        await onAdd()
        handleClose()
      } else {
        setError(data.error || "Failed to create manufacturer")
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create manufacturer")
    } finally {
      setLoading(false)
    }
  }

  const handleClose = () => {
    setName("")
    setError("")
    setLoading(false)
    onClose()
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add Manufacturer</DialogTitle>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Input
              placeholder="Enter manufacturer name"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>

          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <div className="flex justify-end gap-4">
            <Button
              variant="outline"
              onClick={handleClose}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button
              onClick={handleAdd}
              disabled={loading}
            >
              {loading ? "Creating..." : "Create"}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
