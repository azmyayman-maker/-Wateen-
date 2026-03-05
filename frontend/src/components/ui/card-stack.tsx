"use client";
import { useEffect, useState, useRef, useCallback } from "react";
import { motion } from "framer-motion";
import { ChevronRight, ChevronLeft, Pause, Play } from "lucide-react";

let interval: any;

export type Card = {
  id: number;
  name: string;
  designation: React.ReactNode;
  content: React.ReactNode;
  link?: string;
};

export const CardStack = ({
  items,
  offset,
  scaleFactor,
}: {
  items: Card[];
  offset?: number;
  scaleFactor?: number;
}) => {
  const CARD_OFFSET = offset || 10;
  const SCALE_FACTOR = scaleFactor || 0.06;
  const intervalRef = useRef<any>(null);
  const [isPaused, setIsPaused] = useState(false);
  const [cards, setCards] = useState<Card[]>(items);

  const startFlipping = useCallback(() => {
    if (intervalRef.current) clearInterval(intervalRef.current);
    intervalRef.current = setInterval(() => {
      setCards((prevCards: Card[]) => {
        const newArray = [...prevCards];
        newArray.unshift(newArray.pop()!); // move last to front
        return newArray;
      });
    }, 5000);
  }, []);

  useEffect(() => {
    if (!isPaused) {
      startFlipping();
    }
    return () => clearInterval(intervalRef.current);
  }, [isPaused, startFlipping]);

  const handleNext = () => {
    setCards((prevCards: Card[]) => {
      const newArray = [...prevCards];
      newArray.unshift(newArray.pop()!);
      return newArray;
    });
    if (!isPaused) startFlipping(); // Reset timer if not paused
  };

  const handlePrev = () => {
    setCards((prevCards: Card[]) => {
      const newArray = [...prevCards];
      newArray.push(newArray.shift()!); // move front to last
      return newArray;
    });
    if (!isPaused) startFlipping();
  };

  const togglePause = () => {
    setIsPaused((prev) => !prev);
  };

  return (
    <div className="flex flex-col items-center w-full">
      <div className="relative h-60 w-full md:h-60" dir="rtl">
      {cards.map((card, index) => {
        return (
            <motion.div
              key={card.id}
              onClick={() => {
                if (card.link) window.location.hash = `/${card.link}`;
              }}
              className={`absolute bg-[#0a0f1c]/80 backdrop-blur-xl h-60 w-full rounded-2xl p-6 shadow-xl border border-white/10 shadow-black/[0.5] flex flex-col justify-between ${
                card.link ? "cursor-pointer hover:-translate-y-1 transition-transform" : ""
              }`}
              style={{
                transformOrigin: "top center",
              }}
              animate={{
                top: index * CARD_OFFSET,
                scale: 1 - index * SCALE_FACTOR, // decrease scale for cards that are behind
                zIndex: cards.length - index, //  decrease z-index for the cards that are behind
              }}
              whileHover={card.link ? {
                boxShadow: "0 0 25px rgba(0, 102, 255, 0.2)",
                borderColor: "rgba(255, 255, 255, 0.2)"
              } : {}}
            >
            <div className="font-normal text-slate-300 font-['Amiri',_'Outfit',_sans-serif] text-lg leading-relaxed">
              {card.content}
            </div>
            <div>
              <p className="text-white font-bold font-['Fira_Sans',_sans-serif]">
                {card.name}
              </p>
              <div className="text-slate-400 font-normal mt-1 text-sm font-['Fira_Code',_monospace]">
                {card.designation}
              </div>
            </div>
          </motion.div>
        );
      })}
      </div>
      
      {/* ─── Manual Controls & Timeline ─── */}
      <div className="flex items-center gap-4 mt-8 z-30" dir="ltr">
        <button
          onClick={handlePrev}
          className="p-2 rounded-full bg-white/5 border border-white/10 text-white hover:bg-white/10 hover:border-white/20 transition-all duration-200"
          title="التالي"
        >
          <ChevronLeft className="w-5 h-5 text-slate-300" />
        </button>

        {/* Timeline Bar Based on Current Card */}
        <div className="flex items-center gap-1.5 min-w-[100px] justify-center">
          {items.map((item, i) => {
            const isActive = cards[0]?.id === item.id;
            return (
              <div 
                key={item.id} 
                className={`h-1.5 rounded-full overflow-hidden transition-all duration-300 ${isActive ? 'w-8 bg-[#0066FF]/30' : 'w-2 bg-white/10'}`}
              >
                {isActive && !isPaused && (
                  <motion.div
                    key={cards[0]?.id} // Trigger animation on card change
                    initial={{ width: "0%" }}
                    animate={{ width: "100%" }}
                    transition={{ duration: 5, ease: "linear" }}
                    className="h-full bg-gradient-to-r from-[#0066FF] to-[#00E5FF]"
                  />
                )}
                {isActive && isPaused && (
                  <div className="h-full w-full bg-[#0066FF]" />
                )}
              </div>
            );
          })}
        </div>

        <button
          onClick={handleNext}
          className="p-2 rounded-full bg-white/5 border border-white/10 text-white hover:bg-white/10 hover:border-white/20 transition-all duration-200"
          title="السابق"
        >
          <ChevronRight className="w-5 h-5 text-slate-300" />
        </button>
      </div>
    </div>
  );
};
