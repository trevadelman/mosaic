"use client"

import React from 'react'
import Editor from '@monaco-editor/react'
import { useTheme } from 'next-themes'

interface JsonViewerProps {
  content: string
  height?: string
}

export function JsonViewer({ content, height = "500px" }: JsonViewerProps) {
  const { theme } = useTheme()
  
  return (
    <Editor
      height={height}
      language="json"
      value={content}
      theme={theme === 'dark' ? 'vs-dark' : 'vs'}
      options={{
        readOnly: true,
        minimap: { enabled: false },
        scrollBeyondLastLine: false,
        fontSize: 14,
        wordWrap: 'on',
        automaticLayout: true,
        formatOnPaste: true,
        formatOnType: true,
      }}
    />
  )
}
