import { useState } from 'react'

export interface ColumnDetail {
  name: string
  type: string
  nullable: boolean
  default: string | null
  is_primary_key: boolean
}

export interface ForeignKeyDetail {
  column: string
  references: {
    table: string
    column: string
  }
}

export interface IndexDetail {
  name: string
  columns: string[]
  unique: boolean
}

export interface TableDetails {
  name: string
  columns: ColumnDetail[]
  primary_key: string[]
  foreign_keys: ForeignKeyDetail[]
  indexes: IndexDetail[]
}

export function useTableDetails() {
  const [details, setDetails] = useState<TableDetails | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchTableDetails = async (tableName: string) => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/apps/db-visualizer/tables/${tableName}`)
      
      if (!response.ok) {
        throw new Error(`Error: ${response.status} ${response.statusText}`)
      }
      
      const data = await response.json()
      setDetails(data)
    } catch (error) {
      setError(error instanceof Error ? error.message : 'An error occurred')
      console.error('Error fetching table details:', error)
    } finally {
      setLoading(false)
    }
  }

  return { details, loading, error, fetchTableDetails }
}
