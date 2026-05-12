import type { Metadata } from 'next'
import { Bebas_Neue, Space_Grotesk, JetBrains_Mono } from 'next/font/google'
import './globals.css'

const bebasNeue = Bebas_Neue({ weight: '400', subsets: ['latin'], variable: '--font-bebas' })
const spaceGrotesk = Space_Grotesk({ subsets: ['latin'], variable: '--font-space', weight: ['400', '500', '600', '700'] })
const jetbrainsMono = JetBrains_Mono({ subsets: ['latin'], variable: '--font-mono', weight: ['400', '500', '600'] })

export const metadata: Metadata = {
  title: 'CINEIQ - Explainable Movie Recommendations',
  description: 'Next-gen movie discovery with AI-powered recommendations',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${bebasNeue.variable} ${spaceGrotesk.variable} ${jetbrainsMono.variable} font-space bg-bg-base text-text-primary antialiased`}>
        {children}
      </body>
    </html>
  )
}
