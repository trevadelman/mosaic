"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import {
  BrainCircuit,
  Home,
  LogIn,
  LogOut,
  MessageSquare,
  Settings,
  User,
  Layout,
} from "lucide-react"
import { ThemeToggle } from "../theme-toggle"
import { SignInButton, SignOutButton, useAuth, useUser } from "@clerk/nextjs"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

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
    name: "Applications",
    href: "/apps",
    icon: Layout,
  },
  {
    name: "Settings",
    href: "/settings",
    icon: Settings,
  },
]

export function Sidebar() {
  const pathname = usePathname()
  const { isSignedIn } = useAuth()
  const { user } = useUser()

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
      <div className="mt-auto flex flex-col items-center gap-4">
        {isSignedIn ? (
          <div className="relative">
            {/* User status indicator - green dot */}
            <div className="absolute -top-1 -right-1 h-3 w-3 rounded-full bg-green-500 border-2 border-background"></div>
            
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button
                  className="flex h-10 w-10 items-center justify-center rounded-full bg-accent text-accent-foreground transition-colors hover:bg-accent/80"
                  title={`Signed in as ${user?.fullName || user?.username || 'User'}`}
                >
                  <User className="h-5 w-5" />
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="center" sideOffset={10} className="w-48 rounded-xl">
                <DropdownMenuLabel>
                  <div className="flex flex-col">
                    <span className="font-medium">{user?.fullName || user?.username}</span>
                    <span className="text-xs text-muted-foreground">{user?.primaryEmailAddress?.emailAddress}</span>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <Link href="/settings">
                  <DropdownMenuItem>
                    <Settings className="mr-2 h-4 w-4" />
                    <span>Settings</span>
                  </DropdownMenuItem>
                </Link>
                <DropdownMenuSeparator />
                <SignOutButton>
                  <DropdownMenuItem>
                    <LogOut className="mr-2 h-4 w-4" />
                    <span>Sign out</span>
                  </DropdownMenuItem>
                </SignOutButton>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        ) : (
          <SignInButton mode="modal">
            <button
              className="flex h-10 w-10 items-center justify-center rounded-full bg-accent text-accent-foreground transition-colors hover:bg-accent/80"
              title="Sign in"
            >
              <LogIn className="h-5 w-5" />
              <span className="sr-only">Sign in</span>
            </button>
          </SignInButton>
        )}
        <ThemeToggle />
      </div>
    </div>
  )
}
