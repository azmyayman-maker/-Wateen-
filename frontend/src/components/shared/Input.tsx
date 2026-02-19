import { cn } from '@/lib/utils'
import { forwardRef, type InputHTMLAttributes, useId } from 'react'

interface InputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'id'> {
  label: string
  error?: string
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, required, disabled, type = 'text', ...props }, ref) => {
    const id = useId()
    const errorId = `${id}-error`

    return (
      <div className="w-full">
        <label
          htmlFor={id}
          className="block text-sm font-medium text-text-primary mb-1.5"
        >
          {label}
          {required && <span className="text-error me-1" aria-hidden="true">*</span>}
        </label>
        <input
          ref={ref}
          id={id}
          type={type}
          className={cn(
            'w-full h-10 px-3 rounded-md border bg-white text-text-primary',
            'placeholder:text-text-secondary/60',
            'focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary',
            'disabled:opacity-50 disabled:cursor-not-allowed',
            error
              ? 'border-error focus:ring-error focus:border-error'
              : 'border-border',
            className
          )}
          disabled={disabled}
          aria-required={required}
          aria-invalid={!!error}
          aria-describedby={error ? errorId : undefined}
          {...props}
        />
        {error && (
          <p
            id={errorId}
            className="mt-1.5 text-sm text-error"
            role="alert"
          >
            {error}
          </p>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'

export { Input }
