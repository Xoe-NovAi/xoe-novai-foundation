import React from 'react'
import { motion } from 'framer-motion'

interface ProgressProps {
  value: number
  max?: number
  label?: string
  showPercentage?: boolean
  size?: 'sm' | 'md' | 'lg'
  variant?: 'primary' | 'success' | 'warning' | 'error'
  className?: string
}

const Progress: React.FC<ProgressProps> = ({
  value,
  max = 100,
  label,
  showPercentage = true,
  size = 'md',
  variant = 'primary',
  className = ''
}) => {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100))
  
  const sizeClasses = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3'
  }

  const variantClasses = {
    primary: 'bg-primary-500',
    success: 'bg-success-500',
    warning: 'bg-warning-500',
    error: 'bg-error-500'
  }

  return (
    <div className={`space-y-2 ${className}`}>
      {label && (
        <div className="flex justify-between items-center">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            {label}
          </span>
          {showPercentage && (
            <span className="text-sm text-gray-500 dark:text-gray-400">
              {Math.round(percentage)}%
            </span>
          )}
        </div>
      )}
      
      <div className={`w-full bg-gray-200 dark:bg-gray-700 rounded-full ${sizeClasses[size]}`}>
        <motion.div
          className={`progress-fill ${variantClasses[variant]} rounded-full`}
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}

export default Progress