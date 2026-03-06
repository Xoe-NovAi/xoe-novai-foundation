import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { Badge } from '../components/Badge'
import { useTheme } from '../contexts/ThemeContext'
import { useInstallation } from '../contexts/InstallationContext'
import toast from 'react-hot-toast'

const WelcomePage: React.FC = () => {
  const { theme } = useTheme()
  const { config, updateConfig } = useInstallation()
  const navigate = useNavigate()
  const [isAnimating, setIsAnimating] = useState(false)

  const handleStart = () => {
    setIsAnimating(true)
    toast.success('Starting beautiful installation experience!')
    setTimeout(() => {
      navigate('/system-check')
    }, 500)
  }

  const handleThemeToggle = () => {
    // Theme toggle handled by context
  }

  const presets = [
    {
      id: 'quick',
      name: 'Quick Start',
      duration: '5 minutes',
      description: 'Perfect for getting started quickly with core services only',
      features: ['RAG Engine', 'Chainlit UI', 'Redis Cache'],
      icon: '🚀',
      color: 'from-blue-500 to-cyan-500'
    },
    {
      id: 'standard',
      name: 'Standard Stack',
      duration: '10 minutes',
      description: 'Recommended setup with multiple AI providers and monitoring',
      features: ['All Core Services', 'Multiple AI Providers', 'Enhanced Monitoring'],
      icon: '⭐',
      color: 'from-green-500 to-emerald-500'
    },
    {
      id: 'enterprise',
      name: 'Enterprise Stack',
      duration: '15 minutes',
      description: 'Production-ready with all features and advanced security',
      features: ['Complete Feature Set', 'Advanced Security', 'High Availability'],
      icon: '🏢',
      color: 'from-purple-500 to-pink-500'
    },
    {
      id: 'development',
      name: 'Development Stack',
      duration: '12 minutes',
      description: 'With debug tools and source code for contributors',
      features: ['Debug Tools', 'Source Code', 'Hot Reloading'],
      icon: '💻',
      color: 'from-orange-500 to-red-500'
    }
  ]

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8"
      >
        {/* Header */}
        <Card className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
              className="w-16 h-16 bg-gradient-to-r from-primary-500 to-primary-600 rounded-full flex items-center justify-center text-white text-2xl shadow-lg"
            >
              🤖
            </motion.div>
          </div>
          
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            Xoe-NovAi Omega Stack
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 mb-6">
            Beautiful Modular Installation System
          </p>
          
          <div className="flex flex-wrap justify-center gap-2 mb-6">
            <Badge variant="primary">v1.0.0</Badge>
            <Badge variant="success">Modular</Badge>
            <Badge variant="secondary">Beautiful</Badge>
            <Badge variant="warning">Accessible</Badge>
          </div>

          <p className="text-gray-600 dark:text-gray-300 mb-8 max-w-2xl mx-auto">
            Transform your sophisticated Omega stack into an accessible, user-friendly 
            installation experience with stunning UI/UX and complete customization options.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" onClick={handleStart} className="text-lg px-8 py-3">
              {isAnimating ? 'Starting...' : 'Start Installation'}
            </Button>
            <Button variant="secondary" size="lg" onClick={() => navigate('/system-check')}>
              System Check First
            </Button>
          </div>
        </Card>

        {/* Preset Selection */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {presets.map((preset, index) => (
            <motion.div
              key={preset.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
            >
              <Card 
                className={`cursor-pointer hover:shadow-lg transition-all duration-300 ${
                  config.preset === preset.id ? 'ring-2 ring-primary-500' : ''
                }`}
                onClick={() => updateConfig({ preset: preset.id as any })}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-2xl">{preset.icon}</span>
                      <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                        {preset.name}
                      </h3>
                      <Badge variant="primary" className="ml-auto">
                        {preset.duration}
                      </Badge>
                    </div>
                    <p className="text-gray-600 dark:text-gray-300 mb-4">
                      {preset.description}
                    </p>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {preset.features.map((feature, idx) => (
                        <div key={idx} className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                          <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
                          {feature}
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className={`w-2 bg-gradient-to-b ${preset.color} rounded-full`}></div>
                </div>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Features Grid */}
        <Card>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6 text-center">
            Why Choose Our Beautiful Installer?
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">🎨</span>
              </div>
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Stunning UI/UX</h3>
              <p className="text-gray-600 dark:text-gray-300 text-sm">
                Beautiful, modern interface with smooth animations and intuitive navigation
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">⚡</span>
              </div>
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Fast Installation</h3>
              <p className="text-gray-600 dark:text-gray-300 text-sm">
                Optimized installation process with real-time progress tracking
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">🔧</span>
              </div>
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Complete Customization</h3>
              <p className="text-gray-600 dark:text-gray-300 text-sm">
                Choose exactly what you want to install with granular configuration options
              </p>
            </div>
          </div>
        </Card>

        {/* Footer */}
        <div className="text-center mt-8 text-gray-500 dark:text-gray-400 text-sm">
          <p>
            Built with React, TypeScript, Tailwind CSS, and FastAPI • 
            Supports Linux and macOS • 
            Python 3.12+ required
          </p>
        </div>
      </motion.div>
    </div>
  )
}

export default WelcomePage