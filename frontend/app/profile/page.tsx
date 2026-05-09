'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Star, TrendingUp, Film, Upload } from 'lucide-react'
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer } from 'recharts'

interface UserProfile {
  user_id: string
  display_name: string
  total_ratings: number
  average_rating: number
  top_genres: Array<{
    genre: string
    average_rating: number
    count: number
    affinity: number
  }>
  rating_distribution: Record<string, number>
}

export default function ProfilePage() {
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchProfile()
  }, [])

  const fetchProfile = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/users/profile', {
        headers: {
          'Authorization': 'Bearer YOUR_TOKEN'
        }
      })
      const data = await response.json()
      setProfile(data)
    } catch (error) {
      console.error('Failed to fetch profile:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('http://localhost:8000/api/v1/import/letterboxd', {
        method: 'POST',
        headers: {
          'Authorization': 'Bearer YOUR_TOKEN'
        },
        body: formData
      })
      const data = await response.json()
      alert(`Imported ${data.imported} ratings!`)
      fetchProfile() // Refresh profile
    } catch (error) {
      console.error('Import failed:', error)
      alert('Import failed')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-2xl text-text-secondary">Loading profile...</div>
      </div>
    )
  }

  if (!profile) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-2xl text-text-secondary">Profile not found</div>
      </div>
    )
  }

  // Prepare radar chart data
  const radarData = profile.top_genres.slice(0, 8).map(g => ({
    genre: g.genre,
    affinity: g.affinity * 100
  }))

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-12"
        >
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-accent-violet to-accent-primary bg-clip-text text-transparent">
            Your Taste Profile
          </h1>
          <p className="text-xl text-text-secondary">
            {profile.display_name}'s cinematic journey
          </p>
        </motion.div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="glass p-6"
          >
            <div className="flex items-center gap-4 mb-2">
              <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-accent-primary to-accent-violet flex items-center justify-center">
                <Film className="w-6 h-6" />
              </div>
              <div>
                <div className="text-3xl font-bold font-mono">{profile.total_ratings}</div>
                <div className="text-sm text-text-muted">Movies Rated</div>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="glass p-6"
          >
            <div className="flex items-center gap-4 mb-2">
              <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-accent-gold to-accent-amber flex items-center justify-center">
                <Star className="w-6 h-6" />
              </div>
              <div>
                <div className="text-3xl font-bold font-mono">{profile.average_rating.toFixed(1)}</div>
                <div className="text-sm text-text-muted">Average Rating</div>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="glass p-6"
          >
            <div className="flex items-center gap-4 mb-2">
              <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-accent-cyan to-accent-green flex items-center justify-center">
                <TrendingUp className="w-6 h-6" />
              </div>
              <div>
                <div className="text-3xl font-bold">{profile.top_genres[0]?.genre || 'N/A'}</div>
                <div className="text-sm text-text-muted">Top Genre</div>
              </div>
            </div>
          </motion.div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Taste Radar */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
            className="glass p-8"
          >
            <h2 className="text-2xl font-bold mb-6">Genre Affinity Radar</h2>
            <ResponsiveContainer width="100%" height={400}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="#1E293B" />
                <PolarAngleAxis 
                  dataKey="genre" 
                  tick={{ fill: '#94A3B8', fontSize: 12 }}
                />
                <PolarRadiusAxis 
                  angle={90} 
                  domain={[0, 100]}
                  tick={{ fill: '#94A3B8' }}
                />
                <Radar
                  name="Affinity"
                  dataKey="affinity"
                  stroke="#5B5FFF"
                  fill="#5B5FFF"
                  fillOpacity={0.6}
                />
              </RadarChart>
            </ResponsiveContainer>
          </motion.div>

          {/* Top Genres List */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 }}
            className="glass p-8"
          >
            <h2 className="text-2xl font-bold mb-6">Top Genres</h2>
            <div className="space-y-4">
              {profile.top_genres.slice(0, 10).map((genre, index) => (
                <div key={genre.genre} className="flex items-center gap-4">
                  <div className="w-8 h-8 rounded-lg bg-bg-elevated flex items-center justify-center font-mono text-sm">
                    {index + 1}
                  </div>
                  <div className="flex-1">
                    <div className="flex justify-between mb-1">
                      <span className="font-semibold">{genre.genre}</span>
                      <span className="font-mono text-sm text-text-muted">
                        {genre.average_rating.toFixed(1)} ⭐ ({genre.count} movies)
                      </span>
                    </div>
                    <div className="h-2 bg-bg-elevated rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${genre.affinity * 100}%` }}
                        transition={{ delay: 0.6 + index * 0.05, duration: 0.5 }}
                        className="h-full bg-gradient-to-r from-accent-primary to-accent-violet"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Import Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="glass p-8 mt-8"
        >
          <h2 className="text-2xl font-bold mb-4">Import Your Ratings</h2>
          <p className="text-text-secondary mb-6">
            Import your movie ratings from Letterboxd or Trakt to get personalized recommendations
          </p>
          
          <label className="inline-block px-8 py-4 bg-gradient-to-r from-accent-primary to-accent-violet rounded-xl font-semibold cursor-pointer hover:scale-105 transition-transform">
            <Upload className="inline-block w-5 h-5 mr-2" />
            Upload Letterboxd CSV
            <input
              type="file"
              accept=".csv"
              onChange={handleFileUpload}
              className="hidden"
            />
          </label>
          
          <p className="text-sm text-text-muted mt-4">
            Export your data from Letterboxd: Settings → Import & Export → Export Your Data
          </p>
        </motion.div>
      </div>
    </div>
  )
}
