"use client"

import React, {
  forwardRef,
  useCallback,
  useMemo,
  useRef,
  useState,
  type JSX,
} from "react"
import {
  AnimatePresence,
  motion,
  useMotionValue,
  useSpring,
  useTransform,
  type PanInfo,
} from "framer-motion"
import { Check, Loader2, SendHorizontal, X } from "lucide-react"

import { cn } from "@/lib/utils"
import { Button, ButtonProps } from "@/components/ui/button"

const DRAG_CONSTRAINTS = { left: 0, right: 155 }
const DRAG_THRESHOLD = 0.9

const BUTTON_STATES = {
  initial: { width: "16rem" }, // Widened for Arabic text
  completed: { width: "8rem" },
}

const ANIMATION_CONFIG = {
  spring: {
    type: "spring",
    stiffness: 400,
    damping: 40,
    mass: 0.8,
  },
}

type StatusIconProps = {
  status: "idle" | "loading" | "success" | "error"
}

const StatusIcon: React.FC<StatusIconProps> = ({ status }) => {
  const iconMap: Record<string, JSX.Element> = useMemo(
    () => ({
      loading: <Loader2 className="animate-spin text-white" size={20} />,
      success: <Check className="text-white" size={20} />,
      error: <X className="text-white" size={20} />,
    }),
    []
  )

  if (!iconMap[status]) return null

  return (
    <motion.div
      key={status}
      initial={{ opacity: 0, scale: 0.5 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0 }}
    >
      {iconMap[status]}
    </motion.div>
  )
}

const useButtonStatus = (resolveTo: "success" | "error", onComplete?: () => void) => {
  const [status, setStatus] = useState<
    "idle" | "loading" | "success" | "error"
  >("idle")

  const handleSubmit = useCallback(() => {
    setStatus("loading")
    setTimeout(() => {
      setStatus(resolveTo)
      if (onComplete) onComplete()
    }, 2000)
  }, [resolveTo, onComplete])

  return { status, handleSubmit }
}

interface SlideButtonProps extends Omit<ButtonProps, 'onClick'> {
  text?: string;
  onSlideComplete?: () => void;
  direction?: 'ltr' | 'rtl';
}

export const SlideButton = forwardRef<HTMLButtonElement, SlideButtonProps>(
  ({ className, text = "Slide to submit", onSlideComplete, direction = 'ltr', ...props }, ref) => {
    const [isDragging, setIsDragging] = useState(false)
    const [completed, setCompleted] = useState(false)
    const dragHandleRef = useRef<HTMLDivElement | null>(null)
    const { status, handleSubmit } = useButtonStatus("success", onSlideComplete)

    const isRtl = direction === 'rtl';
    const constraints = isRtl ? { left: -155, right: 0 } : { left: 0, right: 155 };

    const dragX = useMotionValue(0)
    const springX = useSpring(dragX, ANIMATION_CONFIG.spring)
    
    // Calculate progress based on direction
    const dragProgress = useTransform(
      springX,
      [0, isRtl ? constraints.left : constraints.right],
      [0, 1]
    )

    const handleDragStart = useCallback(() => {
      if (completed) return
      setIsDragging(true)
    }, [completed])

    const handleDragEnd = () => {
      if (completed) return
      setIsDragging(false)

      const progress = dragProgress.get()
      if (progress >= DRAG_THRESHOLD) {
        setCompleted(true)
        handleSubmit()
        // Force the pill to the end visually
        dragX.set(isRtl ? constraints.left : constraints.right)
      } else {
        dragX.set(0)
      }
    }

    const handleDrag = (
      _event: MouseEvent | TouchEvent | PointerEvent,
      info: PanInfo
    ) => {
      if (completed) return
      let newX = info.offset.x;
      if (isRtl) {
        newX = Math.min(0, Math.max(newX, constraints.left));
      } else {
        newX = Math.max(0, Math.min(newX, constraints.right));
      }
      dragX.set(newX)
    }

    // Dynamic width of the inner glowing bar
    const adjustedWidth = useTransform(springX, (x) => isRtl ? Math.abs(x) + 40 : x + 40)

    return (
      <motion.div
        animate={completed ? BUTTON_STATES.completed : BUTTON_STATES.initial}
        transition={ANIMATION_CONFIG.spring}
        className={cn(
          "relative flex h-[52px] items-center rounded-full bg-slate-900/50 border border-white/10 backdrop-blur-md shadow-2xl overflow-hidden cursor-pointer",
          isRtl ? "justify-end" : "justify-start"
        )}
      >
        {/* The Text Label shown before completion */}
        {!completed && (
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-0">
             <span className={cn(
               "font-bold text-sm tracking-wide text-white/50 transition-opacity duration-300",
               isDragging ? "opacity-0" : "opacity-100"
             )}>
                {text}
             </span>
          </div>
        )}

        {/* The active trail behind the slider */}
        {!completed && (
          <motion.div
            style={{
              width: adjustedWidth,
              // Anchor right if RTL, else anchor left
              right: isRtl ? 0 : 'auto',
              left: isRtl ? 'auto' : 0,
            }}
            className="absolute inset-y-0 z-0 rounded-full bg-gradient-to-r from-[#16615F] to-[#79B253] opacity-80"
          />
        )}
        
        <AnimatePresence mode="wait">
          {!completed && (
            <motion.div
              ref={dragHandleRef}
              drag="x"
              dragConstraints={constraints}
              dragElastic={0.05}
              dragMomentum={false}
              onDragStart={handleDragStart}
              onDragEnd={handleDragEnd}
              onDrag={handleDrag}
              style={{ x: springX }}
              className={cn(
                "absolute z-10 flex cursor-grab active:cursor-grabbing pb-0 m-1",
                   // Fix position for RTL vs LTR to overlap constraints precisely
                isRtl ? "right-0" : "left-0"
              )}
            >
              <Button
                ref={ref}
                disabled={status === "loading"}
                {...props}
                size="icon"
                className={cn(
                  "size-[44px] shadow-button rounded-full drop-shadow-xl bg-white text-slate-900 hover:bg-slate-200 border-none transition-transform",
                  isDragging && "scale-105"
                )}
              >
                <motion.div animate={{ rotate: isRtl ? 180 : 0 }}>
                  <SendHorizontal className="size-5 text-[#16615F]" />
                </motion.div>
              </Button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Completed State (Loading -> Success/Error) */}
        <AnimatePresence mode="wait">
          {completed && (
            <motion.div
              className="absolute inset-0 flex items-center justify-center bg-[#79B253]"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <Button
                ref={ref}
                disabled={status === "loading"}
                {...props}
                className="size-full rounded-full transition-all duration-300 bg-transparent hover:bg-transparent border-none"
              >
                <AnimatePresence mode="wait">
                  <StatusIcon status={status} />
                </AnimatePresence>
              </Button>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    )
  }
)

SlideButton.displayName = "SlideButton"
