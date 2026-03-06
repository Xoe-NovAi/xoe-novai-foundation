import React from 'react'
import { useInstallation } from '../contexts/InstallationContext'
import { motion } from 'framer-motion'
import { useNavigate, useLocation } from 'react-router-dom'

const steps = [
  { id: 'welcome', label: 'Welcome', icon: '👋' },
  { id: 'system-check', label: 'System Check', icon: '🔍' },
  { id: 'services', label: 'Service Selection', icon: '⚙️' },
  { id: 'configuration', label: 'Configuration', icon: '🔧' },
  { id: 'installation', label: 'Installation', icon: '🚀' },
  { id: 'complete', label: 'Complete', icon: '✅' }
]

const Sidebar: React.FC = () => {
  const { progress, isInstalling } = useInstallation()
  const navigate = useNavigate()
  const location = useLocation()

  const getCurrentStepIndex = () => {
    const currentPath = location.pathname
    const stepIndex = steps.findIndex(step => currentPath.includes(step.id))
    return Math.max(0, stepIndex)
  }

  const currentStepIndex = getCurrentStepIndex()
  const completedSteps = Math.min(currentStepIndex, progress.currentStep)

  return (
    <div className="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 h-screen sticky top-0">
      <div className="p-6">
        <div className="flex items-center gap-3 mb-8">
          <div className="w-10 h-10 bg-gradient-to-r from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
            <span className="text-white text-lg">🤖</span>
          </div>
          <div>
            <h1 className="text-lg font-semibold text-gray-900 dark:text-white">Omega Installer</h1>
            <p className="text-xs text-gray-500 dark:text-gray-400">v1.0.0</p>
          </div>
        </div>

        <nav className="space-y-2">
          {steps.map((step, index) => {
            const isCompleted = index < completedSteps
            const isCurrent = index === currentStepIndex
            const isFuture = index > currentStepIndex
            const isInstallingStep = step.id === 'installation'

            return (
              <motion.button
                key={step.id}
                className={`
                  w-full text-left p-3 rounded-lg transition-all duration-200 flex items-center gap-3
                  ${isCurrent 
                    ? 'bg-primary-50 dark:bg-primary-900/20 border border-primary-200 dark:border-primary-800' 
                    : 'hover:bg-gray-50 dark:hover:bg-gray-700'
                  }
                  ${isFuture && !isInstalling ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
                `}
                onClick={() => !isFuture && navigate(`/${step.id}`)}
                disabled={isFuture && !isInstalling}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className={`
                  w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium
                  ${isCompleted 
                    ? 'bg-success-100 dark:bg-success-900 text-success-700 dark:text-success-300' 
                    : isCurrent
                    ? 'bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400'
                  }
                `}>
                  {isCompleted ? '✓' : step.icon}
                </div>
                
                <div className="flex-1">
                  <div className={`font-medium text-sm ${
                    isCurrent ? 'text-primary-700 dark:text-primary-300' : 'text-gray-700 dark:text-gray-300'
                  }`}>
                    {step.label}
                  </div>
                  {isInstallingStep && isInstalling && (
                    <div className="text-xs text-primary-600 dark:text-primary-400 mt-1">
                      {progress.message}
                    </div>
                  )}
                </div>

                {isInstallingStep && isInstalling && (
                  <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse-slow"></div>
                )}
              </motion.button>
            )
          })}
        </nav>

        {/* Progress Summary */}
        {progress.phase !== 'discovery' && (
          <div className="mt-8 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Installation Progress</span>
              <span className="text-xs text-gray-500 dark:text-gray-400">{Math.round(progress.progress)}%</span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
              <motion.div
                className="bg-primary-500 h-2 rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${progress.progress}%` }}
                transition={{ duration: 0.5, ease: 'easeOut' }}
              />
            </div>
            <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
              {progress.message}
            </div>
          </div>
        )}

        {/* System Status */}
        <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
          <div className="text-xs text-gray-500 dark:text-gray-400 mb-2">System Status</div>
          <div className="flex items-center gap-2 text-sm">
            <div className={`w-2 h-2 rounded-full ${
              progress.phase === 'complete' ? 'bg-success-500' : 
              isInstalling ? 'bg-warning-500 animate-pulse' : 'bg-gray-300'
            }`}></div>
            <span className="text-gray-700 dark:text-gray-300">
              {progress.phase === 'complete' ? 'Ready' : 
               isInstalling ? 'Installing...' : 'Ready to start'}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Sidebar