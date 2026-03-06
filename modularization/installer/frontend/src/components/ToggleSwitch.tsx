import React from 'react'
import { motion } from 'framer-motion'

interface ToggleSwitchProps {
  checked: boolean
  onChange: (checked: boolean) => void
  label?: string
  disabled?: boolean
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

const ToggleSwitch: React.FC<ToggleSwitchProps> = ({
  checked,
  onChange,
  label,
  disabled = false,
  size = 'md',
  className = ''
}) => {
  const sizeClasses = {
    sm: 'w-8 h-4',
    md: 'w-10 h-5',
    lg: 'w-12 h-6'
  }

  const handleToggle = () => {
    if (!disabled) {
      onChange(!checked)
    }
  }

  return (
    <div className={`flex items-center space-x-3 ${className}`}>
      <button
        type="button"
        className={`
          relative inline-flex items-center rounded-full transition-colors duration-200 ease-in-out
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
          ${sizeClasses[size]}
          ${checked ? 'bg-primary-600' : 'bg-gray-200 dark:bg-gray-700'}
        `}
        onClick={handleToggle}
        disabled={disabled}
        role="switch"
        aria-checked={checked}
      >
        <motion.span
          className={`
            inline-block rounded-full bg-white shadow-lg transform transition-transform duration-200 ease-in-out
            ${size === 'sm' ? 'w-3 h-3 translate-x-0.5' : ''}
            ${size === 'md' ? 'w-4 h-4 translate-x-0.5' : ''}
            ${size === 'lg' ? 'w-5 h-5 translate-x-0.5' : ''}
            ${checked ? (size === 'sm' ? 'translate-x-4' : size === 'md' ? 'translate-x-5' : 'translate-x-6') : ''}
          `}
          animate={{
            x: checked ? (size === 'sm' ? 16 : size === 'md' ? 20 : 24) : 2
          }}
        />
      </button>
      
      {label && (
        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
          {label}
        </span>
      )}
    </div>
  )
}

export default ToggleSwitch