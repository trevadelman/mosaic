"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import {
  BrainCircuit,
  Home,
  MessageSquare,
  Plus,
  Settings,
  Users,
} from "lucide-react"
import { ThemeToggle } from "../theme-toggle"

const items = [
  {
    name: "Home",
    href: "/",
    icon: Home,
  },
  {
    name: "Chat",
    href: "/chat",
    icon: MessageSquare,
  },
  {
    name: "Agents",
    href: "/agents",
    icon: BrainCircuit,
  },
  {
    name: "Create Agent",
    href: "/agents/create",
    icon: Plus,
  },
  {
    name: "Community",
    href: "/community",
    icon: Users,
  },
  {
    name: "Settings",
    href: "/settings",
    icon: Settings,
  },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <div className="flex h-full w-[80px] flex-col items-center justify-between border-r bg-background py-4">
      <div className="flex flex-col items-center gap-4">
        <Link href="/" className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary text-primary-foreground">
          <BrainCircuit className="h-6 w-6" />
        </Link>
        <div className="h-px w-10 bg-border" />
        <nav className="flex flex-col items-center gap-4">
          {items.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex h-10 w-10 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:text-foreground",
                pathname === item.href && "bg-accent text-accent-foreground"
              )}
            >
              <item.icon className="h-5 w-5" />
              <span className="sr-only">{item.name}</span>
            </Link>
          ))}
        </nav>
      </div>
      <div className="mt-auto pt-4">
        <ThemeToggle />
      </div>
    </div>
  )
}
