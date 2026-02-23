'use client';

import dynamic from 'next/dynamic';
import { useEffect, useState } from "react"

const MeshGradient = dynamic(() => import('@paper-design/shaders-react').then((mod) => mod.MeshGradient), { ssr: false });
import { cn } from "@/lib/utils"
import FlipTextReveal from "@/components/ui/next-reveal"
import { useLanguage } from "@/lib/i18n"
import { SlideButton } from "@/components/ui/slide-button"

interface HeroSectionProps {
  title?: string
  highlightText?: string
  description?: string
  buttonText?: string
  onButtonClick?: () => void
  colors?: string[]
  distortion?: number
  swirl?: number
  speed?: number
  offsetX?: number
  className?: string
  titleClassName?: string
  descriptionClassName?: string
  buttonClassName?: string
  maxWidth?: string
  veilOpacity?: string
  fontFamily?: string
  fontWeight?: number
}

export function HeroSection({
  title = "Intelligent AI Agents for",
  highlightText = "Smart Brands",
  description = "Transform your brand and evolve it through AI-driven brand guidelines and always up-to-date core components.",
  buttonText = "Join Waitlist",
  onButtonClick,
  colors = ["#72b9bb", "#b5d9d9", "#ffd1bd", "#ffebe0", "#8cc5b8", "#dbf4a4"],
  distortion = 0.8,
  swirl = 0.6,
  speed = 0.42,
  offsetX = 0.08,
  className = "",
  titleClassName = "",
  descriptionClassName = "",
  buttonClassName = "",
  maxWidth = "max-w-6xl",
  veilOpacity = "bg-black/30",
  fontFamily = "inherit",
  fontWeight = 700,
}: HeroSectionProps) {
  const { dir } = useLanguage();
  const [dimensions, setDimensions] = useState({ width: 1920, height: 600 })
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    const update = () =>
      setDimensions({
        width: window.innerWidth,
        height: Math.min(window.innerHeight * 0.65, 700),
      })
    update()
    window.addEventListener("resize", update)
    return () => window.removeEventListener("resize", update)
  }, [])

  return (
    <section className={cn(`relative w-full overflow-hidden flex flex-col items-center justify-center -mt-24 ${className}`)} style={{ height: dimensions.height || 600 }}>
      {/* Background Shader */}
      <div className="absolute inset-0 w-full h-full pointer-events-none">
        {mounted && (
          <>
            <MeshGradient
              width={dimensions.width}
              height={dimensions.height}
              colors={colors}
              distortion={distortion}
              swirl={swirl}
              grainMixer={0}
              grainOverlay={0}
              speed={speed}
              offsetX={offsetX}
            />
            <div className={`absolute inset-0 pointer-events-none ${veilOpacity}`} />
          </>
        )}
        {/* Loading fallback gradient */}
        {!mounted && (
          <div
            className="absolute inset-0"
            style={{ background: `linear-gradient(135deg, ${colors[0]}66 0%, ${colors[1]}44 50%, ${colors[2]}33 100%)` }}
          />
        )}

        {/* ✨ Smooth bottom fade — eliminates hard edge between hero and content */}
        <div
          className="absolute bottom-0 left-0 right-0 pointer-events-none z-10"
          style={{
            height: '35%',
            background: 'linear-gradient(to bottom, transparent 0%, rgba(2,6,23,0.6) 50%, rgba(2,6,23,0.95) 80%, rgb(2,6,23) 100%)',
          }}
        />
        {/* Side vignettes for depth */}
        <div className="absolute inset-0 pointer-events-none z-10"
          style={{ background: 'radial-gradient(ellipse at center, transparent 40%, rgba(2,6,23,0.4) 100%)' }}
        />
      </div>

      {/* Content */}
      <div className={`relative z-20 ${maxWidth} mx-auto px-6 w-full text-center`}>

        <div
          className={`font-black text-white text-balance text-4xl sm:text-5xl md:text-6xl xl:text-[72px] leading-tight mb-4 drop-shadow-lg flex justify-center w-full ${titleClassName}`}
          style={{ fontFamily, fontWeight }}
        >
          <FlipTextReveal title={title} highlightText={highlightText} />
        </div>
        {description && (
          <p
            className={`text-lg sm:text-xl text-white/80 text-pretty max-w-xl mx-auto leading-relaxed mb-8 px-4 drop-shadow-sm ${descriptionClassName}`}
          >
            {description}
          </p>
        )}
        {buttonText && (
          <div className="flex justify-center mt-8 w-full">
            <SlideButton
              text={buttonText}
              onSlideComplete={onButtonClick}
              direction={dir === 'rtl' ? 'rtl' : 'ltr'}
              className={buttonClassName}
            />
          </div>
        )}
      </div>
    </section>
  )
}
