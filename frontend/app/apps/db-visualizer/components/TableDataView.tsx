import { TableData } from "../hooks/useTableData"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"

interface TableDataViewProps {
  data: TableData | null
  loading: boolean
  error: string | null
  onPageChange: (page: number) => void
}

export function TableDataView({ data, loading, error, onPageChange }: TableDataViewProps) {
  if (loading) {
    return (
      <div className="w-full h-[400px] flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="w-full p-4 text-destructive bg-destructive/10 rounded-lg">
        <p>{error}</p>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="w-full h-full flex items-center justify-center text-muted-foreground">
        <p>Select a table to view data</p>
      </div>
    )
  }

  return (
    <div className="space-y-4 overflow-hidden">
      <div className="border rounded-lg overflow-x-auto max-h-[50vh]">
        <table className="w-full">
          <thead>
            <tr className="border-b bg-muted/50">
              {data.columns.map((column) => (
                <th key={column} className="text-left p-2 text-sm">
                  {column}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.rows.map((row, index) => (
              <tr key={index} className="border-b last:border-0">
                {data.columns.map((column) => (
                  <td key={column} className="p-2">
                    <div className="max-w-[300px] truncate" title={row[column]?.toString() ?? ""}>
                      {row[column]?.toString() ?? ""}
                    </div>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination and Row Count */}
      <div className="flex items-center justify-between mt-4 px-1">
        <div className="text-sm text-muted-foreground">
          {data.total} total rows
          {data.total_pages > 1 && ` • Page ${data.page} of ${data.total_pages}`}
        </div>
        {data.total_pages > 1 && (
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => onPageChange(data.page - 1)}
              disabled={data.page <= 1}
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onPageChange(data.page + 1)}
              disabled={data.page >= data.total_pages}
            >
              Next
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}
