'use client'

import { motion, useScroll, useTransform, useSpring } from 'framer-motion'
import { Search, Play, Star, TrendingUp, Users, Sparkles } from 'lucide-react'
import { useRef, useState, useEffect } from 'react'
import InteractiveFeatures from './components/InteractiveFeatures'

const trendingMovies = [
  { 
    title: 'Dune: Part Two', 
    year: '2024', 
    rating: '8.8',
    genre: 'Sci-Fi Epic',
    color: 'from-amber-500 to-orange-600',
    image: 'https://image.tmdb.org/t/p/w500/8b8R8l88Qje9dn9OE8PY05Nxl1X.jpg'
  },
  { 
    title: 'Oppenheimer', 
    year: '2023', 
    rating: '8.5',
    genre: 'Historical Drama',
    color: 'from-purple-500 to-pink-600',
    image: 'https://image.tmdb.org/t/p/w500/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg'
  },
  { 
    title: 'The Substance', 
    year: '2024', 
    rating: '7.9',
    genre: 'Body Horror',
    color: 'from-cyan-500 to-blue-600',
    image: 'https://image.tmdb.org/t/p/w500/lqoMzCcZYEFK729d6qzt349fB4o.jpg'
  },
  { 
    title: 'Poor Things', 
    year: '2023', 
    rating: '8.2',
    genre: 'Dark Comedy',
    color: 'from-pink-500 to-rose-600',
    image: 'https://image.tmdb.org/t/p/w500/kCGlIMHnOm8JPXq3rXM6c5wMxcT.jpg'
  },
]

const vibeChips = [
  { label: 'slow burn', icon: '🔥', color: 'from-orange-500 to-red-600' },
  { label: 'neon noir', icon: '🌃', color: 'from-purple-500 to-pink-600' },
  { label: 'emotional gut-punch', icon: '💔', color: 'from-blue-500 to-cyan-600' },
  { label: 'mind-bending', icon: '🌀', color: 'from-violet-500 to-purple-600' },
]

export default function Home() {
  const [searchValue, setSearchValue] = useState('')
  const [hoveredMovie, setHoveredMovie] = useState<number | null>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const heroRef = useRef<HTMLDivElement>(null)
  const moviesRef = useRef<HTMLDivElement>(null)
  
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end end"]
  })

  const { scrollYProgress: heroProgress } = useScroll({
    target: heroRef,
    offset: ["start start", "end start"]
  })

  const { scrollYProgress: moviesProgress } = useScroll({
    target: moviesRef,
    offset: ["start end", "end start"]
  })

  const heroOpacity = useTransform(heroProgress, [0, 0.5], [1, 0])
  const heroScale = useTransform(heroProgress, [0, 0.5], [1, 0.95])
  const heroY = useTransform(heroProgress, [0, 1], [0, -100])
  
  const moviesRotateX = useTransform(moviesProgress, [0, 0.5, 1], [15, 0, -15])
  const moviesY = useTransform(moviesProgress, [0, 0.5, 1], [100, 0, -100])
  
  const springConfig = { stiffness: 100, damping: 30, restDelta: 0.001 }
  const moviesRotateXSpring = useSpring(moviesRotateX, springConfig)
  const moviesYSpring = useSpring(moviesY, springConfig)

  return (
    <div ref={containerRef} className="min-h-screen bg-bg-base text-text-primary overflow-x-hidden">
      {/* Gradient Mesh Background */}
      <div className="gradient-mesh" />
      <div className="film-grain fixed inset-0 pointer-events-none" />

      {/* NAVBAR */}
      <motion.nav 
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="fixed top-0 left-0 right-0 z-50 glass border-b border-white/5"
      >
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <motion.div 
            className="font-bebas text-3xl tracking-wider text-white"
            whileHover={{ scale: 1.05 }}
          >
            CINEIQ
          </motion.div>
          <div className="flex items-center gap-6">
            <button className="text-text-secondary hover:text-white transition-colors text-sm font-medium">
              Sign In
            </button>
            <motion.button 
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="px-6 py-2.5 bg-gradient-to-r from-accent-amber to-orange-500 text-black font-mono text-sm font-medium rounded-lg glow-amber"
            >
              Get Started
            </motion.button>
          </div>
        </div>
      </motion.nav>

      {/* HERO SECTION */}
      <motion.section 
        ref={heroRef}
        style={{ opacity: heroOpacity, scale: heroScale, y: heroY }}
        className="relative min-h-screen pt-32 pb-20 px-6 flex items-center"
      >
        <div className="max-w-7xl mx-auto w-full">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            {/* Left Column */}
            <div className="space-y-8">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
              >
                <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass border border-accent-amber/20 mb-6">
                  <Sparkles className="w-4 h-4 text-accent-amber" />
                  <span className="font-mono text-xs text-accent-amber tracking-wider">
                    AI-POWERED FILM DISCOVERY
                  </span>
                </div>
                
                <h1 className="font-bebas text-7xl lg:text-8xl leading-[0.9] mb-6">
                  <span className="bg-gradient-to-r from-white via-white to-text-secondary bg-clip-text text-transparent">
                    Find Films That
                  </span>
                  <br />
                  <span className="bg-gradient-to-r from-accent-amber via-orange-500 to-accent-pink bg-clip-text text-transparent">
                    Feel Like You
                  </span>
                </h1>

                <p className="text-text-secondary text-lg leading-relaxed max-w-xl">
                  Describe a mood, a scene, or a feeling. Get personalized film recommendations powered by AI that actually understands what you're looking for.
                </p>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.4 }}
                className="space-y-4"
              >
                <div className="relative group">
                  <div className="absolute -inset-0.5 bg-gradient-to-r from-accent-amber via-accent-purple to-accent-cyan rounded-xl opacity-30 group-hover:opacity-50 blur transition duration-300" />
                  <div className="relative flex items-center">
                    <input
                      type="text"
                      value={searchValue}
                      onChange={(e) => setSearchValue(e.target.value)}
                      placeholder="a film that feels like a fever dream at 2am..."
                      className="w-full px-6 py-5 bg-bg-surface/90 backdrop-blur-xl border border-white/10 text-white font-mono text-sm placeholder:text-text-muted rounded-xl focus:outline-none focus:border-accent-amber/50 transition-all"
                    />
                    <motion.button 
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                      className="absolute right-3 p-3 bg-gradient-to-r from-accent-amber to-orange-500 rounded-lg glow-amber"
                    >
                      <Search className="w-5 h-5 text-black" />
                    </motion.button>
                  </div>
                </div>

                <div className="flex flex-wrap gap-3">
                  {vibeChips.map((chip, index) => (
                    <motion.button
                      key={chip.label}
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ duration: 0.4, delay: 0.5 + index * 0.1 }}
                      whileHover={{ scale: 1.05, y: -2 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => setSearchValue(chip.label)}
                      className="group relative px-5 py-2.5 glass rounded-lg overflow-hidden"
                    >
                      <div className={`absolute inset-0 bg-gradient-to-r ${chip.color} opacity-0 group-hover:opacity-20 transition-opacity`} />
                      <span className="relative font-mono text-xs text-text-secondary group-hover:text-white transition-colors flex items-center gap-2">
                        <span>{chip.icon}</span>
                        {chip.label}
                      </span>
                    </motion.button>
                  ))}
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.8 }}
                className="flex items-center gap-8 pt-4"
              >
                <div className="flex items-center gap-2">
                  <div className="flex -space-x-2">
                    {[1, 2, 3, 4].map((i) => (
                      <div key={i} className="w-8 h-8 rounded-full bg-gradient-to-br from-accent-purple to-accent-pink border-2 border-bg-base" />
                    ))}
                  </div>
                  <span className="text-text-secondary text-sm">
                    <span className="text-white font-semibold">12.5K+</span> film lovers
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <Star className="w-5 h-5 text-accent-amber fill-accent-amber" />
                  <span className="text-text-secondary text-sm">
                    <span className="text-white font-semibold">4.9</span> rating
                  </span>
                </div>
              </motion.div>
            </div>

            {/* Right Column - 3D Movie Cards */}
            <motion.div
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.3 }}
              className="relative h-[600px] hidden lg:block"
              style={{ perspective: '1000px' }}
            >
              <div className="absolute inset-0">
                {trendingMovies.slice(0, 3).map((movie, index) => (
                  <motion.div
                    key={movie.title}
                    className="absolute w-64 h-96 cursor-pointer"
                    style={{
                      left: `${index * 80}px`,
                      top: `${index * 40}px`,
                      zIndex: hoveredMovie === index ? 10 : 3 - index,
                    }}
                    animate={{
                      y: [0, -10, 0],
                      rotateY: hoveredMovie === index ? 0 : index * 5,
                      rotateZ: hoveredMovie === index ? 0 : index * -2,
                    }}
                    transition={{
                      y: {
                        duration: 3 + index * 0.5,
                        repeat: Infinity,
                        ease: "easeInOut"
                      },
                      rotateY: { duration: 0.3 },
                      rotateZ: { duration: 0.3 }
                    }}
                    whileHover={{ scale: 1.05, z: 50 }}
                    onHoverStart={() => setHoveredMovie(index)}
                    onHoverEnd={() => setHoveredMovie(null)}
                  >
                    <div className="relative w-full h-full rounded-2xl overflow-hidden group">
                      <div className={`absolute inset-0 bg-gradient-to-br ${movie.color} opacity-20 group-hover:opacity-40 transition-opacity`} />
                      <img 
                        src={movie.image}
                        alt={movie.title}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          e.currentTarget.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="600"%3E%3Crect fill="%231a1a1a" width="400" height="600"/%3E%3C/svg%3E'
                        }}
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-black via-black/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
                        <div className="absolute bottom-0 left-0 right-0 p-6">
                          <div className="flex items-center gap-2 mb-2">
                            <Star className="w-4 h-4 text-accent-amber fill-accent-amber" />
                            <span className="text-white font-semibold">{movie.rating}</span>
                          </div>
                          <h3 className="font-bebas text-2xl text-white mb-1">{movie.title}</h3>
                          <p className="text-text-secondary text-sm">{movie.genre} • {movie.year}</p>
                        </div>
                      </div>
                      <motion.div
                        className="absolute top-4 right-4 w-12 h-12 bg-black/50 backdrop-blur-xl rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100"
                        whileHover={{ scale: 1.1 }}
                      >
                        <Play className="w-5 h-5 text-white fill-white ml-0.5" />
                      </motion.div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </div>
        </div>
      </motion.section>

      {/* TRENDING MOVIES SECTION - 3D Scroll Effect */}
      <section ref={moviesRef} className="relative py-32 px-6">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6 }}
            className="text-center mb-16"
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass border border-accent-purple/20 mb-6">
              <TrendingUp className="w-4 h-4 text-accent-purple" />
              <span className="font-mono text-xs text-accent-purple tracking-wider">
                TRENDING NOW
              </span>
            </div>
            <h2 className="font-bebas text-6xl mb-4">
              <span className="bg-gradient-to-r from-white to-text-secondary bg-clip-text text-transparent">
                What Everyone's Watching
              </span>
            </h2>
          </motion.div>

          <motion.div
            style={{
              rotateX: moviesRotateXSpring,
              y: moviesYSpring,
              transformStyle: 'preserve-3d',
            }}
            className="grid grid-cols-2 lg:grid-cols-4 gap-6"
          >
            {trendingMovies.map((movie, index) => (
              <motion.div
                key={movie.title}
                initial={{ opacity: 0, y: 50 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-50px" }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                whileHover={{ scale: 1.05, z: 50 }}
                className="group relative rounded-2xl overflow-hidden cursor-pointer"
                style={{ transformStyle: 'preserve-3d' }}
              >
                <div className="aspect-[2/3] relative">
                  <div className={`absolute inset-0 bg-gradient-to-br ${movie.color} opacity-20 group-hover:opacity-40 transition-opacity`} />
                  <img 
                    src={movie.image}
                    alt={movie.title}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.currentTarget.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="600"%3E%3Crect fill="%231a1a1a" width="400" height="600"/%3E%3C/svg%3E'
                    }}
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black via-black/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
                    <div className="absolute bottom-0 left-0 right-0 p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <Star className="w-4 h-4 text-accent-amber fill-accent-amber" />
                        <span className="text-white font-semibold text-sm">{movie.rating}</span>
                      </div>
                      <h3 className="font-bebas text-xl text-white mb-1">{movie.title}</h3>
                      <p className="text-text-secondary text-xs">{movie.genre}</p>
                    </div>
                  </div>
                  <motion.div
                    className="absolute top-3 right-3 w-10 h-10 bg-black/50 backdrop-blur-xl rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100"
                    whileHover={{ scale: 1.1 }}
                  >
                    <Play className="w-4 h-4 text-white fill-white ml-0.5" />
                  </motion.div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* FEATURES SECTION - Interactive with Backend */}
      <InteractiveFeatures />

      {/* CTA SECTION */}
      <section className="relative py-32 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="relative p-16 glass rounded-3xl overflow-hidden"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-accent-amber/20 via-accent-purple/20 to-accent-cyan/20" />
            <div className="relative">
              <h2 className="font-bebas text-6xl mb-6">
                <span className="bg-gradient-to-r from-white to-text-secondary bg-clip-text text-transparent">
                  Ready to Find Your Film?
                </span>
              </h2>
              <p className="text-text-secondary text-lg mb-8 max-w-2xl mx-auto">
                Join thousands of film lovers discovering their next favorite movie
              </p>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-10 py-4 bg-gradient-to-r from-accent-amber via-orange-500 to-accent-pink text-black font-mono text-sm font-medium rounded-xl glow-amber inline-flex items-center gap-3"
              >
                Start Exploring
                <Play className="w-5 h-5 fill-black" />
              </motion.button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="relative py-12 px-6 border-t border-white/5">
        <div className="max-w-7xl mx-auto text-center">
          <div className="font-bebas text-2xl text-white mb-4">CINEIQ</div>
          <p className="font-mono text-xs text-text-muted">
            © 2026 CineIQ. Discover films that feel like you.
          </p>
        </div>
      </footer>
    </div>
  )
}
