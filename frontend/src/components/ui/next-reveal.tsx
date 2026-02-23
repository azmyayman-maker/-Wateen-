'use client';

import { cn } from "@/lib/utils";
import { useState } from 'react';

interface FlipTextProps {
  title?: string;
  highlightText?: string;
  className?: string;
}

export default function FlipTextReveal({ title = "Welcome,", highlightText = "Ahmed", className = "" }: FlipTextProps) {
  const [key, setKey] = useState(0);

  const replay = () => {
    setKey((prev) => prev + 1);
  };

  const titleWords = title ? title.split(" ").filter(Boolean) : [];
  const highlightWords = highlightText ? highlightText.split(" ").filter(Boolean) : [];

  return (
    <div className={cn("flip-container flex justify-center w-full", className)}>
      <h1 className="title flex flex-wrap gap-x-3 md:gap-x-4 items-center justify-center text-center" aria-label={`${title} ${highlightText}`}>
        {titleWords.map((word, i) => (
          <span
            key={`${key}-title-${i}`}
            className="word"
            style={{ "--index": i } as React.CSSProperties}
          >
            {word}
          </span>
        ))}
        {highlightWords.map((word, i) => (
          <span
            key={`${key}-highlight-${i}`}
            className="word text-[#79B253]"
            style={{ "--index": titleWords.length + i } as React.CSSProperties}
          >
            {word}
          </span>
        ))}
      </h1>

      <style>{`
        /* --- Layout --- */
        .flip-container {
          color: inherit;
          overflow: hidden;
          perspective: 800px; 
        }

        /* --- Typography --- */
        .title {
          margin: 0;
          line-height: inherit;
        }

        /* --- Animation Core --- */
        .word {
          display: inline-block;
          transform-origin: bottom center;
          
          opacity: 0;
          transform: rotateX(-90deg) translateY(20px);
          
          animation: flip-up 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
          animation-delay: calc(0.15s * var(--index));
          will-change: transform, opacity;
        }

        /* --- Keyframes --- */
        @keyframes flip-up {
          0% {
            opacity: 0;
            transform: rotateX(-90deg) translateY(20px);
          }
          100% {
            opacity: 1;
            transform: rotateX(0deg) translateY(0);
          }
        }

        @media (prefers-reduced-motion: reduce) {
          .word {
            opacity: 1 !important;
            transform: none !important;
            animation: none !important;
          }
        }
      `}</style>
    </div>
  );
}
