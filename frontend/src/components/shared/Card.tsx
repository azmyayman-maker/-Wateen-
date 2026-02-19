import { cn } from '@/lib/utils'
import { type HTMLAttributes, type ReactNode } from 'react'

<<<<<<< HEAD
interface CardProps extends HTMLAttributes<HTMLDivElement> {
=======
interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
>>>>>>> 7a4881e265e7672516941722399a3cb4be1cb240
  variant?: 'elevated' | 'outlined'
  padding?: 'sm' | 'md' | 'lg'
  children: ReactNode
}

export function Card({
  variant = 'elevated',
  padding = 'md',
  children,
  className,
  ...props
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
      {...props}
    >
      {children}
    </div>
  )
}
