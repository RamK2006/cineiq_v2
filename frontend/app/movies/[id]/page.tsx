'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { motion } from 'framer-motion'
import { Star, Clock, Calendar, Users, Play, Heart } from 'lucide-react'

interface Movie {
  tmdb_id: number
  title: string
  overview: string
  release_date: string
  runtime: number
  genres: string[]
  director: string
  cast: Array<{ name: string; character: string }>
  vote_average: number
  poster_url: string
  backdrop_url: string
  tagline: string
}

export default function MovieDetailPage() {
  const params = useParams()
  const [movie, setMovie] = useState<Movie | null>(null)
  const [loading, setLoading] = useState(true)
  const [userRating, setUserRating] = useState<number>(0)

  useEffect(() => {
    fetchMovie()
  }, [params.id])

  const fetchMovie = async () => {
    try {
      // In production, use real API with auth
      const response = await fetch(`http://localhost:8000/api/v1/movies/${params.id}`, {
        headers: {
          'Authorization': 'Bearer YOUR_TOKEN'
        }
      })
      const data = await response.json()
      setMovie(data)
    } catch (error) {
      console.error('Failed to fetch movie:', error)
    } finally {
      setLoading(false)
    }
  }

  const submitRating = async (rating: number) => {
    setUserRating(rating)
    // Submit to API
    try {
      await fetch('http://localhost:8000/api/v1/users/ratings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer YOUR_TOKEN'
        },
        body: JSON.stringify({
          tmdb_id: params.id,
          rating: rating
        })
      })
    } catch (error) {
      console.error('Failed to submit rating:', error)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-2xl text-text-secondary">Loading...</div>
      </div>
    )
  }

  if (!movie) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-2xl text-text-secondary">Movie not found</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen">
      {/* Hero Section with Backdrop */}
      <div className="relative h-[70vh] overflow-hidden">
        {/* Backdrop Image */}
        <div 
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: `url(${movie.backdrop_url})` }}
        >
          <div className="absolute inset-0 bg-gradient-to-t from-bg-base via-bg-base/80 to-transparent" />
        </div>

        {/* Content */}
        <div className="relative z-10 h-full max-w-7xl mx-auto px-6 flex items-end pb-16">
          <div className="flex gap-8 items-end">
            {/* Poster */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="flex-shrink-0"
            >
              <img
                src={movie.poster_url}
                alt={movie.title}
                className="w-64 rounded-2xl shadow-2xl"
              />
            </motion.div>

            {/* Info */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="flex-1"
            >
              <h1 className="text-6xl font-bold mb-4">{movie.title}</h1>
              
              {movie.tagline && (
                <p className="text-xl text-text-secondary italic mb-6">
                  "{movie.tagline}"
                </p>
              )}

              <div className="flex gap-6 mb-6 text-text-secondary">
                <div className="flex items-center gap-2">
                  <Calendar className="w-5 h-5" />
                  <span>{new Date(movie.release_date).getFullYear()}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="w-5 h-5" />
                  <span>{movie.runtime} min</span>
                </div>
                <div className="flex items-center gap-2">
                  <Star className="w-5 h-5 text-accent-gold fill-accent-gold" />
                  <span className="font-mono">{movie.vote_average.toFixed(1)}/10</span>
                </div>
              </div>

              <div className="flex gap-3 mb-6">
                {movie.genres.map((genre) => (
                  <span
                    key={genre}
                    className="px-4 py-2 bg-bg-elevated rounded-lg text-sm border border-border"
                  >
                    {genre}
                  </span>
                ))}
              </div>

              <div className="flex gap-4">
                <button className="px-8 py-4 bg-gradient-to-r from-accent-primary to-accent-violet rounded-xl font-semibold flex items-center gap-2 hover:scale-105 transition-transform">
                  <Play className="w-5 h-5" />
                  Watch Together
                </button>
                <button className="px-8 py-4 glass rounded-xl font-semibold flex items-center gap-2 hover:scale-105 transition-transform">
                  <Heart className="w-5 h-5" />
                  Add to Watchlist
                </button>
              </div>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Details Section */}
      <div className="max-w-7xl mx-auto px-6 py-16">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Overview */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="glass p-8"
            >
              <h2 className="text-3xl font-bold mb-4">Overview</h2>
              <p className="text-text-secondary leading-relaxed text-lg">
                {movie.overview}
              </p>
            </motion.div>

            {/* Cast */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="glass p-8"
            >
              <h2 className="text-3xl font-bold mb-6">Cast</h2>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {movie.cast.slice(0, 6).map((actor, idx) => (
                  <div key={idx} className="text-center">
                    <div className="w-24 h-24 mx-auto mb-2 bg-bg-elevated rounded-full flex items-center justify-center">
                      <Users className="w-8 h-8 text-text-muted" />
                    </div>
                    <div className="font-semibold">{actor.name}</div>
                    <div className="text-sm text-text-muted">{actor.character}</div>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Rate This Movie */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.6 }}
              className="glass p-6"
            >
              <h3 className="text-xl font-bold mb-4">Rate This Movie</h3>
              <div className="flex gap-2 justify-center">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    onClick={() => submitRating(star)}
                    className="transition-transform hover:scale-110"
                  >
                    <Star
                      className={`w-8 h-8 ${
                        star <= userRating
                          ? 'text-accent-gold fill-accent-gold'
                          : 'text-text-muted'
                      }`}
                    />
                  </button>
                ))}
              </div>
              {userRating > 0 && (
                <p className="text-center mt-4 text-accent-green">
                  You rated this {userRating}/5 ⭐
                </p>
              )}
            </motion.div>

            {/* Director */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.7 }}
              className="glass p-6"
            >
              <h3 className="text-xl font-bold mb-2">Director</h3>
              <p className="text-text-secondary">{movie.director || 'Unknown'}</p>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  )
}
