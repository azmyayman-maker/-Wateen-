import { cn } from '@/lib/utils'
import { type ReactNode } from 'react'

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'elevated' | 'outlined'
  padding?: 'sm' | 'md' | 'lg'
  children: ReactNode
  className?: string
}

export function Card({
  variant = 'elevated',
  padding = 'md',
  children,
  className,
}: CardProps) {
  const variants = {
    elevated: 'bg-white shadow-md',
    outlined: 'bg-white border border-border',
  }

  const paddings = {
    sm: 'p-3',
    md: 'p-4',
    lg: 'p-6',
  }

  return (
    <div
      className={cn(
        'rounded-lg',
        variants[variant],
        paddings[padding],
        className
      )}
    >
      {children}
    </div>
  )
}
