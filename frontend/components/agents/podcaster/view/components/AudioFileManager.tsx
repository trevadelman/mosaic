"use client"

import { useState, useEffect } from 'react'
import { Trash2 } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

interface AudioFile {
  name: string
  size: number
  created: string
  modified: string
  format: string
  url: string
}

interface AudioFileManagerProps {
  onSelectFile: (file: AudioFile | null) => void
  selectedFile?: AudioFile | null
}

export function AudioFileManager({ onSelectFile, selectedFile }: AudioFileManagerProps) {
  const [files, setFiles] = useState<AudioFile[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Fetch audio files
  const fetchFiles = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/audio/list`)
      if (!response.ok) throw new Error('Failed to fetch audio files')
      const data = await response.json()
      setFiles(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load audio files')
      console.error('Error fetching audio files:', err)
    } finally {
      setLoading(false)
    }
  }

  // Delete file
  const handleDelete = async (file: AudioFile) => {
    if (!confirm(`Are you sure you want to delete ${file.name}?`)) return

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/audio/${file.name}`, {
        method: 'DELETE'
      })
      if (!response.ok) throw new Error('Failed to delete file')
      
      // Remove file from list
      setFiles(files.filter(f => f.name !== file.name))
      
      // If this was the selected file, clear it
      if (selectedFile?.name === file.name) {
        onSelectFile(null)
      }
    } catch (err) {
      console.error('Error deleting file:', err)
      alert('Failed to delete file')
    }
  }

  // Load files on mount
  useEffect(() => {
    fetchFiles()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 dark:border-gray-100"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center text-red-500 dark:text-red-400 p-4">
        <p>{error}</p>
        <button 
          onClick={fetchFiles}
          className="mt-2 text-sm text-blue-500 dark:text-blue-400 hover:underline"
        >
          Try again
        </button>
      </div>
    )
  }

  if (files.length === 0) {
    return (
      <div className="text-center text-gray-500 dark:text-gray-400 p-4">
        No audio files found
      </div>
    )
  }

  return (
    <div className="overflow-auto max-h-[400px]">
      <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead className="bg-gray-50 dark:bg-gray-800 sticky top-0">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Name
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Format
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Size
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Created
            </th>
            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
          {files.map((file) => (
            <tr 
              key={file.name}
              className={`hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer ${
                selectedFile?.name === file.name ? 'bg-blue-50 dark:bg-blue-900/50' : ''
              }`}
              onClick={() => onSelectFile(file)}
            >
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                {file.name}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400 uppercase">
                {file.format}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {(file.size / 1024).toFixed(1)} KB
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {formatDistanceToNow(new Date(file.created), { addSuffix: true })}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    handleDelete(file)
                  }}
                  className="text-red-600 hover:text-red-900 dark:text-red-500 dark:hover:text-red-400"
                  title="Delete file"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
