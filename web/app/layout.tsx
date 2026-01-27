import type { Metadata, Viewport } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'CIMEIKA - Українська персональна система',
  description: 'Система управління знаннями та подіями',
  manifest: '/manifest.json',
}

export const viewport: Viewport = {
  themeColor: '#0b0f14',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="uk">
      <body>{children}</body>
    </html>
  )
}
