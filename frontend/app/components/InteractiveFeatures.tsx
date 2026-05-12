'use client'

import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion'
import { Search, Sparkles, Users, TrendingUp, Zap, Film, Heart, MessageCircle } from 'lucide-react'
import { useState, useRef } from 'react'

const features = [
  {
    id: 'semantic-search',
    icon: Sparkles,
    title: 'Vibe Search',
    description: 'Describe a mood, get perfect matches',
    endpoint: '/api/v1/search/semantic',
    action: 'Try It',
    gradient: 'from-amber-500 via-orange-500 to-red-500',
    demo: {
      placeholder: 'dark psychological thriller with twist ending...',
      examples: ['mind-bending', 'feel-good', 'neon noir']
    }
  },
  {
    id: 'recommendations',
    icon: TrendingUp,
    title: 'AI Recommendations',
    description: 'Personalized picks that evolve with you',
    endpoint: '/api/v1/recommend',
    action: 'Get Recommendations',
    gradient: 'from-purple-500 via-pink-500 to-rose-500',
    demo: {
      info: 'Hybrid ML: SVD + NCF + Content + Sentiment'
    }
  },
  {
    id: 'watch-together',
    icon: Users,
    title: 'Watch Together',
    description: 'Sync playback, chat, react in real-time',
    endpoint: '/api/v1/rooms/create',
    action: 'Create Room',
    gradient: 'from-cyan-500 via-blue-500 to-indigo-500',
    demo: {
      info: 'WebSocket sync • Live reactions • Group chat'
    }
  },
  {
    id: 'similar-movies',
    icon: Film,
    title: 'Similar Films',
    description: 'Content-based vector similarity',
    endpoint: '/api/v1/similar',
    action: 'Find Similar',
    gradient: 'from-green-500 via-emerald-500 to-teal-500',
    demo: {
      info: 'Qdrant vector search • Plot embeddings'
    }
  },
  {
    id: 'trending',
    icon: Zap,
    title: 'Trending Now',
    description: "What everyone's watching this week",
    endpoint: '/api/v1/movies/trending',
    action: 'See Trending',
    gradient: 'from-yellow-500 via-amber-500 to-orange-500',
    demo: {
      info: 'TMDB API • Real-time data • Cached'
    }
  },
  {
    id: 'taste-profile',
    icon: Heart,
    title: 'Taste Evolution',
    description: 'Track your cinematic journey',
    endpoint: '/api/v1/users/profile',
    action: 'View Profile',
    gradient: 'from-pink-500 via-rose-500 to-red-500',
    demo: {
      info: 'Radar charts • Timeline • Genre analysis'
    }
  },
]

export default function InteractiveFeatures() {
  const [hoveredFeature, setHoveredFeature] = useState<string | null>(null)
  const [activeDemo, setActiveDemo] = useState<string | null>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  const handleFeatureClick = async (feature: typeof features[0]) => {
    setActiveDemo(feature.id)
    
    // Simulate API call
    console.log(`Calling ${feature.endpoint}`)
    
    // In production, you'd make actual API calls here
    // const response = await fetch(`http://localhost:8000${feature.endpoint}`)
    // const data = await response.json()
  }

  return (
    <section className="relative py-32 px-6 overflow-hidden">
      {/* Background effects */}
      <div className="absolute inset-0 opacity-30">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-cyan-500/20 rounded-full blur-3xl" />
      </div>

      <div className="max-w-7xl mx-auto relative z-10">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6 }}
          className="text-center mb-20"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass border border-accent-amber/20 mb-6">
            <Zap className="w-4 h-4 text-accent-amber" />
            <span className="font-mono text-xs text-accent-amber tracking-wider uppercase">
              Powered by AI
            </span>
          </div>
          <h2 className="font-bebas text-7xl mb-6">
            <span className="bg-gradient-to-r from-white via-text-primary to-text-secondary bg-clip-text text-transparent">
              Try It Yourself
            </span>
          </h2>
          <p className="text-text-secondary text-xl max-w-2xl mx-auto">
            Every feature is live and connected to our backend. Click to interact.
          </p>
        </motion.div>

        {/* Interactive Feature Grid */}
        <div 
          ref={containerRef}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
          style={{ perspective: '1000px' }}
        >
          {features.map((feature, index) => (
            <FeatureCard
              key={feature.id}
              feature={feature}
              index={index}
              isHovered={hoveredFeature === feature.id}
              isActive={activeDemo === feature.id}
              onHover={() => setHoveredFeature(feature.id)}
              onLeave={() => setHoveredFeature(null)}
              onClick={() => handleFeatureClick(feature)}
            />
          ))}
        </div>

        {/* Active Demo Display */}
        {activeDemo && (
          <motion.div
            initial={{ opacity: 0, y: 50, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 50, scale: 0.9 }}
            className="mt-12 p-8 glass rounded-2xl border border-white/10"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-bebas text-3xl text-white">
                {features.find(f => f.id === activeDemo)?.title} Demo
              </h3>
              <button
                onClick={() => setActiveDemo(null)}
                className="text-text-muted hover:text-white transition-colors"
              >
                Close
              </button>
            </div>
            <div className="h-64 flex items-center justify-center border border-white/5 rounded-xl bg-bg-base/50">
              <p className="text-text-muted font-mono text-sm">
                Demo interface would load here with live backend connection
              </p>
            </div>
          </motion.div>
        )}
      </div>
    </section>
  )
}

interface FeatureCardProps {
  feature: typeof features[0]
  index: number
  isHovered: boolean
  isActive: boolean
  onHover: () => void
  onLeave: () => void
  onClick: () => void
}

function FeatureCard({ feature, index, isHovered, isActive, onHover, onLeave, onClick }: FeatureCardProps) {
  const cardRef = useRef<HTMLDivElement>(null)
  const mouseX = useMotionValue(0)
  const mouseY = useMotionValue(0)

  const rotateX = useSpring(useTransform(mouseY, [-0.5, 0.5], [10, -10]), {
    stiffness: 300,
    damping: 30
  })
  const rotateY = useSpring(useTransform(mouseX, [-0.5, 0.5], [-10, 10]), {
    stiffness: 300,
    damping: 30
  })

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return
    const rect = cardRef.current.getBoundingClientRect()
    const centerX = rect.left + rect.width / 2
    const centerY = rect.top + rect.height / 2
    mouseX.set((e.clientX - centerX) / rect.width)
    mouseY.set((e.clientY - centerY) / rect.height)
  }

  const handleMouseLeave = () => {
    mouseX.set(0)
    mouseY.set(0)
    onLeave()
  }

  return (
    <motion.div
      ref={cardRef}
      initial={{ opacity: 0, y: 50 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-50px" }}
      transition={{ duration: 0.6, delay: index * 0.1 }}
      style={{
        rotateX: isHovered ? rotateX : 0,
        rotateY: isHovered ? rotateY : 0,
        transformStyle: 'preserve-3d',
      }}
      onMouseMove={handleMouseMove}
      onMouseEnter={onHover}
      onMouseLeave={handleMouseLeave}
      className="group relative"
    >
      <div className="relative p-8 glass rounded-2xl overflow-hidden cursor-pointer transition-all duration-300 hover:border-white/20">
        {/* Gradient overlay */}
        <div 
          className={`absolute inset-0 bg-gradient-to-br ${feature.gradient} opacity-0 group-hover:opacity-10 transition-opacity duration-300`}
          style={{ transform: 'translateZ(0)' }}
        />

        {/* Animated gradient border */}
        <motion.div
          className={`absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity`}
          style={{
            background: `linear-gradient(135deg, transparent 0%, transparent 40%, ${feature.gradient.split(' ')[1]} 50%, transparent 60%, transparent 100%)`,
            backgroundSize: '200% 200%',
          }}
          animate={isHovered ? {
            backgroundPosition: ['0% 0%', '100% 100%'],
          } : {}}
          transition={{
            duration: 2,
            repeat: Infinity,
            repeatType: 'reverse'
          }}
        />

        {/* Content */}
        <div className="relative z-10" style={{ transform: 'translateZ(20px)' }}>
          {/* Icon */}
          <motion.div
            className={`w-16 h-16 rounded-xl bg-gradient-to-br ${feature.gradient} flex items-center justify-center mb-6 group-hover:scale-110 transition-transform`}
            animate={isHovered ? {
              rotateY: [0, 360],
            } : {}}
            transition={{
              duration: 0.8,
            }}
          >
            <feature.icon className="w-8 h-8 text-white" />
          </motion.div>

          {/* Title */}
          <h3 className="font-bebas text-3xl text-white mb-3 group-hover:text-transparent group-hover:bg-gradient-to-r group-hover:bg-clip-text" style={{ backgroundImage: `linear-gradient(to right, ${feature.gradient})` }}>
            {feature.title}
          </h3>

          {/* Description */}
          <p className="text-text-secondary text-sm leading-relaxed mb-6">
            {feature.description}
          </p>

          {/* Demo info */}
          {feature.demo.info && (
            <div className="mb-6 p-3 bg-bg-base/50 rounded-lg border border-white/5">
              <p className="font-mono text-xs text-text-muted">
                {feature.demo.info}
              </p>
            </div>
          )}

          {/* Action button */}
          <motion.button
            onClick={onClick}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className={`w-full px-6 py-3 bg-gradient-to-r ${feature.gradient} text-white font-mono text-sm font-medium rounded-lg relative overflow-hidden group/btn`}
          >
            <span className="relative z-10">{feature.action}</span>
            <motion.div
              className="absolute inset-0 bg-white/20"
              initial={{ x: '-100%' }}
              whileHover={{ x: '100%' }}
              transition={{ duration: 0.5 }}
            />
          </motion.button>

          {/* Endpoint badge */}
          <div className="mt-4 flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <span className="font-mono text-xs text-text-muted">
              {feature.endpoint}
            </span>
          </div>
        </div>

        {/* 3D depth effect */}
        <div 
          className="absolute inset-0 rounded-2xl bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"
          style={{ transform: 'translateZ(10px)' }}
        />
      </div>
    </motion.div>
  )
}
