"use client";

import React, { useRef, useState } from "react";
import { motion, useMotionValue, useSpring, useTransform } from "framer-motion";
import { cn } from "@/lib/utils";

interface TiltCardProps {
  children: React.ReactNode;
  className?: string;
}

export const TiltCard = ({ children, className }: TiltCardProps) => {
  const ref = useRef<HTMLDivElement>(null);
  const [isHovered, setIsHovered] = useState(false);

  // Mouse position values
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  // Smooth springs for buttery 60fps physics
  const springX = useSpring(mouseX, { stiffness: 300, damping: 30 });
  const springY = useSpring(mouseY, { stiffness: 300, damping: 30 });

  // Transform raw mouse values to rotation degrees
  // rotateX is driven by Y-axis movement (up/down)
  // rotateY is driven by X-axis movement (left/right)
  // We use a relatively small rotation range (-10 to 10 degrees) for realism
  const rotateX = useTransform(springY, [-1, 1], [10, -10]);
  const rotateY = useTransform(springX, [-1, 1], [-10, 10]);

  // Glare effect transforms based on mouse position
  // We want the glare to move opposite to the tilt for physical realism
  const glareX = useTransform(springX, [-1, 1], ["0%", "100%"]);
  const glareY = useTransform(springY, [-1, 1], ["0%", "100%"]);
  const glareOpacity = useTransform(
    springY,
    [-1, 1],
    // Opacity increases slightly when tilting towards the light source
    [0.1, 0.3]
  );

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!ref.current) return;

    const rect = ref.current.getBoundingClientRect();

    // Calculate mouse position relative to card center, normalized to [-1, 1]
    const centerX = rect.x + rect.width / 2;
    const centerY = rect.y + rect.height / 2;

    const normalizedX = (e.clientX - centerX) / (rect.width / 2);
    const normalizedY = (e.clientY - centerY) / (rect.height / 2);

    mouseX.set(normalizedX);
    mouseY.set(normalizedY);
  };

  const handleMouseEnter = () => {
    setIsHovered(true);
  };

  const handleMouseLeave = () => {
    setIsHovered(false);
    // Reset tilt and glare slowly on leave
    mouseX.set(0);
    mouseY.set(0);
  };

  return (
    <div
      className="relative [perspective:1000px] w-full h-full"
      style={{
        transformStyle: "preserve-3d",
      }}
    >
      <motion.div
        ref={ref}
        onMouseMove={handleMouseMove}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        style={{
          rotateX,
          rotateY,
          transformStyle: "preserve-3d",
        }}
        className={cn(
          "relative w-full h-full rounded-2xl overflow-hidden cursor-pointer",
          className
        )}
      >
        {/* The Card Content */}
        {children}

        {/* Dynamic Glare Overlay */}
        <motion.div
          className="pointer-events-none absolute inset-0 z-50 transition-opacity duration-300"
          style={{
            background: `radial-gradient(
              farthest-corner circle at var(--x, 50%) var(--y, 50%),
              rgba(255, 255, 255, 0.4) 0%,
              rgba(255, 255, 255, 0) 60%
            )`,
            // Instead of mapping css vars, we can achieve this with a direct motion style if preferred,
            // but the CSS variable approach is often simpler. Let's use a simpler linear gradient approach
            // driven directly by framer-motion transforms for performance.
            backgroundImage: "linear-gradient(105deg, transparent 20%, rgba(255,255,255,0.1) 25%, transparent 30%)",
            backgroundSize: "200% 200%",
            backgroundPositionX: glareX,
            backgroundPositionY: glareY,
            opacity: isHovered ? glareOpacity : 0,
            transition: "opacity 0.3s ease",
          }}
        />
      </motion.div>
    </div>
  );
};
