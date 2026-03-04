"use client";

import React from "react";

export function WateenSpinner() {
  return (
    <div className="relative flex items-center justify-center w-full h-full min-h-[300px]">
      {/* 
        The SVG Viewport and aspect ratio. 
        Breathing animation is applied to the outermost SVG element wrapper for the micro-interaction.
      */}
      <svg
        className="w-48 h-48 sm:w-64 sm:h-64 animate-wateen-breathe"
        viewBox="0 0 400 200"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          {/* Gradient Definition: Cyan -> Primary Blue -> Purple */}
          <linearGradient id="wateenGradient" x1="0%" y1="50%" x2="100%" y2="50%">
            <stop offset="0%" stopColor="#00FFFF" />
            <stop offset="50%" stopColor="#0066FF" />
            <stop offset="100%" stopColor="#8A2BE2" />
          </linearGradient>

          {/* 
            Glow Filter to add the hyper-premium glass/neon effect 
            We use multiple blurs to create a soft, wide glow and a tight, bright core glow.
          */}
          <filter id="neonGlow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="4" result="blur1" />
            <feGaussianBlur stdDeviation="8" result="blur2" />
            <feGaussianBlur stdDeviation="15" result="blur3" />
            <feMerge>
              <feMergeNode in="blur3" />
              <feMergeNode in="blur2" />
              <feMergeNode in="blur1" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* 
          The Heartbeat 'W' Path 
          This path simulates an ECG tracing that forms a 'W'.
          M: Move to start (flat line left)
          L: Line to (the peaks and valleys of the heartbeat/W)
          L: Line to end (flat line right)

          d="M 20 100 L 100 100 L 130 50 L 160 150 L 200 20 L 240 150 L 270 50 L 300 100 L 380 100"
        */}
        <path
          d="M 20 100 L 100 100 L 130 50 L 160 150 L 200 20 L 240 150 L 270 50 L 300 100 L 380 100"
          stroke="url(#wateenGradient)"
          strokeWidth="8"
          strokeLinecap="round"
          strokeLinejoin="round"
          fill="none"
          filter="url(#neonGlow)"
          /* The animation class handling the continuous pulse path-drawing effect */
          className="animate-wateen-pulse"
        />
        
        {/*
          Faded background track (optional: gives the pulse a rail to travel on)
        */}
        <path
          d="M 20 100 L 100 100 L 130 50 L 160 150 L 200 20 L 240 150 L 270 50 L 300 100 L 380 100"
          stroke="url(#wateenGradient)"
          strokeWidth="8"
          strokeLinecap="round"
          strokeLinejoin="round"
          fill="none"
          opacity="0.1"
        />
      </svg>
    </div>
  );
}
