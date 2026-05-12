import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'bg-base': '#0A0A0A',
        'bg-surface': '#1A1A1A',
        'text-primary': '#FFFFFF',
        'text-secondary': '#B8B8B8',
        'text-muted': '#6B6B6B',
        'accent-amber': '#E8A838',
        'accent-purple': '#8B5CF6',
        'accent-cyan': '#06B6D4',
        'accent-pink': '#EC4899',
      },
      fontFamily: {
        bebas: ['var(--font-bebas)'],
        space: ['var(--font-space)'],
        mono: ['var(--font-mono)'],
      },
    },
  },
  plugins: [],
}

export default config
