import { TableDetails } from "../hooks/useTableDetails"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { Badge } from "@/components/ui/badge"

interface TableDetailsProps {
  details: TableDetails | null
  loading: boolean
  error: string | null
}

export function TableDetailsPanel({ details, loading, error }: TableDetailsProps) {
  if (loading) {
    return (
      <div className="w-full space-y-4">
        <Skeleton className="h-8 w-3/4" />
        <Skeleton className="h-32 w-full" />
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

  if (!details) {
    return (
      <div className="w-full h-full flex items-center justify-center text-muted-foreground">
        <p>Select a table to view details</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <span>{details.name}</span>
            <Badge variant="outline">Table</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {/* Columns */}
            <div>
              <h3 className="font-semibold mb-2">Columns</h3>
              <div className="border rounded-lg">
                <table className="w-full">
                  <thead>
                    <tr className="border-b bg-muted/50">
                      <th className="text-left p-2 text-sm">Name</th>
                      <th className="text-left p-2 text-sm">Type</th>
                      <th className="text-left p-2 text-sm">Nullable</th>
                      <th className="text-left p-2 text-sm">Default</th>
                    </tr>
                  </thead>
                  <tbody>
                    {details.columns.map((column) => (
                      <tr key={column.name} className="border-b last:border-0">
                        <td className="p-2">
                          <div className="flex items-center gap-2">
                            <span>{column.name}</span>
                            {column.is_primary_key && (
                              <Badge className="bg-amber-500">PK</Badge>
                            )}
                          </div>
                        </td>
                        <td className="p-2">
                          <code className="text-sm bg-muted px-1 py-0.5 rounded">
                            {column.type}
                          </code>
                        </td>
                        <td className="p-2">
                          {column.nullable ? "Yes" : "No"}
                        </td>
                        <td className="p-2">
                          {column.default ? (
                            <code className="text-sm bg-muted px-1 py-0.5 rounded">
                              {column.default}
                            </code>
                          ) : (
                            <span className="text-muted-foreground">null</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Foreign Keys */}
            {details.foreign_keys.length > 0 && (
              <div>
                <h3 className="font-semibold mb-2">Foreign Keys</h3>
                <div className="border rounded-lg">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        <th className="text-left p-2 text-sm">Column</th>
                        <th className="text-left p-2 text-sm">References</th>
                      </tr>
                    </thead>
                    <tbody>
                      {details.foreign_keys.map((fk, index) => (
                        <tr key={index} className="border-b last:border-0">
                          <td className="p-2">{fk.column}</td>
                          <td className="p-2">
                            <code className="text-sm bg-muted px-1 py-0.5 rounded">
                              {fk.references.table}.{fk.references.column}
                            </code>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Indexes */}
            {details.indexes.length > 0 && (
              <div>
                <h3 className="font-semibold mb-2">Indexes</h3>
                <div className="border rounded-lg">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        <th className="text-left p-2 text-sm">Name</th>
                        <th className="text-left p-2 text-sm">Columns</th>
                        <th className="text-left p-2 text-sm">Type</th>
                      </tr>
                    </thead>
                    <tbody>
                      {details.indexes.map((index) => (
                        <tr key={index.name} className="border-b last:border-0">
                          <td className="p-2">{index.name}</td>
                          <td className="p-2">
                            <code className="text-sm bg-muted px-1 py-0.5 rounded">
                              {index.columns.join(", ")}
                            </code>
                          </td>
                          <td className="p-2">
                            <Badge variant={index.unique ? "default" : "secondary"}>
                              {index.unique ? "Unique" : "Non-unique"}
                            </Badge>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
