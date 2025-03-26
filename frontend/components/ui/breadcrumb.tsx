import { ChevronRight } from "lucide-react"
import Link from "next/link"
import { cn } from "@/lib/utils"

interface BreadcrumbProps {
  items: {
    label: string
    href?: string
  }[]
}

export function Breadcrumb({ items }: BreadcrumbProps) {
  return (
    <nav className="flex items-center space-x-1 text-sm text-muted-foreground">
      {items.map((item, index) => {
        const isLast = index === items.length - 1
        
        return (
          <div key={item.label} className="flex items-center">
            {index > 0 && <ChevronRight className="h-4 w-4 mx-1" />}
            {item.href && !isLast ? (
              <Link
                href={item.href}
                className="hover:text-foreground transition-colors"
              >
                {item.label}
              </Link>
            ) : (
              <span className={cn(isLast && "text-foreground font-medium")}>
                {item.label}
              </span>
            )}
          </div>
        )
      })}
    </nav>
  )
}
