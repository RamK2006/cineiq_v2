'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Search, Mic, Filter, Star } from 'lucide-react'
import Link from 'next/link'

interface SearchResult {
  tmdb_id: number
  title: string
  overview: string
  genres: string[]
  year: string
  rating: number
  similarity_score: number
  poster_url?: string
}

const vibePresets = [
  { label: 'Mind-Bending', emoji: '🧠', query: 'mind-bending' },
  { label: 'Feel-Good', emoji: '😊', query: 'feel-good' },
  { label: 'Dark & Atmospheric', emoji: '🌑', query: 'dark-atmospheric' },
  { label: 'Action-Packed', emoji: '💥', query: 'action-packed' },
  { label: 'Romantic', emoji: '❤️', query: 'romantic' },
  { label: 'Scary', emoji: '😱', query: 'scary' },
  { label: 'Epic Adventure', emoji: '⚔️', query: 'epic' },
  { label: 'Funny', emoji: '😂', query: 'funny' }
]

export default function SearchPage() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [searchType, setSearchType] = useState<'semantic' | 'vibe'>('semantic')

  const handleSearch = async (searchQuery: string = query) => {
    if (!searchQuery.trim()) return

    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/api/v1/search/semantic', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer YOUR_TOKEN'
        },
        body: JSON.stringify({
          query: searchQuery,
          limit: 20
        })
      })
      const data = await response.json()
      setResults(data.results || [])
    } catch (error) {
      console.error('Search failed:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleVibeSearch = async (vibe: string) => {
    setLoading(true)
    try {
      const response = await fetch(`http://localhost:8000/api/v1/search/vibe?vibe=${vibe}&limit=20`, {
        headers: {
          'Authorization': 'Bearer YOUR_TOKEN'
        }
      })
      const data = await response.json()
      setResults(data.results || [])
    } catch (error) {
      console.error('Vibe search failed:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-12"
        >
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-accent-cyan to-accent-primary bg-clip-text text-transparent">
            Discover Movies
          </h1>
          <p className="text-xl text-text-secondary">
            Search by vibe, mood, or natural language
          </p>
        </motion.div>

        {/* Search Bar */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="glass p-6 mb-8"
        >
          <div className="flex gap-4 mb-4">
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-text-muted" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                placeholder="Try: 'dark psychological thriller with twist ending'"
                className="w-full pl-12 pr-4 py-4 bg-bg-elevated rounded-xl border border-border focus:border-accent-primary outline-none text-lg"
              />
            </div>
            <button
              onClick={() => handleSearch()}
              disabled={loading}
              className="px-8 py-4 bg-gradient-to-r from-accent-primary to-accent-violet rounded-xl font-semibold hover:scale-105 transition-transform disabled:opacity-50"
            >
              {loading ? 'Searching...' : 'Search'}
            </button>
            <button className="px-6 py-4 glass rounded-xl hover:scale-105 transition-transform">
              <Mic className="w-5 h-5" />
            </button>
          </div>

          {/* Vibe Presets */}
          <div className="flex flex-wrap gap-3">
            {vibePresets.map((preset) => (
              <button
                key={preset.query}
                onClick={() => handleVibeSearch(preset.query)}
                className="px-4 py-2 bg-bg-elevated rounded-lg border border-border hover:border-accent-primary transition-colors text-sm"
              >
                <span className="mr-2">{preset.emoji}</span>
                {preset.label}
              </button>
            ))}
          </div>
        </motion.div>

        {/* Results */}
        <AnimatePresence mode="wait">
          {loading ? (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="text-center py-20"
            >
              <div className="inline-block w-16 h-16 border-4 border-accent-primary border-t-transparent rounded-full animate-spin" />
              <p className="mt-4 text-text-secondary">Searching the cinematic universe...</p>
            </motion.div>
          ) : results.length > 0 ? (
            <motion.div
              key="results"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6"
            >
              {results.map((movie, index) => (
                <motion.div
                  key={movie.tmdb_id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  whileHover={{ scale: 1.05, y: -5 }}
                  className="group cursor-pointer"
                >
                  <Link href={`/movies/${movie.tmdb_id}`}>
                    <div className="relative overflow-hidden rounded-xl mb-3">
                      {movie.poster_url ? (
                        <img
                          src={movie.poster_url}
                          alt={movie.title}
                          className="w-full aspect-[2/3] object-cover"
                        />
                      ) : (
                        <div className="w-full aspect-[2/3] bg-bg-elevated flex items-center justify-center">
                          <span className="text-4xl">🎬</span>
                        </div>
                      )}
                      
                      {/* Overlay */}
                      <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
                        <div className="absolute bottom-0 left-0 right-0 p-4">
                          <div className="flex items-center gap-2 text-sm">
                            <Star className="w-4 h-4 text-accent-gold fill-accent-gold" />
                            <span className="font-mono">{movie.rating?.toFixed(1)}</span>
                          </div>
                          {movie.similarity_score && (
                            <div className="mt-2 text-xs text-accent-cyan">
                              {(movie.similarity_score * 100).toFixed(0)}% match
                            </div>
                          )}
                        </div>
                      </div>
                    </div>

                    <h3 className="font-semibold line-clamp-2 mb-1">{movie.title}</h3>
                    <p className="text-sm text-text-muted">{movie.year}</p>
                    
                    {movie.genres && movie.genres.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {movie.genres.slice(0, 2).map((genre) => (
                          <span
                            key={genre}
                            className="text-xs px-2 py-1 bg-bg-elevated rounded"
                          >
                            {genre}
                          </span>
                        ))}
                      </div>
                    )}
                  </Link>
                </motion.div>
              ))}
            </motion.div>
          ) : (
            <motion.div
              key="empty"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="text-center py-20"
            >
              <div className="text-6xl mb-4">🔍</div>
              <p className="text-xl text-text-secondary">
                Start searching to discover amazing movies
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
