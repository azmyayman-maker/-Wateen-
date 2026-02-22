"use client";

import React, { useRef, useEffect, useCallback } from "react";

/**
 * LiveECGMonitor — A real-time Canvas-based ECG heart monitor.
 * Draws a continuously advancing heartbeat waveform with natural variation,
 * glow effects, and a trailing fade — just like a real hospital monitor.
 */
export function LiveECGMonitor() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animRef = useRef<number>(0);

  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // High-DPI support
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    if (canvas.width !== rect.width * dpr || canvas.height !== rect.height * dpr) {
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      ctx.scale(dpr, dpr);
    }

    const W = rect.width;
    const H = rect.height;
    const midY = H * 0.5;

    // --- ECG Waveform Generation ---
    // One full PQRST complex cycle length in pixels
    const cycleLen = 180;
    // Speed: pixels per frame
    const speed = 1.8;

    // Time-based offset for continuous scrolling
    const now = performance.now();
    const offset = (now * speed * 0.06) % cycleLen;

    // Generate Y value for a given X position in the waveform cycle
    function ecgY(phase: number, beatVariation: number): number {
      // Normalize phase to 0-1 within a cycle
      const p = ((phase % 1) + 1) % 1;
      const amp = H * 0.35;
      const bv = beatVariation;

      // P wave (small bump)
      if (p > 0.05 && p < 0.15) {
        const t = (p - 0.05) / 0.1;
        return midY - Math.sin(t * Math.PI) * amp * 0.12 * bv;
      }
      // Q dip (small negative)
      if (p >= 0.18 && p < 0.22) {
        const t = (p - 0.18) / 0.04;
        return midY + Math.sin(t * Math.PI) * amp * 0.1 * bv;
      }
      // R peak (tall spike)
      if (p >= 0.22 && p < 0.30) {
        const t = (p - 0.22) / 0.08;
        return midY - Math.sin(t * Math.PI) * amp * 0.85 * bv;
      }
      // S dip (negative after R)
      if (p >= 0.30 && p < 0.36) {
        const t = (p - 0.30) / 0.06;
        return midY + Math.sin(t * Math.PI) * amp * 0.25 * bv;
      }
      // T wave (medium bump)
      if (p > 0.42 && p < 0.58) {
        const t = (p - 0.42) / 0.16;
        return midY - Math.sin(t * Math.PI) * amp * 0.2 * bv;
      }
      // Baseline
      return midY;
    }

    // Clear canvas
    ctx.clearRect(0, 0, W, H);

    // --- Draw Grid (subtle) ---
    ctx.strokeStyle = "rgba(255,255,255,0.04)";
    ctx.lineWidth = 1;
    const gridSize = 24;
    for (let x = 0; x < W; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, H);
      ctx.stroke();
    }
    for (let y = 0; y < H; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(W, y);
      ctx.stroke();
    }

    // --- Draw ECG Trace ---
    // Build the path points
    const points: { x: number; y: number }[] = [];
    for (let x = 0; x <= W; x += 1) {
      const worldX = x + offset;
      const cyclePos = worldX / cycleLen;
      const phase = cyclePos % 1;
      // Natural variation per beat — slight randomness seeded by cycle index
      const beatIdx = Math.floor(cyclePos);
      const variation = 0.85 + 0.3 * Math.abs(Math.sin(beatIdx * 2.718 + beatIdx * 0.37));
      const y = ecgY(phase, variation);
      points.push({ x, y });
    }

    // Trailing glow layer (thicker, softer)
    ctx.save();
    ctx.shadowColor = "rgba(225, 29, 72, 0.6)";
    ctx.shadowBlur = 20;
    ctx.strokeStyle = "rgba(225, 29, 72, 0.3)";
    ctx.lineWidth = 4;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.beginPath();
    for (let i = 0; i < points.length; i++) {
      if (i === 0) ctx.moveTo(points[i].x, points[i].y);
      else ctx.lineTo(points[i].x, points[i].y);
    }
    ctx.stroke();
    ctx.restore();

    // Main bright line
    ctx.save();
    ctx.shadowColor = "rgba(225, 29, 72, 0.8)";
    ctx.shadowBlur = 10;
    const gradient = ctx.createLinearGradient(0, 0, W, 0);
    gradient.addColorStop(0, "rgba(225, 29, 72, 0.1)");
    gradient.addColorStop(0.15, "rgba(225, 29, 72, 0.9)");
    gradient.addColorStop(0.85, "rgba(225, 29, 72, 0.9)");
    gradient.addColorStop(1, "rgba(225, 29, 72, 0.1)");
    ctx.strokeStyle = gradient;
    ctx.lineWidth = 2.5;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.beginPath();
    for (let i = 0; i < points.length; i++) {
      if (i === 0) ctx.moveTo(points[i].x, points[i].y);
      else ctx.lineTo(points[i].x, points[i].y);
    }
    ctx.stroke();
    ctx.restore();

    // Bright dot at scan head (right edge)
    const headX = W * 0.88;
    const headIdx = Math.min(Math.round(headX), points.length - 1);
    const headY = points[headIdx]?.y ?? midY;
    ctx.save();
    ctx.shadowColor = "rgba(225, 29, 72, 1)";
    ctx.shadowBlur = 18;
    ctx.fillStyle = "rgba(251, 113, 133, 0.9)";
    ctx.beginPath();
    ctx.arc(headX, headY, 3.5, 0, Math.PI * 2);
    ctx.fill();
    // Outer pulse ring
    const pulse = 0.5 + 0.5 * Math.sin(now * 0.008);
    ctx.globalAlpha = 0.3 * pulse;
    ctx.fillStyle = "rgba(225, 29, 72, 0.5)";
    ctx.beginPath();
    ctx.arc(headX, headY, 8 + pulse * 4, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    animRef.current = requestAnimationFrame(draw);
  }, []);

  useEffect(() => {
    animRef.current = requestAnimationFrame(draw);
    return () => cancelAnimationFrame(animRef.current);
  }, [draw]);

  return (
    <canvas
      ref={canvasRef}
      className="w-full h-full"
      style={{ display: "block" }}
    />
  );
}

export default LiveECGMonitor;
