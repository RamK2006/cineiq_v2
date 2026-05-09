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
        'bg-base': '#0A0E1A',
        'bg-surface': '#111827',
        'bg-elevated': '#1E293B',
        'accent-primary': '#5B5FFF',
        'accent-secondary': '#A78BFA',
        'accent-cyan': '#38BDF8',
        'accent-green': '#4ADE80',
        'accent-amber': '#F59E0B',
        'accent-red': '#F87171',
        'accent-gold': '#F59E0B',
        'accent-violet': '#A78BFA',
        'text-primary': '#F1F5F9',
        'text-secondary': '#94A3B8',
        'text-muted': '#475569',
        'border': '#1E293B',
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}

export default config
