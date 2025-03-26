import { useState, useEffect } from 'react'

export interface Node {
  id: string
  group: 'table' | 'column'
  label: string
}

export interface Link {
  source: string
  target: string
  type: 'contains' | 'references'
}

export interface GraphData {
  nodes: Node[]
  links: Link[]
}

export function useGraphData() {
  const [data, setData] = useState<GraphData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      setError(null)
      
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/apps/db-visualizer/graph`)
        
        if (!response.ok) {
          throw new Error(`Error: ${response.status} ${response.statusText}`)
        }
        
        const data = await response.json()
        setData(data)
      } catch (error) {
        setError(error instanceof Error ? error.message : 'An error occurred')
        console.error('Error fetching graph data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  return { data, loading, error }
}
