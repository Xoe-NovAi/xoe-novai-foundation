import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react'
import { io, Socket } from 'socket.io-client'
import toast from 'react-hot-toast'

export interface SystemInfo {
  os: string
  cpu: string
  memory: string
  disk: string
  pythonVersion: string
  dockerAvailable: boolean
  podmanAvailable: boolean
  networkStatus: 'online' | 'offline' | 'checking'
}

export interface ServiceConfig {
  id: string
  name: string
  description: string
  required: boolean
  selected: boolean
  dependencies: string[]
  resources: {
    cpu: number
    memory: number
    storage: number
  }
}

export interface ProviderConfig {
  id: string
  name: string
  description: string
  selected: boolean
  credentials: Record<string, string>
  enabled: boolean
}

export interface InstallationConfig {
  preset: 'quick' | 'standard' | 'enterprise' | 'development'
  environment: 'development' | 'staging' | 'production'
  services: ServiceConfig[]
  providers: ProviderConfig[]
  credentials: {
    opencode: string[]
    antigravity: string
    gemini: string
    copilot: string
  }
  performance: {
    cpuCores: number
    memoryLimit: string
    storagePath: string
  }
  security: {
    enableTelemetry: boolean
    enableEncryption: boolean
    accessControl: boolean
  }
}

export interface InstallationProgress {
  phase: 'discovery' | 'installation' | 'configuration' | 'validation' | 'complete'
  currentStep: number
  totalSteps: number
  progress: number
  status: 'running' | 'completed' | 'failed' | 'paused'
  message: string
  components: Array<{
    id: string
    name: string
    status: 'pending' | 'running' | 'completed' | 'failed'
    progress: number
    message: string
  }>
}

interface InstallationContextType {
  systemInfo: SystemInfo | null
  config: InstallationConfig
  progress: InstallationProgress
  socket: Socket | null
  isInstalling: boolean
  isComplete: boolean
  
  // Actions
  setSystemInfo: (info: SystemInfo) => void
  updateConfig: (updates: Partial<InstallationConfig>) => void
  startInstallation: () => Promise<void>
  pauseInstallation: () => void
  resumeInstallation: () => void
  cancelInstallation: () => void
  resetInstallation: () => void
  selectPreset: (preset: InstallationConfig['preset']) => void
  toggleService: (serviceId: string) => void
  toggleProvider: (providerId: string) => void
  updateCredentials: (provider: string, credentials: Record<string, string>) => void
}

const InstallationContext = createContext<InstallationContextType | undefined>(undefined)

export const useInstallation = () => {
  const context = useContext(InstallationContext)
  if (context === undefined) {
    throw new Error('useInstallation must be used within an InstallationProvider')
  }
  return context
}

interface InstallationProviderProps {
  children: ReactNode
}

export const InstallationProvider: React.FC<InstallationProviderProps> = ({ children }) => {
  const [systemInfo, setSystemInfoState] = useState<SystemInfo | null>(null)
  const [config, setConfig] = useState<InstallationConfig>({
    preset: 'standard',
    environment: 'development',
    services: [],
    providers: [],
    credentials: {
      opencode: [],
      antigravity: '',
      gemini: '',
      copilot: '',
    },
    performance: {
      cpuCores: 4,
      memoryLimit: '8GB',
      storagePath: '/tmp',
    },
    security: {
      enableTelemetry: false,
      enableEncryption: true,
      accessControl: true,
    },
  })
  const [progress, setProgress] = useState<InstallationProgress>({
    phase: 'discovery',
    currentStep: 0,
    totalSteps: 0,
    progress: 0,
    status: 'completed',
    message: 'Ready to install',
    components: [],
  })
  const [socket, setSocket] = useState<Socket | null>(null)
  const [isInstalling, setIsInstalling] = useState(false)
  const [isComplete, setIsComplete] = useState(false)

  // Initialize socket connection
  const initializeSocket = useCallback(() => {
    const newSocket = io('http://localhost:8001')
    
    newSocket.on('connect', () => {
      console.log('Connected to installation server')
    })

    newSocket.on('disconnect', () => {
      console.log('Disconnected from installation server')
    })

    newSocket.on('system_info', (data: SystemInfo) => {
      setSystemInfoState(data)
    })

    newSocket.on('installation_progress', (data: InstallationProgress) => {
      setProgress(data)
      setIsInstalling(data.status === 'running')
      setIsComplete(data.phase === 'complete')
    })

    newSocket.on('installation_complete', () => {
      toast.success('Installation completed successfully!')
      setIsInstalling(false)
      setIsComplete(true)
    })

    newSocket.on('installation_error', (error: string) => {
      toast.error(`Installation failed: ${error}`)
      setIsInstalling(false)
    })

    setSocket(newSocket)
    return newSocket
  }, [])

  const setSystemInfo = useCallback((info: SystemInfo) => {
    setSystemInfoState(info)
  }, [])

  const updateConfig = useCallback((updates: Partial<InstallationConfig>) => {
    setConfig(prev => ({ ...prev, ...updates }))
  }, [])

  const selectPreset = useCallback((preset: InstallationConfig['preset']) => {
    setConfig(prev => {
      const newConfig = { ...prev, preset }
      
      // Apply preset-specific configurations
      switch (preset) {
        case 'quick':
          newConfig.services = prev.services.map(s => ({
            ...s,
            selected: s.required || ['rag-engine', 'chainlit-ui', 'redis-cache'].includes(s.id)
          }))
          newConfig.environment = 'development'
          newConfig.performance.memoryLimit = '4GB'
          break
        case 'standard':
          newConfig.services = prev.services.map(s => ({
            ...s,
            selected: s.required || ['rag-engine', 'chainlit-ui', 'redis-cache', 'postgres', 'victoriametrics'].includes(s.id)
          }))
          newConfig.environment = 'development'
          newConfig.performance.memoryLimit = '8GB'
          break
        case 'enterprise':
          newConfig.services = prev.services.map(s => ({ ...s, selected: true }))
          newConfig.environment = 'production'
          newConfig.performance.memoryLimit = '16GB'
          newConfig.security.enableTelemetry = true
          break
        case 'development':
          newConfig.services = prev.services.map(s => ({
            ...s,
            selected: s.required || ['rag-engine', 'chainlit-ui', 'redis-cache', 'postgres', 'victoriametrics', 'library-curator', 'voice-interface'].includes(s.id)
          }))
          newConfig.environment = 'development'
          newConfig.performance.memoryLimit = '8GB'
          break
      }
      
      return newConfig
    })
  }, [])

  const toggleService = useCallback((serviceId: string) => {
    setConfig(prev => ({
      ...prev,
      services: prev.services.map(service => {
        if (service.id === serviceId) {
          return { ...service, selected: !service.selected }
        }
        return service
      })
    }))
  }, [])

  const toggleProvider = useCallback((providerId: string) => {
    setConfig(prev => ({
      ...prev,
      providers: prev.providers.map(provider => {
        if (provider.id === providerId) {
          return { ...provider, selected: !provider.selected }
        }
        return provider
      })
    }))
  }, [])

  const updateCredentials = useCallback((provider: string, credentials: Record<string, string>) => {
    setConfig(prev => ({
      ...prev,
      credentials: {
        ...prev.credentials,
        [provider]: credentials
      }
    }))
  }, [])

  const startInstallation = useCallback(async () => {
    if (!socket) {
      initializeSocket()
    }
    
    try {
      toast.loading('Starting installation...')
      setIsInstalling(true)
      socket?.emit('start_installation', config)
    } catch (error) {
      toast.error('Failed to start installation')
      setIsInstalling(false)
    }
  }, [socket, config, initializeSocket])

  const pauseInstallation = useCallback(() => {
    socket?.emit('pause_installation')
    setIsInstalling(false)
  }, [socket])

  const resumeInstallation = useCallback(() => {
    socket?.emit('resume_installation')
    setIsInstalling(true)
  }, [socket])

  const cancelInstallation = useCallback(() => {
    socket?.emit('cancel_installation')
    setIsInstalling(false)
    setIsComplete(false)
    toast.error('Installation cancelled')
  }, [socket])

  const resetInstallation = useCallback(() => {
    setProgress({
      phase: 'discovery',
      currentStep: 0,
      totalSteps: 0,
      progress: 0,
      status: 'completed',
      message: 'Ready to install',
      components: [],
    })
    setIsInstalling(false)
    setIsComplete(false)
  }, [])

  return (
    <InstallationContext.Provider
      value={{
        systemInfo,
        config,
        progress,
        socket,
        isInstalling,
        isComplete,
        setSystemInfo,
        updateConfig,
        startInstallation,
        pauseInstallation,
        resumeInstallation,
        cancelInstallation,
        resetInstallation,
        selectPreset,
        toggleService,
        toggleProvider,
        updateCredentials,
      }}
    >
      {children}
    </InstallationContext.Provider>
  )
}