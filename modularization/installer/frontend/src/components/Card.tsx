import React from 'react'
import { motion } from 'framer-motion'

interface CardProps {
  children: React.ReactNode
  className?: string
  variant?: 'default' | 'elevated' | 'outlined'
  hoverable?: boolean
  onClick?: () => void
}

const Card: React.FC<CardProps> = ({ 
  children, 
  className = '', 
  variant = 'default',
  hoverable = false,
  onClick 
}) => {
  const baseClasses = 'card p-6'
  const variantClasses = {
    default: 'bg-white dark:bg-gray-800',
    elevated: 'bg-white dark:bg-gray-800 shadow-medium',
    outlined: 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700'
  }
  
  const hoverClasses = hoverable 
    ? 'hover:shadow-medium hover:-translate-y-0.5 transition-all duration-200 cursor-pointer' 
    : ''

  const classes = `${baseClasses} ${variantClasses[variant]} ${hoverClasses} ${className}`

  if (onClick) {
    return (
      <motion.div
        className={classes}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={onClick}
      >
        {children}
      </motion.div>
    )
  }

  return <div className={classes}>{children}</div>
}

export default Card