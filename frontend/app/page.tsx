'use client'

import { motion } from 'framer-motion'
import { Film, Sparkles, Users, Brain, TrendingUp, Zap } from 'lucide-react'

const features = [
  {
    icon: Brain,
    title: 'Hybrid ML Engine',
    description: 'SVD + Neural CF + Content-Based + Sentiment Re-ranking',
    color: 'from-purple-500 to-pink-500',
    delay: 0.1
  },
  {
    icon: Sparkles,
    title: 'Semantic Vibe Search',
    description: 'Natural language queries with sentence-transformers',
    color: 'from-cyan-500 to-blue-500',
    delay: 0.2
  },
  {
    icon: Users,
    title: 'Watch Together',
    description: 'Real-time sync with WebSocket rooms & reactions',
    color: 'from-orange-500 to-red-500',
    delay: 0.3
  },
  {
    icon: Zap,
    title: 'Explainable AI',
    description: 'LIME + Groq LLM insights for every recommendation',
    color: 'from-green-500 to-emerald-500',
    delay: 0.4
  },
  {
    icon: TrendingUp,
    title: 'Taste Evolution',
    description: 'Radar charts & timeline of your cinematic journey',
    color: 'from-yellow-500 to-amber-500',
    delay: 0.5
  },
  {
    icon: Film,
    title: 'Visual Similarity',
    description: 'CLIP embeddings for poster-based discovery',
    color: 'from-indigo-500 to-violet-500',
    delay: 0.6
  }
]

export default function Home() {
  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Animated background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-bg-base via-purple-900/10 to-bg-base" />
      
      {/* Floating orbs */}
      <motion.div
        className="absolute top-20 left-20 w-72 h-72 bg-accent-primary/20 rounded-full blur-3xl"
        animate={{
          scale: [1, 1.2, 1],
          opacity: [0.3, 0.5, 0.3],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />
      <motion.div
        className="absolute bottom-20 right-20 w-96 h-96 bg-accent-violet/20 rounded-full blur-3xl"
        animate={{
          scale: [1.2, 1, 1.2],
          opacity: [0.5, 0.3, 0.5],
        }}
        transition={{
          duration: 10,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />

      <main className="relative z-10 max-w-7xl mx-auto px-6 py-16">
        {/* Hero Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-20"
        >
          <motion.div
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.5 }}
            className="inline-block mb-6"
          >
            <div className="relative">
              <h1 className="text-8xl font-bold bg-gradient-to-r from-accent-primary via-accent-violet to-accent-cyan bg-clip-text text-transparent">
                CINEIQ
              </h1>
              <motion.div
                className="absolute -inset-4 bg-gradient-to-r from-accent-primary/20 to-accent-violet/20 blur-2xl -z-10"
                animate={{
                  opacity: [0.5, 0.8, 0.5],
                }}
                transition={{
                  duration: 3,
                  repeat: Infinity,
                }}
              />
            </div>
          </motion.div>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3, duration: 0.8 }}
            className="text-2xl text-text-secondary max-w-3xl mx-auto leading-relaxed"
          >
            Next-Gen Explainable Movie Intelligence & Social Discovery Platform
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.8 }}
            className="mt-8 flex gap-4 justify-center"
          >
            <button className="px-8 py-4 bg-gradient-to-r from-accent-primary to-accent-violet rounded-xl font-semibold text-lg hover:scale-105 transition-transform shadow-lg shadow-accent-primary/50">
              Explore Movies
            </button>
            <button className="px-8 py-4 glass rounded-xl font-semibold text-lg hover:scale-105 transition-transform">
              Watch Together
            </button>
          </motion.div>
        </motion.div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: feature.delay, duration: 0.5 }}
              whileHover={{ scale: 1.05, y: -5 }}
              className="glass p-6 group cursor-pointer relative overflow-hidden"
            >
              <motion.div
                className={`absolute inset-0 bg-gradient-to-br ${feature.color} opacity-0 group-hover:opacity-10 transition-opacity duration-300`}
              />
              
              <div className="relative z-10">
                <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${feature.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                  <feature.icon className="w-6 h-6 text-white" />
                </div>
                
                <h3 className="text-xl font-semibold mb-2 text-text-primary">
                  {feature.title}
                </h3>
                
                <p className="text-text-secondary text-sm leading-relaxed">
                  {feature.description}
                </p>
              </div>

              {/* Animated border */}
              <motion.div
                className="absolute inset-0 rounded-2xl"
                style={{
                  background: `linear-gradient(90deg, transparent, ${feature.color}, transparent)`,
                  opacity: 0,
                }}
                whileHover={{ opacity: 0.3 }}
              />
            </motion.div>
          ))}
        </div>

        {/* Tech Stack Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8, duration: 0.8 }}
          className="glass p-8 relative overflow-hidden"
        >
          <div className="absolute top-0 right-0 w-64 h-64 bg-accent-cyan/10 rounded-full blur-3xl" />
          
          <div className="relative z-10">
            <h2 className="text-3xl font-bold mb-6 bg-gradient-to-r from-accent-cyan to-accent-primary bg-clip-text text-transparent">
              Production-Ready Architecture
            </h2>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              {[
                { label: 'Backend', value: 'FastAPI', status: 'operational' },
                { label: 'Database', value: 'PostgreSQL 16', status: 'operational' },
                { label: 'Cache', value: 'Redis 7', status: 'operational' },
                { label: 'Vector DB', value: 'Qdrant', status: 'operational' },
                { label: 'ML - CF', value: 'SVD + NCF', status: 'training' },
                { label: 'ML - NLP', value: 'DistilBERT', status: 'training' },
                { label: 'Embeddings', value: 'Sentence-T', status: 'training' },
                { label: 'LLM', value: 'Groq Llama', status: 'ready' },
              ].map((item, i) => (
                <motion.div
                  key={item.label}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.9 + i * 0.05 }}
                  className="bg-bg-elevated/50 p-4 rounded-lg border border-border hover:border-accent-primary/50 transition-colors"
                >
                  <div className="text-xs text-text-muted mb-1 uppercase tracking-wider">
                    {item.label}
                  </div>
                  <div className="font-mono text-sm font-semibold text-text-primary mb-2">
                    {item.value}
                  </div>
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${
                      item.status === 'operational' ? 'bg-accent-green' :
                      item.status === 'training' ? 'bg-accent-amber animate-pulse' :
                      'bg-accent-cyan'
                    }`} />
                    <span className="text-xs text-text-muted capitalize">
                      {item.status}
                    </span>
                  </div>
                </motion.div>
              ))}
            </div>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.5 }}
              className="mt-8 p-4 bg-accent-amber/10 border border-accent-amber/30 rounded-lg"
            >
              <p className="text-sm text-text-secondary">
                <span className="font-semibold text-accent-amber">⚡ Quick Start:</span> Run{' '}
                <code className="font-mono bg-bg-base px-2 py-1 rounded text-accent-cyan">
                  make setup
                </code>{' '}
                to download MovieLens 25M, train models, and generate embeddings
              </p>
            </motion.div>
          </div>
        </motion.div>

        {/* Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.8 }}
          className="mt-16 text-center text-text-muted text-sm"
        >
          <p>IIT Guwahati Coding Club • Even Semester 2026 • Production-Ready ML Platform</p>
        </motion.div>
      </main>
    </div>
  )
}
