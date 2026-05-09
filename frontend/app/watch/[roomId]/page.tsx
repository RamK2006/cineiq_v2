'use client'

import { useEffect, useState, useRef } from 'react'
import { useParams } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { Play, Pause, Users, MessageCircle, Heart, Laugh, ThumbsUp, Fire } from 'lucide-react'

interface Participant {
  user_id: string
  display_name: string
}

interface ChatMessage {
  type: 'chat_message' | 'user_joined' | 'user_left'
  user_id: string
  display_name: string
  message?: string
  timestamp: string
}

interface Reaction {
  emoji: string
  x: number
  id: string
}

export default function WatchTogetherPage() {
  const params = useParams()
  const [ws, setWs] = useState<WebSocket | null>(null)
  const [connected, setConnected] = useState(false)
  const [participants, setParticipants] = useState<Participant[]>([])
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [chatInput, setChatInput] = useState('')
  const [playbackState, setPlaybackState] = useState<'playing' | 'paused'>('paused')
  const [currentTime, setCurrentTime] = useState(0)
  const [reactions, setReactions] = useState<Reaction[]>([])
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Connect to WebSocket
    const websocket = new WebSocket(
      `ws://localhost:8000/api/v1/ws/room/${params.roomId}?user_id=user123&display_name=Guest`
    )

    websocket.onopen = () => {
      console.log('WebSocket connected')
      setConnected(true)
    }

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      console.log('Received:', data)

      switch (data.type) {
        case 'room_state':
          setPlaybackState(data.state.playback_state)
          setCurrentTime(data.state.current_time)
          break

        case 'user_joined':
        case 'user_left':
          setMessages(prev => [...prev, data])
          break

        case 'playback_sync':
          setPlaybackState(data.state)
          setCurrentTime(data.time)
          break

        case 'chat_message':
          setMessages(prev => [...prev, data])
          scrollToBottom()
          break

        case 'reaction':
          addReaction(data.emoji)
          break
      }
    }

    websocket.onclose = () => {
      console.log('WebSocket disconnected')
      setConnected(false)
    }

    setWs(websocket)

    return () => {
      websocket.close()
    }
  }, [params.roomId])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handlePlayPause = () => {
    if (!ws) return

    const newState = playbackState === 'playing' ? 'paused' : 'playing'
    
    ws.send(JSON.stringify({
      type: 'playback',
      action: newState === 'playing' ? 'play' : 'pause',
      time: currentTime
    }))

    setPlaybackState(newState)
  }

  const sendMessage = () => {
    if (!ws || !chatInput.trim()) return

    ws.send(JSON.stringify({
      type: 'chat',
      text: chatInput
    }))

    setChatInput('')
  }

  const sendReaction = (emoji: string) => {
    if (!ws) return

    ws.send(JSON.stringify({
      type: 'reaction',
      emoji: emoji
    }))

    addReaction(emoji)
  }

  const addReaction = (emoji: string) => {
    const id = Math.random().toString(36)
    const x = Math.random() * 80 + 10 // 10-90%
    
    setReactions(prev => [...prev, { emoji, x, id }])

    // Remove after animation
    setTimeout(() => {
      setReactions(prev => prev.filter(r => r.id !== id))
    }, 3000)
  }

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold mb-2">Watch Together</h1>
              <p className="text-text-secondary">
                Room: <span className="font-mono text-accent-cyan">{params.roomId}</span>
              </p>
            </div>
            <div className="flex items-center gap-3 glass px-6 py-3 rounded-xl">
              <div className={`w-3 h-3 rounded-full ${connected ? 'bg-accent-green' : 'bg-accent-red'} animate-pulse`} />
              <span className="text-sm">{connected ? 'Connected' : 'Disconnected'}</span>
              <Users className="w-5 h-5 ml-2" />
              <span className="font-mono">{participants.length}</span>
            </div>
          </div>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Video Player Area */}
          <div className="lg:col-span-3 space-y-6">
            {/* Player */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="relative aspect-video bg-black rounded-2xl overflow-hidden"
            >
              {/* Placeholder for video player */}
              <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-bg-elevated to-bg-base">
                <div className="text-center">
                  <div className="text-6xl mb-4">🎬</div>
                  <p className="text-xl text-text-secondary">Video Player Placeholder</p>
                  <p className="text-sm text-text-muted mt-2">
                    In production, integrate with your video streaming service
                  </p>
                </div>
              </div>

              {/* Floating Reactions */}
              <AnimatePresence>
                {reactions.map((reaction) => (
                  <motion.div
                    key={reaction.id}
                    initial={{ y: 0, opacity: 1, scale: 1 }}
                    animate={{ y: -300, opacity: 0, scale: 1.5 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 3, ease: 'easeOut' }}
                    className="absolute bottom-20 text-4xl pointer-events-none"
                    style={{ left: `${reaction.x}%` }}
                  >
                    {reaction.emoji}
                  </motion.div>
                ))}
              </AnimatePresence>

              {/* Controls */}
              <div className="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-black/80 to-transparent">
                <div className="flex items-center gap-4">
                  <button
                    onClick={handlePlayPause}
                    className="w-12 h-12 rounded-full bg-accent-primary flex items-center justify-center hover:scale-110 transition-transform"
                  >
                    {playbackState === 'playing' ? (
                      <Pause className="w-6 h-6" />
                    ) : (
                      <Play className="w-6 h-6 ml-1" />
                    )}
                  </button>

                  <div className="flex-1">
                    <div className="h-2 bg-white/20 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-accent-primary"
                        style={{ width: '30%' }}
                      />
                    </div>
                  </div>

                  <span className="font-mono text-sm">
                    {Math.floor(currentTime / 60)}:{(currentTime % 60).toString().padStart(2, '0')}
                  </span>
                </div>
              </div>
            </motion.div>

            {/* Reaction Buttons */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="glass p-4 flex gap-3 justify-center"
            >
              {[
                { emoji: '❤️', icon: Heart },
                { emoji: '😂', icon: Laugh },
                { emoji: '👍', icon: ThumbsUp },
                { emoji: '🔥', icon: Fire }
              ].map(({ emoji, icon: Icon }) => (
                <button
                  key={emoji}
                  onClick={() => sendReaction(emoji)}
                  className="w-12 h-12 rounded-xl bg-bg-elevated hover:bg-bg-elevated/80 flex items-center justify-center hover:scale-110 transition-transform"
                >
                  <span className="text-2xl">{emoji}</span>
                </button>
              ))}
            </motion.div>
          </div>

          {/* Chat Sidebar */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="glass p-6 flex flex-col h-[600px]"
          >
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
              <MessageCircle className="w-5 h-5" />
              Chat
            </h3>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto space-y-3 mb-4">
              {messages.map((msg, index) => (
                <div key={index} className="text-sm">
                  {msg.type === 'chat_message' ? (
                    <div>
                      <span className="font-semibold text-accent-cyan">
                        {msg.display_name}:
                      </span>{' '}
                      <span className="text-text-secondary">{msg.message}</span>
                    </div>
                  ) : (
                    <div className="text-text-muted italic">
                      {msg.display_name} {msg.type === 'user_joined' ? 'joined' : 'left'}
                    </div>
                  )}
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="flex gap-2">
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="Type a message..."
                className="flex-1 px-4 py-2 bg-bg-elevated rounded-lg border border-border focus:border-accent-primary outline-none"
              />
              <button
                onClick={sendMessage}
                className="px-4 py-2 bg-accent-primary rounded-lg hover:scale-105 transition-transform"
              >
                Send
              </button>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}
