import { useState } from 'react'

export interface TableData {
  columns: string[]
  rows: Record<string, any>[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export function useTableData() {
  const [data, setData] = useState<TableData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchTableData = async (tableName: string, page: number = 1, pageSize: number = 50) => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/apps/db-visualizer/tables/${tableName}/data?page=${page}&page_size=${pageSize}`
      )
      
      if (!response.ok) {
        throw new Error(`Error: ${response.status} ${response.statusText}`)
      }
      
      const data = await response.json()
      setData(data)
    } catch (error) {
      setError(error instanceof Error ? error.message : 'An error occurred')
      console.error('Error fetching table data:', error)
    } finally {
      setLoading(false)
    }
  }

  return { data, loading, error, fetchTableData }
}
