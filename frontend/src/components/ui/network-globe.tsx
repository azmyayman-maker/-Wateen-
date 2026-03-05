"use client";

import React, { useEffect, useRef } from "react";
import createGlobe from "cobe";
import { motion } from "framer-motion";

export function NetworkGlobe() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const pointerInteracting = useRef<number | null>(null);
  const pointerInteractionMovement = useRef(0);
  const fadeMaskRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let phi = 0;
    let width = 0;
    const canvas = canvasRef.current;
    if (!canvas) return;

    const onResize = () => {
        // High resolution for retina displays
        canvas.style.width = '100%';
        canvas.style.height = '100%';
        canvas.style.maxWidth = '1000px';
        canvas.style.aspectRatio = '1 / 1';
        width = canvas.offsetWidth;
    };
    window.addEventListener('resize', onResize);
    onResize();

    const globe = createGlobe(canvas, {
      devicePixelRatio: 2,
      width: width * 2,
      height: width * 2,
      phi: 0,
      theta: 0.3, // Slight tilt for architectural view
      dark: 1, // Deep dark mode
      diffuse: 1.2, // Light diffusion
      mapSamples: 16000, // Very dense samples for a "dotted particle network"
      mapBrightness: 6,
      baseColor: [0.02, 0.02, 0.04], // Almost black, matches #050505 bg perfectly when dark=1
      markerColor: [1, 0.7, 0], // #FFB300 Amber for Wateen Urgent/Active states
      glowColor: [0, 0.4, 1], // #0066FF Deep Blue Halo
      markers: [
        // Simulated Network Nodes (Hospitals, Dispatch Centers, Agencies)
        { location: [30.0444, 31.2357], size: 0.05 }, // Cairo
        { location: [24.7136, 46.6753], size: 0.04 }, // Riyadh
        { location: [25.2048, 55.2708], size: 0.03 }, // Dubai
        { location: [15.3229, 44.1955], size: 0.03 }, // Sana'a
        { location: [29.3759, 47.9774], size: 0.025 }, // Kuwait City
        { location: [31.9522, 35.2332], size: 0.03 }, // Jerusalem
        { location: [33.8886, 35.4955], size: 0.025 }, // Beirut
        { location: [25.2854, 51.5310], size: 0.03 }, // Doha
        { location: [33.3152, 44.3661], size: 0.04 }, // Baghdad
      ],
      onRender: (state) => {
        // Smooth auto-rotation unless interacting
        if (!pointerInteracting.current) {
          phi += 0.0025; // elegant, slow rotation
        } else {
          phi += pointerInteractionMovement.current;
          pointerInteractionMovement.current *= 0.9; // Friction
        }
        state.phi = phi;
        
        // Ensure size is dynamically updated
        if (state.width !== width * 2) {
          state.width = width * 2;
          state.height = width * 2;
        }
      },
    });

    // Cleanup
    const cleanup = () => {
      globe.destroy();
      window.removeEventListener('resize', onResize);
    };
    
    // Simulate initial fade-in mask for dramatic "boot up" effect
    setTimeout(() => {
      if (fadeMaskRef.current) {
        fadeMaskRef.current.style.opacity = '0';
      }
    }, 500);

    return cleanup;
  }, []);

  return (
    <div className="relative w-full h-full max-w-[800px] aspect-square flex items-center justify-center mx-auto">
      {/* Boot up fade mask */}
      <div 
        ref={fadeMaskRef} 
        className="absolute inset-0 bg-[#050505] z-10 pointer-events-none transition-opacity duration-[2000ms] ease-[cubic-bezier(0.16,1,0.3,1)] opacity-100" 
      />
      
      {/* Deep atmosphere glow behind globe, constrained slightly more */}
      <div className="absolute inset-0 bg-[#0066FF] opacity-[0.06] blur-[100px] rounded-full mix-blend-screen transform scale-75 animate-pulse" style={{ animationDuration: '6s' }} />
      
      <canvas
        ref={canvasRef}
        onPointerDown={(e) => {
          pointerInteracting.current =
            e.clientX - pointerInteractionMovement.current;
          if (canvasRef.current) {
            canvasRef.current.style.cursor = 'grabbing';
          }
        }}
        onPointerUp={() => {
          pointerInteracting.current = null;
          if (canvasRef.current) {
            canvasRef.current.style.cursor = 'grab';
          }
        }}
        onPointerOut={() => {
          pointerInteracting.current = null;
          if (canvasRef.current) {
            canvasRef.current.style.cursor = 'grab';
          }
        }}
        onMouseMove={(e) => {
          if (pointerInteracting.current !== null) {
            const delta = e.clientX - pointerInteracting.current;
            pointerInteractionMovement.current = delta * 0.005;
            pointerInteracting.current = e.clientX;
          }
        }}
        onTouchMove={(e) => {
          if (pointerInteracting.current !== null && e.touches[0]) {
            const delta = e.touches[0].clientX - pointerInteracting.current;
            pointerInteractionMovement.current = delta * 0.005;
            pointerInteracting.current = e.touches[0].clientX;
          }
        }}
        style={{
          width: "100%",
          height: "100%",
          contain: "layout paint size",
          cursor: "grab",
          mixBlendMode: "screen", // Essential for blending with the dark bg
        }}
      />
    </div>
  );
}
