import React from 'react'
import { useTheme } from '../contexts/ThemeContext'
import { useInstallation } from '../contexts/InstallationContext'
import { Button } from './Button'
import { motion } from 'framer-motion'

const Header: React.FC = () => {
  const { theme, toggleTheme } = useTheme()
  const { progress, isInstalling } = useInstallation()

  return (
    <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Left Section */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-r from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
                <span className="text-white text-sm">🤖</span>
              </div>
              <div>
                <h2 className="text-sm font-semibold text-gray-900 dark:text-white">Omega Stack Installer</h2>
                <p className="text-xs text-gray-500 dark:text-gray-400">Beautiful & Modular</p>
              </div>
            </div>
          </div>

          {/* Center Section - Progress Indicator */}
          <div className="flex-1 max-w-md mx-8">
            {progress.phase !== 'discovery' && (
              <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-medium text-gray-700 dark:text-gray-300">
                    {progress.phase.charAt(0).toUpperCase() + progress.phase.slice(1)}
                  </span>
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {Math.round(progress.progress)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                  <motion.div
                    className="bg-primary-500 h-2 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${progress.progress}%` }}
                    transition={{ duration: 0.5, ease: 'easeOut' }}
                  />
                </div>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1 truncate">
                  {progress.message}
                </p>
              </div>
            )}
          </div>

          {/* Right Section */}
          <div className="flex items-center space-x-3">
            {/* Theme Toggle */}
            <Button
              variant="ghost"
              size="sm"
              onClick={toggleTheme}
              className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
            >
              {theme === 'light' ? '🌙' : '☀️'}
              <span className="ml-2 text-sm">Theme</span>
            </Button>

            {/* Status Indicator */}
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${
                progress.phase === 'complete' ? 'bg-success-500' :
                isInstalling ? 'bg-warning-500 animate-pulse' :
                'bg-gray-300'
              }`}></div>
              <span className="text-sm text-gray-600 dark:text-gray-300">
                {progress.phase === 'complete' ? 'Complete' : 
                 isInstalling ? 'Installing' : 'Ready'}
              </span>
            </div>

            {/* Quick Actions */}
            {isInstalling && (
              <div className="flex space-x-2">
                <Button variant="secondary" size="sm" onClick={() => {}}>
                  Pause
                </Button>
                <Button variant="danger" size="sm" onClick={() => {}}>
                  Cancel
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header