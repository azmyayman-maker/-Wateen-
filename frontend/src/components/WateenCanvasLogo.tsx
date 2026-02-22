import React, { useEffect, useRef, useState } from 'react';

// Easing function: cubic ease out
const easeOutCubic = (x: number): number => {
  return 1 - Math.pow(1 - x, 3);
};

interface WateenCanvasLogoProps {
  className?: string;
  width?: number;
  height?: number;
}

export const WateenCanvasLogo: React.FC<WateenCanvasLogoProps> = ({
  className = "",
  width = 340,
  height = 160
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [animationComplete, setAnimationComplete] = useState<boolean>(false);
  const animationCompleteRef = useRef(false);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    ctx.scale(dpr, dpr);

    const img = new Image();
    img.src = '/images/icon.svg';

    let animationFrameId: number;
    let startTime: number | null = null;
    const animationDuration = 2500;

    img.onload = () => {
      const render = (timestamp: number) => {
        if (!startTime) startTime = timestamp;
        const elapsed = timestamp - startTime;
        let progress = Math.min(elapsed / animationDuration, 1);
        const easedProgress = easeOutCubic(progress);

        ctx.clearRect(0, 0, width, height);

        const imgSize = 130; // Desired logo display dimension
        const centerX = width / 2;
        const centerY = height / 2;
        
        if (progress < 1) {
            // Entrance Animation: Fade, Scale, and Glow
            ctx.globalAlpha = easedProgress;
            ctx.shadowBlur = 25 * easedProgress;
            ctx.shadowColor = 'rgba(0, 136, 255, 0.4)';
            
            const scale = 0.85 + (0.15 * easedProgress);
            const currentSize = imgSize * scale;
            
            ctx.drawImage(
                img, 
                centerX - (currentSize / 2), 
                centerY - (currentSize / 2), 
                currentSize, 
                currentSize
            );
            
            animationFrameId = requestAnimationFrame(render);
        } else {
            // Continuous Float Animation
            if (!animationCompleteRef.current) {
                animationCompleteRef.current = true;
                setAnimationComplete(true);
            }
            
            const floatTime = timestamp - (startTime + animationDuration);
            // 4px vertical breathing
            const floatY = Math.sin(floatTime / 1200) * 4; 
            
            ctx.globalAlpha = 1;
            ctx.shadowBlur = 15;
            ctx.shadowColor = 'rgba(138, 43, 226, 0.25)';
            
            ctx.drawImage(
                img, 
                centerX - (imgSize / 2), 
                (centerY - (imgSize / 2)) + floatY, 
                imgSize, 
                imgSize
            );
            
            animationFrameId = requestAnimationFrame(render);
        }
      };
      
      animationFrameId = requestAnimationFrame(render);
    };

    return () => {
      if (animationFrameId) cancelAnimationFrame(animationFrameId);
    };
  }, [width, height]);

  return (
    <div className={`relative flex flex-col items-center justify-center ${className}`} dir="rtl">
      <canvas 
        ref={canvasRef} 
        className="block"
        aria-label="Wateen Premium Logo"
        role="img"
      />

      <div 
        className={`mt-4 text-center select-none transition-all duration-[1500ms] ease-[cubic-bezier(0.16,1,0.3,1)] flex flex-col items-center
          ${animationComplete ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"}`}
      >
        <h1 className="text-4xl md:text-5xl font-black tracking-widest text-transparent bg-clip-text bg-gradient-to-r from-[#0088FF] to-[#8A2BE2]">
          Wateen
        </h1>
        <h2 className="text-2xl md:text-3xl font-bold text-slate-700 mt-2 tracking-wide">
          وَتِين
        </h2>
      </div>
    </div>
  );
};

export default WateenCanvasLogo;
