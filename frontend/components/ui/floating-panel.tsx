import { X } from "lucide-react"
import { cn } from "@/lib/utils"

interface FloatingPanelProps {
  children: React.ReactNode
  open: boolean
  onClose: () => void
  className?: string
}

export function FloatingPanel({ children, open, onClose, className }: FloatingPanelProps) {
  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 bg-black/20" onClick={onClose}>
      <div 
        className={cn(
          "absolute right-8 top-[20vh] w-[480px] max-h-[70vh] rounded-lg border bg-background p-6 shadow-lg overflow-hidden flex flex-col",
          "animate-in slide-in-from-right duration-200",
          className
        )}
        onClick={e => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100"
        >
          <X className="h-4 w-4" />
          <span className="sr-only">Close</span>
        </button>
        <div className="overflow-y-auto flex-1 -mr-6 pr-6">
          {children}
        </div>
      </div>
    </div>
  )
}
