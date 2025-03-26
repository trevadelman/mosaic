"use client"

import Link from "next/link"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Database, Layout, LineChart } from "lucide-react"

const applications = [
  {
    id: "hello-world",
    name: "Hello World",
    description: "A simple example application",
    icon: "👋",
    color: "bg-blue-500"
  },
  {
    id: "db-visualizer",
    name: "Database Visualizer",
    description: "Interactive visualization of the database structure",
    icon: <Database className="w-8 h-8" />,
    color: "bg-purple-500"
  },
  {
    id: "financial-analysis",
    name: "Financial Analysis",
    description: "Analyze stocks with technical and fundamental indicators",
    icon: <LineChart className="w-8 h-8" />,
    color: "bg-green-500"
  }
]

export default function ApplicationsPage() {
  return (
    <div className="container py-10">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold">Applications</h1>
          <p className="text-muted-foreground mt-1">
            Custom applications built on the Mosaic platform
          </p>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {applications.map(app => (
          <Link href={`/apps/${app.id}`} key={app.id} className="block">
            <Card className="h-full hover:shadow-md transition-shadow">
              <CardHeader className={`${app.color} text-white rounded-t-lg`}>
                <div className="text-3xl mb-2">
                  {typeof app.icon === "string" ? app.icon : app.icon}
                </div>
                <CardTitle>{app.name}</CardTitle>
              </CardHeader>
              <CardContent className="pt-4">
                <CardDescription className="text-base text-foreground/80">
                  {app.description}
                </CardDescription>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  )
}
