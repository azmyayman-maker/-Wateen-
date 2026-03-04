"use client";

import React, { useEffect, useState } from 'react';

interface WateenAnimatedLogoProps {
  className?: string;
  width?: number;
  height?: number;
}

export const WateenAnimatedLogo: React.FC<WateenAnimatedLogoProps> = ({
  className = "",
  width = 340,
  height = 100,
}) => {
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    // Slight delay to ensure smooth entrance after render
    const timer = setTimeout(() => setIsLoaded(true), 100);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className={`flex flex-col items-center justify-center ${className} relative`}>
      <style dangerouslySetInnerHTML={{__html: `
        @keyframes fade-in-up {
          0% { opacity: 0; transform: translateY(20px); }
          100% { opacity: 1; transform: translateY(0); }
        }
        @keyframes cinematic-entrance {
          0% { opacity: 0; transform: scale(0.85) translateY(10px); filter: blur(8px); }
          100% { opacity: 1; transform: scale(1) translateY(0); filter: blur(0); }
        }
        @keyframes float-breathing {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-4px); }
        }
      `}} />
      
      <div className="relative flex justify-center items-center w-full" style={{ height: Math.max(height, 140) }}>
        {/* The Actual Image Logo with premium cinematic entrance */}
        <div 
          className={`w-32 h-32 md:w-36 md:h-36 transition-all duration-[2000ms] ease-[cubic-bezier(0.16,1,0.3,1)] ${
            isLoaded ? 'opacity-100 scale-100 blur-none' : 'opacity-0 scale-75 blur-md translate-y-4'
          }`}
        >
          <div className="w-full h-full animate-[float-breathing_6s_ease-in-out_infinite_2s]">
            <img 
              src="/images/icon.svg" 
              alt="Wateen Logo"
              className="w-full h-full object-contain drop-shadow-2xl"
            />
          </div>
        </div>
      </div>

      {/* Typography Entrances */}
      <div className={`mt-4 text-center select-none transition-all duration-[1500ms] ease-[cubic-bezier(0.16,1,0.3,1)] delay-750 ${
        isLoaded ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
      }`}>
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

export default WateenAnimatedLogo;
