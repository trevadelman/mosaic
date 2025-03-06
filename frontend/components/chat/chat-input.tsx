"use client"

import { useState, useRef, useEffect } from "react"
import { Send, Paperclip, X, Image, FileText, Loader2 } from "lucide-react"
import { Attachment } from "@/lib/types"

interface ChatInputProps {
  onSendMessage: (message: string, attachments?: File[]) => void
  isDisabled?: boolean
  isProcessing?: boolean
  placeholder?: string
}

export function ChatInput({
  onSendMessage,
  isDisabled = false,
  isProcessing = false,
  placeholder = "Type a message..."
}: ChatInputProps) {
  const [message, setMessage] = useState("")
  const [files, setFiles] = useState<File[]>([])
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Auto-resize textarea based on content
  useEffect(() => {
    const textarea = textareaRef.current
    if (!textarea) return

    textarea.style.height = "auto"
    textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`
  }, [message])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if ((!message.trim() && files.length === 0) || isDisabled) return
    
    onSendMessage(message, files.length > 0 ? files : undefined)
    setMessage("")
    setFiles([])
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Submit on Enter (without Shift)
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const newFiles = Array.from(e.target.files)
      setFiles(prev => [...prev, ...newFiles])
    }
  }

  const handleRemoveFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }

  const openFileSelector = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click()
    }
  }

  const getFileIcon = (file: File) => {
    if (file.type.startsWith('image/')) {
      return <Image className="h-4 w-4" />
    }
    return <FileText className="h-4 w-4" />
  }

  return (
    <form onSubmit={handleSubmit} className="relative">
      {/* File attachments preview */}
      {files.length > 0 && (
        <div className="mb-2 flex flex-wrap gap-2">
          {files.map((file, index) => (
            <div 
              key={index} 
              className={`flex items-center gap-2 rounded-md border ${
                isProcessing && file.type.startsWith('image/') 
                  ? 'bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800' 
                  : 'bg-muted/50'
              } px-3 py-1 text-xs`}
            >
              {isProcessing && file.type.startsWith('image/') ? (
                <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />
              ) : (
                getFileIcon(file)
              )}
              <span className="max-w-[150px] truncate">{file.name}</span>
              {!isProcessing && (
                <button
                  type="button"
                  onClick={() => handleRemoveFile(index)}
                  className="text-muted-foreground hover:text-foreground"
                >
                  <X className="h-3 w-3" />
                  <span className="sr-only">Remove file</span>
                </button>
              )}
            </div>
          ))}
        </div>
      )}
      
      {/* Processing indicator */}
      {isProcessing && files.some(file => file.type.startsWith('image/')) && (
        <div className="mb-2 text-xs text-blue-500 flex items-center gap-1">
          <Loader2 className="h-3 w-3 animate-spin" />
          <span>Processing image{files.filter(f => f.type.startsWith('image/')).length > 1 ? 's' : ''}...</span>
        </div>
      )}

      <div className="relative flex items-center rounded-lg border bg-background p-1 shadow-sm focus-within:ring-1 focus-within:ring-ring">
        {/* File input (hidden) */}
        <input
          ref={fileInputRef}
          type="file"
          multiple
          onChange={handleFileChange}
          className="hidden"
          accept="image/*,.pdf,.doc,.docx,.txt"
          disabled={isDisabled}
        />
        
        {/* File attachment button */}
        <button
          type="button"
          onClick={openFileSelector}
          disabled={isDisabled}
          className="inline-flex h-8 w-8 items-center justify-center rounded-md text-muted-foreground hover:bg-muted hover:text-foreground disabled:pointer-events-none disabled:opacity-50"
        >
          <Paperclip className="h-4 w-4" />
          <span className="sr-only">Attach file</span>
        </button>
        
        {/* Message input */}
        <textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={isDisabled}
          rows={1}
          className="flex-1 resize-none bg-transparent px-3 py-2 placeholder:text-muted-foreground focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50"
        />
        
        {/* Send button */}
        <button
          type="submit"
          disabled={(message.trim() === "" && files.length === 0) || isDisabled || isProcessing}
          className="inline-flex h-8 w-8 items-center justify-center rounded-md bg-primary text-primary-foreground shadow-sm hover:bg-primary/90 disabled:pointer-events-none disabled:opacity-50"
        >
          {isProcessing ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Send className="h-4 w-4" />
          )}
          <span className="sr-only">{isProcessing ? "Processing" : "Send message"}</span>
        </button>
      </div>
      <p className="mt-1 text-xs text-muted-foreground">
        Press <kbd className="rounded border px-1 py-0.5 text-xs">Enter</kbd> to send,{" "}
        <kbd className="rounded border px-1 py-0.5 text-xs">Shift + Enter</kbd> for new line
      </p>
    </form>
  )
}
