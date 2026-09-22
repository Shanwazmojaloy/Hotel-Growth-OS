import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Hotel Growth OS',
  description: 'Hotel growth operations dashboard',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
