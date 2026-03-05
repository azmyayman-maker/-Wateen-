"use client";

import { useMotionValue, motion, useMotionTemplate } from "framer-motion";
import React, { MouseEvent as ReactMouseEvent, useState } from "react";
import { cn } from "@/lib/utils";

export const CardSpotlight = ({
  children,
  radius = 350,
  color = "#262626",
  className,
  spotlightColors,
  ...props
}: {
  radius?: number;
  color?: string;
  children: React.ReactNode;
  spotlightColors?: number[][];
} & React.HTMLAttributes<HTMLDivElement>) => {
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  function handleMouseMove({
    currentTarget,
    clientX,
    clientY,
  }: ReactMouseEvent<HTMLDivElement>) {
    let { left, top } = currentTarget.getBoundingClientRect();
    mouseX.set(clientX - left);
    mouseY.set(clientY - top);
  }

  const [isHovering, setIsHovering] = useState(false);
  const handleMouseEnter = () => setIsHovering(true);
  const handleMouseLeave = () => setIsHovering(false);

  // Build CSS-based dot grid color from spotlightColors
  const dotColor = spotlightColors?.[0]
    ? `rgba(${spotlightColors[0][0]}, ${spotlightColors[0][1]}, ${spotlightColors[0][2]}, 0.4)`
    : "rgba(59, 130, 246, 0.4)";

  const dotColor2 = spotlightColors?.[1]
    ? `rgba(${spotlightColors[1][0]}, ${spotlightColors[1][1]}, ${spotlightColors[1][2]}, 0.25)`
    : "rgba(139, 92, 246, 0.25)";

  return (
    <div
      className={cn(
        "group/spotlight rounded-md relative border border-neutral-800 bg-black dark:border-neutral-800",
        className
      )}
      onMouseMove={handleMouseMove}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      {...props}
    >
      {/* Spotlight radial gradient — follows mouse */}
      <motion.div
        className="pointer-events-none absolute z-0 -inset-px rounded-md opacity-0 transition duration-300 group-hover/spotlight:opacity-100"
        style={{
          backgroundColor: color,
          maskImage: useMotionTemplate`
            radial-gradient(
              ${radius}px circle at ${mouseX}px ${mouseY}px,
              white,
              transparent 80%
            )
          `,
        }}
      >
        {/* CSS-based animated dot grid — replaces WebGL CanvasRevealEffect */}
        {isHovering && (
          <div
            className="absolute inset-0 pointer-events-none animate-pulse"
            style={{
              backgroundImage: `
                radial-gradient(${dotColor} 1px, transparent 1px),
                radial-gradient(${dotColor2} 1px, transparent 1px)
              `,
              backgroundSize: "8px 8px, 12px 12px",
              backgroundPosition: "0 0, 4px 4px",
            }}
          />
        )}
      </motion.div>

      {/* Hover border glow effect */}
      <motion.div
        className="pointer-events-none absolute -inset-px rounded-md opacity-0 transition duration-500 group-hover/spotlight:opacity-100"
        style={{
          background: useMotionTemplate`
            radial-gradient(
              ${radius * 0.6}px circle at ${mouseX}px ${mouseY}px,
              ${dotColor},
              transparent 70%
            )
          `,
          mixBlendMode: "soft-light",
        }}
      />

      {children}
    </div>
  );
};
