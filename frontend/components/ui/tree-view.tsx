"use client"

import * as React from "react"
import { ChevronDown, ChevronRight, Folder, File } from "lucide-react"
import { cn } from "@/lib/utils"

interface TreeItem {
  id: string
  name: string
  children?: TreeItem[]
  type: 'folder' | 'file' | 'directory' | 'divider'
  manufacturer?: string
  path?: string
}

interface TreeViewProps {
  items: TreeItem[]
  onSelect?: (item: TreeItem) => void
  className?: string
}

interface TreeNodeProps extends TreeItem {
  onSelect?: (item: TreeItem) => void
  level: number
}

const TreeNode: React.FC<TreeNodeProps> = ({
  id,
  name,
  children,
  type,
  onSelect,
  level,
  manufacturer,
  path,
}) => {
  const [isExpanded, setIsExpanded] = React.useState(false)
  const hasChildren = children && children.length > 0

  return (
    <div>
      <div
        className={cn(
          "flex items-center py-1 px-2 rounded-md",
          type === 'divider' ? "cursor-default" : "hover:bg-accent/50 cursor-pointer",
          "transition-colors duration-200"
        )}
        style={{ paddingLeft: `${level * 12 + 8}px` }}
        onClick={() => {
          if (type === 'divider') return
          if (hasChildren) {
            setIsExpanded(!isExpanded)
          }
          if (onSelect) {
            onSelect({ id, name, type, children, manufacturer, path })
          }
        }}
      >
        {type === 'divider' ? (
          <span className="text-sm text-muted-foreground">{name}</span>
        ) : (
          <div className="flex items-center gap-2">
            {hasChildren ? (
              isExpanded ? (
                <ChevronDown className="h-4 w-4 shrink-0 text-muted-foreground" />
              ) : (
                <ChevronRight className="h-4 w-4 shrink-0 text-muted-foreground" />
              )
            ) : (
              <span className="w-4" />
            )}
            {(type === 'folder' || type === 'directory') ? (
              <Folder className="h-4 w-4 shrink-0 text-primary" />
            ) : (
              <File className="h-4 w-4 shrink-0 text-muted-foreground" />
            )}
            <span className="text-sm">{name}</span>
          </div>
        )}
      </div>
      {hasChildren && isExpanded && (
        <div>
          {children.map((child) => (
            <TreeNode
              key={child.id}
              {...child}
              onSelect={onSelect}
              level={level + 1}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export const TreeView: React.FC<TreeViewProps> = ({
  items,
  onSelect,
  className,
}) => {
  return (
    <div className={cn("min-h-0 overflow-auto", className)}>
      {items.map((item) => (
        <TreeNode key={item.id} {...item} onSelect={onSelect} level={0} />
      ))}
    </div>
  )
}
