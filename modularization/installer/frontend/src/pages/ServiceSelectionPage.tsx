import React, { useState, useEffect } from 'react'
import { useInstallation } from '../contexts/InstallationContext'
import { Card } from '../components/Card'
import { Button } from '../components/Button'
import { Badge } from '../components/Badge'
import { ToggleSwitch } from '../components/ToggleSwitch'
import { Progress } from '../components/Progress'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'

const ServiceSelectionPage: React.FC = () => {
  const { config, updateConfig, selectPreset } = useInstallation()
  const navigate = useNavigate()
  const [selectedPreset, setSelectedPreset] = useState(config.preset)

  // Service definitions based on your existing Omega stack
  const serviceDefinitions = [
    {
      id: 'rag-engine',
      name: 'RAG Engine',
      description: 'Your existing FastAPI + Qwen3-0.6B RAG system',
      required: true,
      category: 'Core',
      icon: '🧠',
      resources: { cpu: 2, memory: 4, storage: 2 },
      dependencies: []
    },
    {
      id: 'chainlit-ui',
      name: 'Chainlit UI',
      description: 'Your existing web interface for AI interactions',
      required: true,
      category: 'Core',
      icon: '🌐',
      resources: { cpu: 1, memory: 2, storage: 1 },
      dependencies: ['rag-engine']
    },
    {
      id: 'redis-cache',
      name: 'Redis Cache',
      description: 'Your existing caching layer for performance',
      required: true,
      category: 'Core',
      icon: '⚡',
      resources: { cpu: 1, memory: 1, storage: 0.5 },
      dependencies: []
    },
    {
      id: 'postgres',
      name: 'PostgreSQL',
      description: 'Database backend for persistent storage',
      required: false,
      category: 'Database',
      icon: '🗄️',
      resources: { cpu: 2, memory: 2, storage: 5 },
      dependencies: []
    },
    {
      id: 'victoriametrics',
      name: 'VictoriaMetrics',
      description: 'Your existing monitoring and metrics collection',
      required: false,
      category: 'Monitoring',
      icon: '📊',
      resources: { cpu: 1, memory: 1, storage: 2 },
      dependencies: []
    },
    {
      id: 'library-curator',
      name: 'Library Curator',
      description: 'Your existing offline library management system',
      required: false,
      category: 'Integration',
      icon: '📚',
      resources: { cpu: 1, memory: 1, storage: 10 },
      dependencies: ['rag-engine']
    },
    {
      id: 'voice-interface',
      name: 'Voice Interface',
      description: 'Your existing voice-to-voice conversation system',
      required: false,
      category: 'Integration',
      icon: '🎤',
      resources: { cpu: 2, memory: 2, storage: 1 },
      dependencies: ['rag-engine']
    },
    {
      id: 'advanced-analytics',
      name: 'Advanced Analytics',
      description: 'Enhanced insights and reporting',
      required: false,
      category: 'Analytics',
      icon: '📈',
      resources: { cpu: 1, memory: 1, storage: 1 },
      dependencies: ['victoriametrics']
    },
    {
      id: 'enterprise-security',
      name: 'Enterprise Security',
      description: 'Additional security layers and encryption',
      required: false,
      category: 'Security',
      icon: '🔒',
      resources: { cpu: 1, memory: 1, storage: 0.5 },
      dependencies: []
    }
  ]

  const providerDefinitions = [
    {
      id: 'opencode',
      name: 'OpenCode Multi-Account',
      description: 'Your existing 8-account rotation system',
      icon: '🤖',
      selected: config.providers.find(p => p.id === 'opencode')?.selected || false
    },
    {
      id: 'antigravity',
      name: 'Antigravity',
      description: 'Free frontier models with Opus 4.6',
      icon: '🚀',
      selected: config.providers.find(p => p.id === 'antigravity')?.selected || false
    },
    {
      id: 'gemini',
      name: 'Gemini',
      description: 'Advanced AI capabilities',
      icon: '💎',
      selected: config.providers.find(p => p.id === 'gemini')?.selected || false
    },
    {
      id: 'copilot',
      name: 'Copilot',
      description: 'Code assistance and development help',
      icon: '👨‍💻',
      selected: config.providers.find(p => p.id === 'copilot')?.selected || false
    },
    {
      id: 'cline',
      name: 'Cline',
      description: 'CLI integration and command execution',
      icon: '🖥️',
      selected: config.providers.find(p => p.id === 'cline')?.selected || false
    }
  ]

  const calculateResources = () => {
    const selectedServices = serviceDefinitions.filter(s => 
      config.services.find(cs => cs.id === s.id)?.selected
    )
    
    const total = selectedServices.reduce((acc, service) => ({
      cpu: acc.cpu + service.resources.cpu,
      memory: acc.memory + service.resources.memory,
      storage: acc.storage + service.resources.storage
    }), { cpu: 0, memory: 0, storage: 0 })

    return total
  }

  const resources = calculateResources()

  const handleServiceToggle = (serviceId: string) => {
    const service = serviceDefinitions.find(s => s.id === serviceId)
    if (service?.required) return // Cannot toggle required services

    updateConfig({
      services: config.services.map(s => 
        s.id === serviceId ? { ...s, selected: !s.selected } : s
      )
    })
  }

  const handleProviderToggle = (providerId: string) => {
    updateConfig({
      providers: config.providers.map(p => 
        p.id === providerId ? { ...p, selected: !p.selected } : p
      )
    })
  }

  const handlePresetChange = (preset: typeof config.preset) => {
    setSelectedPreset(preset)
    selectPreset(preset)
    toast.success(`Applied ${preset} preset`)
  }

  const handleNext = () => {
    // Validate selection
    const selectedServices = config.services.filter(s => s.selected)
    if (selectedServices.length === 0) {
      toast.error('Please select at least one service')
      return
    }

    navigate('/configuration')
  }

  // Initialize services if not already set
  useEffect(() => {
    if (config.services.length === 0) {
      updateConfig({
        services: serviceDefinitions.map(service => ({
          ...service,
          selected: service.required
        }))
      })
    }
    if (config.providers.length === 0) {
      updateConfig({
        providers: providerDefinitions.map(provider => ({
          ...provider,
          selected: false
        }))
      })
    }
  }, [config.services.length, config.providers.length, updateConfig])

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Service Selection
        </h1>
        <p className="text-gray-600 dark:text-gray-300">
          Choose the services and AI providers you want to install
        </p>
      </div>

      {/* Preset Selection */}
      <Card className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Installation Presets</h2>
          <div className="text-sm text-gray-500">
            Selected: <span className="font-medium capitalize">{selectedPreset}</span>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[
            { id: 'quick', name: 'Quick Start', desc: '5 minutes • Core services only', color: 'blue' },
            { id: 'standard', name: 'Standard', desc: '10 minutes • Recommended setup', color: 'green' },
            { id: 'enterprise', name: 'Enterprise', desc: '15 minutes • All features', color: 'purple' },
            { id: 'development', name: 'Development', desc: '12 minutes • With debug tools', color: 'orange' }
          ].map(preset => (
            <button
              key={preset.id}
              onClick={() => handlePresetChange(preset.id as any)}
              className={`p-4 rounded-lg border-2 transition-all ${
                selectedPreset === preset.id 
                  ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20' 
                  : 'border-gray-200 hover:border-gray-300 dark:border-gray-700 dark:hover:border-gray-600'
              }`}
            >
              <div className="text-left">
                <div className="font-semibold text-gray-900 dark:text-white">
                  {preset.name}
                </div>
                <div className="text-sm text-gray-500 mt-1">
                  {preset.desc}
                </div>
              </div>
            </button>
          ))}
        </div>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Services Selection */}
        <div className="lg:col-span-2">
          <Card>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold">Core Services</h2>
              <div className="text-sm text-gray-500">
                {config.services.filter(s => s.selected).length} of {config.services.length} selected
              </div>
            </div>

            <div className="space-y-4">
              {serviceDefinitions.map(service => {
                const serviceConfig = config.services.find(s => s.id === service.id) || service
                const isDisabled = service.required && serviceConfig.selected
                const canToggle = !service.required

                return (
                  <div
                    key={service.id}
                    className={`service-card ${
                      serviceConfig.selected ? 'selected' : ''
                    } ${isDisabled ? 'disabled' : ''}`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <span className="text-2xl">{service.icon}</span>
                        <div>
                          <div className="font-medium text-gray-900 dark:text-white">
                            {service.name}
                            {service.required && (
                              <Badge variant="primary" className="ml-2">Required</Badge>
                            )}
                          </div>
                          <div className="text-sm text-gray-500">
                            {service.description}
                          </div>
                          <div className="text-xs text-gray-400 mt-1">
                            {service.category} • CPU: {service.resources.cpu} • RAM: {service.resources.memory}GB
                          </div>
                        </div>
                      </div>
                      <ToggleSwitch
                        checked={serviceConfig.selected}
                        onChange={() => canToggle && handleServiceToggle(service.id)}
                        disabled={isDisabled}
                        label={serviceConfig.selected ? 'Enabled' : 'Disabled'}
                      />
                    </div>
                  </div>
                )
              })}
            </div>
          </Card>
        </div>

        {/* AI Providers */}
        <div className="lg:col-span-1">
          <Card>
            <h2 className="text-xl font-semibold mb-6">AI Providers</h2>
            
            <div className="space-y-4">
              {providerDefinitions.map(provider => {
                const providerConfig = config.providers.find(p => p.id === provider.id) || provider
                
                return (
                  <div
                    key={provider.id}
                    className={`service-card ${
                      providerConfig.selected ? 'selected' : ''
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <span className="text-2xl">{provider.icon}</span>
                        <div>
                          <div className="font-medium text-gray-900 dark:text-white">
                            {provider.name}
                          </div>
                          <div className="text-sm text-gray-500">
                            {provider.description}
                          </div>
                        </div>
                      </div>
                      <ToggleSwitch
                        checked={providerConfig.selected}
                        onChange={() => handleProviderToggle(provider.id)}
                        label={providerConfig.selected ? 'Enabled' : 'Disabled'}
                      />
                    </div>
                  </div>
                )
              })}
            </div>
          </Card>

          {/* Resource Summary */}
          <Card className="mt-6">
            <h3 className="text-lg font-semibold mb-4">Resource Requirements</h3>
            
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Total CPU Cores:</span>
                <span className="font-semibold">{resources.cpu}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Total Memory:</span>
                <span className="font-semibold">{resources.memory} GB</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Storage Required:</span>
                <span className="font-semibold">{resources.storage} GB</span>
              </div>
            </div>

            <div className="mt-4">
              <Progress 
                value={Math.min(100, (resources.cpu / 8) * 100)} 
                label="CPU Usage"
              />
              <Progress 
                value={Math.min(100, (resources.memory / 16) * 100)} 
                label="Memory Usage"
                className="mt-2"
              />
            </div>
          </Card>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex justify-between mt-8">
        <Button variant="secondary" onClick={() => navigate('/system-check')}>
          ← Back
        </Button>
        <Button onClick={handleNext}>
          Next →
        </Button>
      </div>
    </div>
  )
}

export default ServiceSelectionPage