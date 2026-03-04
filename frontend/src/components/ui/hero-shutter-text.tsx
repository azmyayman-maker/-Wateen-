'use client';

import { cn } from "@/lib/utils";
import React from "react";
import { motion, AnimatePresence } from "framer-motion";

interface HeroTextProps {
  text?: string;
  className?: string;
}

export default function HeroText({
  text = "IMMERSE",
  className = "",
}: HeroTextProps) {
  // We use word splitting if it's Arabic to prevent disconnecting cursive letters.
  // We also remove the hardcoded text-[15vw] so the component can be integrated 
  // into dashboards cleanly without breaking the layout.
  const hasArabic = /[\u0600-\u06FF]/.test(text);
  const items = hasArabic ? text.split(" ") : text.split("");

  return (
    <div
      className={cn(
        "relative flex flex-col items-center justify-center transition-colors duration-700",
        className
      )}
    >
      {/* Main Text Container */}
      <div className="relative z-10 w-full flex flex-col items-center">
        <AnimatePresence mode="wait">
          <motion.div
            key="shutter-text-static-count"
            className="flex flex-wrap justify-center items-center w-full"
          >
            {items.map((item, i) => (
              <div
                key={i}
                className="relative px-[0.1vw] overflow-hidden group"
              >
                {/* Main Character / Word */}
                <motion.span
                  initial={{ opacity: 0, filter: "blur(10px)" }}
                  animate={{ opacity: 1, filter: "blur(0px)" }}
                  transition={{ delay: i * 0.04 + 0.3, duration: 0.8 }}
                  className="leading-none font-black tracking-tighter"
                >
                  {item === " " ? "\u00A0" : item}
                </motion.span>

                {/* Top Slice Layer */}
                <motion.span
                  initial={{ x: "-100%", opacity: 0 }}
                  animate={{ x: "100%", opacity: [0, 1, 0] }}
                  transition={{
                    duration: 0.7,
                    delay: i * 0.04,
                    ease: "easeInOut",
                  }}
                  className="absolute inset-0 leading-none font-black text-indigo-600 dark:text-emerald-400 z-10 pointer-events-none"
                  style={{ clipPath: "polygon(0 0, 100% 0, 100% 35%, 0 35%)" }}
                >
                  {item}
                </motion.span>

                {/* Middle Slice Layer */}
                <motion.span
                  initial={{ x: "100%", opacity: 0 }}
                  animate={{ x: "-100%", opacity: [0, 1, 0] }}
                  transition={{
                    duration: 0.7,
                    delay: i * 0.04 + 0.1,
                    ease: "easeInOut",
                  }}
                  className="absolute inset-0 leading-none font-black text-zinc-800 dark:text-amber-500 z-10 pointer-events-none"
                  style={{
                    clipPath: "polygon(0 35%, 100% 35%, 100% 65%, 0 65%)",
                  }}
                >
                  {item}
                </motion.span>

                {/* Bottom Slice Layer */}
                <motion.span
                  initial={{ x: "-100%", opacity: 0 }}
                  animate={{ x: "100%", opacity: [0, 1, 0] }}
                  transition={{
                    duration: 0.7,
                    delay: i * 0.04 + 0.2,
                    ease: "easeInOut",
                  }}
                  className="absolute inset-0 leading-none font-black text-indigo-600 dark:text-emerald-400 z-10 pointer-events-none"
                  style={{
                    clipPath: "polygon(0 65%, 100% 65%, 100% 100%, 0 100%)",
                  }}
                >
                  {item}
                </motion.span>
              </div>
            ))}
          </motion.div>
        </AnimatePresence>
      </div>
      {/* Intentionally removed the background grids, corner accents, and the manual refresh button to cleanly integrate into the dashboards. */}
    </div>
  );
}
