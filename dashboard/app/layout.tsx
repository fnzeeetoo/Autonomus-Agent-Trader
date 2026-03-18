import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'AgentTrader Dashboard',
  description: 'Dashboard for AgentTrader',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-gray-100 min-h-screen">
        <nav className="bg-gray-800 text-white p-4">
          <div className="container mx-auto flex space-x-4">
            <a href="/" className="hover:underline">Equity</a>
            <a href="/trades" className="hover:underline">Trades</a>
            <a href="/config" className="hover:underline">Config</a>
          </div>
        </nav>
        <main className="container mx-auto p-4">
          {children}
        </main>
      </body>
    </html>
  )
}
