import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { ThemeProvider } from '@/components/theme-provider'
import { Sidebar } from '@/components/sidebar/sidebar'
import { WebSocketProvider } from '@/lib/contexts/websocket-context'
import { ToastProvider } from '@/components/ui/toast'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'MOSAIC - Multi-agent Orchestration System',
  description: 'Multi-agent Orchestration System for Adaptive Intelligent Collaboration',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem
          disableTransitionOnChange
        >
          <WebSocketProvider>
            <ToastProvider>
              <div className="flex h-screen">
                <Sidebar />
                <div className="flex-1 overflow-auto">
                  {children}
                </div>
              </div>
            </ToastProvider>
          </WebSocketProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}
