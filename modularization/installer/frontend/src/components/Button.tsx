import React from 'react'
import { motion } from 'framer-motion'

interface ButtonProps {
  children: React.ReactNode
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  fullWidth?: boolean
  disabled?: boolean
  loading?: boolean
  onClick?: () => void
  type?: 'button' | 'submit' | 'reset'
  className?: string
  icon?: React.ReactNode
  iconPosition?: 'left' | 'right'
}

const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  disabled = false,
  loading = false,
  onClick,
  type = 'button',
  className = '',
  icon,
  iconPosition = 'left'
}) => {
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg'
  }

  const baseClasses = `
    btn-${variant} 
    ${sizeClasses[size]}
    ${fullWidth ? 'w-full' : ''}
    ${disabled || loading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
    transition-all duration-200
    inline-flex items-center justify-center gap-2
  `

  const handleClick = () => {
    if (!disabled && !loading && onClick) {
      onClick()
    }
  }

  const content = (
    <>
      {icon && iconPosition === 'left' && icon}
      {loading && (
        <motion.div
          className="w-4 h-4 border-2 border-white border-t-transparent rounded-full"
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
        />
      )}
      {children}
      {icon && iconPosition === 'right' && icon}
    </>
  )

  if (disabled || loading) {
    return (
      <button
        type={type}
        className={`${baseClasses} ${className}`}
        disabled
      >
        {content}
      </button>
    )
  }

  return (
    <motion.button
      type={type}
      className={`${baseClasses} ${className}`}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={handleClick}
    >
      {content}
    </motion.button>
  )
}

export default Button