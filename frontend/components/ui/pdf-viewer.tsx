"use client"

import { useEffect, useRef } from "react"

interface PdfViewerProps {
  url: string
  height?: string
  className?: string
}

export function PdfViewer({ url, height = "100%", className = "" }: PdfViewerProps) {
  const iframeRef = useRef<HTMLIFrameElement>(null)

  useEffect(() => {
    // Ensure iframe is sized correctly
    if (iframeRef.current) {
      iframeRef.current.style.height = height
    }
  }, [height])

  return (
    <iframe
      ref={iframeRef}
      src={`${url}#toolbar=0`}
      className={`w-full ${className}`}
      style={{ height }}
    />
  )
}
