"use client"

import { useState } from "react"
import { Message as MessageType } from "@/lib/types"
import { BrainCircuit, User, AlertCircle, Copy, Check, ChevronDown, ChevronUp, Terminal, FileText, Image, Download } from "lucide-react"
import { formatDistanceToNow } from "date-fns"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"

interface MessageProps {
  message: MessageType
  isLastMessage?: boolean
}

export function Message({ message, isLastMessage = false }: MessageProps) {
  const [copied, setCopied] = useState(false)
  const [showLogs, setShowLogs] = useState(isLastMessage)

  const copyToClipboard = () => {
    navigator.clipboard.writeText(message.content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const isUser = message.role === "user"
  const isError = message.status === "error"
  const hasLogs = message.logs && message.logs.length > 0
  const hasAttachments = message.attachments && message.attachments.length > 0
  const formattedTime = formatDistanceToNow(new Date(message.timestamp), { 
    addSuffix: true 
  })

  const getAttachmentIcon = (type: string) => {
    if (type.startsWith('image/')) {
      return <Image className="h-4 w-4" />
    }
    return <FileText className="h-4 w-4" />
  }

  return (
    <div
      className={`group relative flex gap-3 px-4 py-6 ${
        isUser ? "" : "bg-muted/40"
      }`}
    >
      <div className="flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-md border bg-background shadow">
        {isUser ? (
          <User className="h-4 w-4" />
        ) : (
          <BrainCircuit className="h-4 w-4" />
        )}
      </div>
      <div className="flex-1 space-y-2">
        <div className="flex items-center gap-2">
          <div className="font-semibold">
            {isUser ? "You" : message.agentId || "Assistant"}
          </div>
          <div className="text-xs text-muted-foreground">{formattedTime}</div>
          {isError && (
            <div className="flex items-center text-xs text-destructive">
              <AlertCircle className="mr-1 h-3 w-3" />
              Error
            </div>
          )}
          {hasLogs && !isUser && (
            <button
              onClick={() => setShowLogs(!showLogs)}
              className="ml-auto flex items-center text-xs text-muted-foreground hover:text-foreground"
            >
              <Terminal className="mr-1 h-3 w-3" />
              {showLogs ? "Hide logs" : "Show logs"}
              {showLogs ? (
                <ChevronUp className="ml-1 h-3 w-3" />
              ) : (
                <ChevronDown className="ml-1 h-3 w-3" />
              )}
            </button>
          )}
        </div>
        
        {/* Attachments section */}
        {hasAttachments && (
          <div className="mb-2 flex flex-wrap gap-2">
            {message.attachments!.map((attachment, index) => (
              <div 
                key={index} 
                className="flex items-center gap-2 rounded-md border bg-muted/50 px-3 py-1 text-xs"
              >
                {getAttachmentIcon(attachment.type)}
                <span className="max-w-[150px] truncate">{attachment.filename}</span>
                {attachment.url && (
                  <a
                    href={attachment.url}
                    download={attachment.filename}
                    className="text-muted-foreground hover:text-foreground"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <Download className="h-3 w-3" />
                    <span className="sr-only">Download file</span>
                  </a>
                )}
              </div>
            ))}
          </div>
        )}
        
        {/* Image attachments preview */}
        {hasAttachments && message.attachments!.some(a => a.type.startsWith('image/')) && (
          <div className="mb-4 flex flex-wrap gap-2">
            {message.attachments!
              .filter(a => a.type.startsWith('image/'))
              .map((attachment, index) => (
                <div key={index} className="relative overflow-hidden rounded-md border">
                  {attachment.data ? (
                    <img 
                      src={`data:${attachment.type};base64,${attachment.data}`} 
                      alt={attachment.filename}
                      className="max-h-64 object-contain"
                    />
                  ) : attachment.url ? (
                    <img 
                      src={attachment.url} 
                      alt={attachment.filename}
                      className="max-h-64 object-contain"
                    />
                  ) : null}
                </div>
              ))
            }
          </div>
        )}
        
        {/* Logs section */}
        {hasLogs && showLogs && !isUser && (
          <div className="mb-4 rounded-md border bg-black p-3 text-xs text-white font-mono overflow-auto max-h-60">
            <div className="text-green-400 mb-2">Agent Logs:</div>
            {message.logs!.map((log, i) => (
              <div key={i} className="mb-1 last:mb-0 whitespace-pre-wrap">
                {log}
              </div>
            ))}
          </div>
        )}
        
        <div className="prose prose-sm dark:prose-invert max-w-none">
          {isUser ? (
            // For user messages, keep the simple text rendering
            message.content.split("\n").map((line, i) => (
              <p key={i} className={line.trim() === "" ? "h-4" : undefined}>
                {line}
              </p>
            ))
          ) : (
            // For assistant messages, render markdown
            <div className="markdown-content">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.content}
              </ReactMarkdown>
            </div>
          )}
        </div>
      </div>
      <button
        onClick={copyToClipboard}
        className="absolute right-4 top-6 opacity-0 transition-opacity group-hover:opacity-100"
        aria-label="Copy message"
      >
        {copied ? (
          <Check className="h-4 w-4 text-green-500" />
        ) : (
          <Copy className="h-4 w-4 text-muted-foreground" />
        )}
      </button>
    </div>
  )
}
