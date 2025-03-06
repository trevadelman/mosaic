import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import Link from 'next/link'
import { BrainCircuit } from 'lucide-react'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Authentication - MOSAIC',
  description: 'Sign in or sign up to MOSAIC',
}

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gray-50 dark:bg-gray-900 p-4">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <Link href="/" className="inline-flex items-center justify-center">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary text-primary-foreground mx-auto mb-4">
              <BrainCircuit className="h-6 w-6" />
            </div>
          </Link>
          <h1 className="text-4xl font-bold tracking-tight text-gray-900 dark:text-gray-100">MOSAIC</h1>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Multi-agent Orchestration System for Adaptive Intelligent Collaboration
          </p>
        </div>
        {children}
      </div>
    </div>
  )
}
