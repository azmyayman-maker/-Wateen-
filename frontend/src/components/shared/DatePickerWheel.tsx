'use client';

import React, { useRef, useEffect, useState } from 'react';
import { cn } from '@/lib/utils';
import { ChevronUp, ChevronDown } from 'lucide-react';

interface WheelPickerProps {
  options: { label: string; value: number | string }[];
  value: number | string;
  onChange: (value: number | string) => void;
  itemHeight?: number;
  className?: string;
  align?: 'left' | 'center' | 'right';
}

export function WheelPicker({
  options,
  value,
  onChange,
  itemHeight = 40,
  className,
  align = 'center',
}: WheelPickerProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [isScrolling, setIsScrolling] = useState(false);
  const scrollTimeoutRef = useRef<NodeJS.Timeout>();

  // Center index
  const selectedIndex = options.findIndex((o) => o.value === value);
  // Add empty items to allow first/last items to be scrollable to the center
  const emptyItemsCount = 2; // For displaying 5 items (2 top, 1 center, 2 bottom)
  const totalHeight = itemHeight * 5;

  // Initialize scroll position when mounted
  useEffect(() => {
    if (scrollRef.current && selectedIndex !== -1) {
      scrollRef.current.scrollTop = selectedIndex * itemHeight;
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleScroll = () => {
    if (!scrollRef.current || isDragging.current) return;
    setIsScrolling(true);
    
    if (scrollTimeoutRef.current) {
      clearTimeout(scrollTimeoutRef.current);
    }

    scrollTimeoutRef.current = setTimeout(() => {
      setIsScrolling(false);
      if (!scrollRef.current) return;
      
      const scrollTop = scrollRef.current.scrollTop;
      const index = Math.round(scrollTop / itemHeight);
      
      if (index >= 0 && index < options.length) {
        onChange(options[index].value);
        // Correct perfectly to snap (just in case snap is slightly off on some browsers)
        scrollRef.current.scrollTo({
          top: index * itemHeight,
          behavior: 'smooth',
        });
      }
    }, 150);
  };

  // Drag to scroll implementation
  const isDragging = useRef(false);
  const startY = useRef(0);
  const startScrollTop = useRef(0);
  const dragged = useRef(false);

  const handleMouseDown = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!scrollRef.current) return;
    isDragging.current = true;
    dragged.current = false;
    startY.current = e.pageY;
    startScrollTop.current = scrollRef.current.scrollTop;
    
    // Temporarily disable snap to make dragging smoother
    scrollRef.current.style.scrollSnapType = 'none';
    scrollRef.current.style.cursor = 'grabbing';
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!isDragging.current || !scrollRef.current) return;
    e.preventDefault(); // Prevent text selection
    const y = e.pageY;
    const walk = y - startY.current;
    
    if (Math.abs(walk) > 3) {
      dragged.current = true;
    }
    
    scrollRef.current.scrollTop = startScrollTop.current - walk;
  };

  const handleMouseUpOrLeave = () => {
    if (!isDragging.current) return;
    isDragging.current = false;
    if (scrollRef.current) {
      scrollRef.current.style.scrollSnapType = 'y mandatory';
      scrollRef.current.style.cursor = 'grab';
      
      if (dragged.current) {
         const idx = Math.round(scrollRef.current.scrollTop / itemHeight);
         if (idx >= 0 && idx < options.length) {
            onChange(options[idx].value);
            scrollRef.current.scrollTo({ top: idx * itemHeight, behavior: 'smooth' });
         }
      }
    }
  };

  const scrollToIndex = (dir: 'up' | 'down') => {
    if (!scrollRef.current) return;
    let idx = Math.round(scrollRef.current.scrollTop / itemHeight);
    idx = dir === 'up' ? Math.max(0, idx - 1) : Math.min(options.length - 1, idx + 1);
    onChange(options[idx].value);
    scrollRef.current.scrollTo({ top: idx * itemHeight, behavior: 'smooth' });
  };

  return (
    <div 
      className={cn("relative overflow-hidden select-none", className)}
      style={{ height: totalHeight }}
    >
      {/* Top Chevron Button */}
      <div 
        className="absolute top-0 left-0 w-full flex items-center justify-center h-8 z-30 cursor-pointer text-slate-500 hover:text-cyan-400 hover:bg-slate-800/50 transition-colors rounded-t-md opacity-0 hover:opacity-100 group-hover:opacity-100"
        onClick={() => scrollToIndex('up')}
      >
        <ChevronUp className="w-5 h-5" />
      </div>

      {/* Center Highlight / Selection area */}
      <div 
        className="absolute top-1/2 left-0 w-full -translate-y-1/2 rounded-md bg-white/5 border border-white/10 pointer-events-none z-10"
        style={{ height: itemHeight }}
      />
      
      {/* Scrollable Container */}
      <div
        ref={scrollRef}
        onScroll={handleScroll}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUpOrLeave}
        onMouseLeave={handleMouseUpOrLeave}
        className="h-full overflow-y-auto no-scrollbar snap-y snap-mandatory relative z-20 mask-image-vertical-fading cursor-grab"
        style={{ 
          // Fade out top and bottom
          maskImage: 'linear-gradient(to bottom, transparent 0%, black 30%, black 70%, transparent 100%)',
          WebkitMaskImage: 'linear-gradient(to bottom, transparent 0%, black 30%, black 70%, transparent 100%)',
        }}
      >
        {/* Top Empty Pad */}
        <div style={{ height: itemHeight * emptyItemsCount }} />
        
        {options.map((option, idx) => {
          const isSelected = value === option.value;
          const distance = Math.abs(selectedIndex - idx);
          
          return (
            <div
              key={option.value}
              className={cn(
                "w-full flex items-center px-4 snap-center cursor-pointer transition-all duration-300",
                align === 'center' ? 'justify-center' : align === 'left' ? 'justify-start' : 'justify-end',
                "font-medium",
                isSelected 
                  ? "text-white text-lg font-bold" 
                  : distance === 1 
                    ? "text-white/60 text-base" 
                    : "text-white/30 text-sm"
              )}
              style={{ height: itemHeight }}
              onClick={(e) => {
                if (dragged.current) {
                  e.preventDefault();
                  e.stopPropagation();
                  return;
                }
                onChange(option.value);
                scrollRef.current?.scrollTo({
                  top: idx * itemHeight,
                  behavior: 'smooth'
                });
              }}
            >
              {option.label}
            </div>
          );
        })}
        
        {/* Bottom Empty Pad */}
        <div style={{ height: itemHeight * emptyItemsCount }} />
      </div>

      {/* Bottom Chevron Button */}
      <div 
        className="absolute bottom-0 left-0 w-full flex items-center justify-center h-8 z-30 cursor-pointer text-slate-500 hover:text-cyan-400 hover:bg-slate-800/50 transition-colors rounded-b-md opacity-0 hover:opacity-100 group-hover:opacity-100"
        onClick={() => scrollToIndex('down')}
      >
        <ChevronDown className="w-5 h-5" />
      </div>
    </div>
  );
}

// ----------------------------------------------------------------------------
// DatePicker Component
// ----------------------------------------------------------------------------

interface DatePickerProps {
  date: Date;
  onChange: (date: Date) => void;
  className?: string;
  minYear?: number;
  maxYear?: number;
}

export function DatePickerWheel({
  date,
  onChange,
  className,
  minYear = 1940,
  maxYear = new Date().getFullYear(),
}: DatePickerProps) {
  
  const currentDay = date.getDate();
  const currentMonth = date.getMonth(); // 0-11
  const currentYear = date.getFullYear();

  // Generate Days (1-31 depending on month/year)
  const getDaysInMonth = (month: number, year: number) => new Date(year, month + 1, 0).getDate();
  const daysCount = getDaysInMonth(currentMonth, currentYear);
  
  const daysOptions = Array.from({ length: daysCount }, (_, i) => ({
    label: (i + 1).toString().padStart(2, '0'),
    value: i + 1,
  }));

  const monthsOptions = [
    { label: 'يناير', value: 0 },
    { label: 'فبراير', value: 1 },
    { label: 'مارس', value: 2 },
    { label: 'أبريل', value: 3 },
    { label: 'مايو', value: 4 },
    { label: 'يونيو', value: 5 },
    { label: 'يوليو', value: 6 },
    { label: 'أغسطس', value: 7 },
    { label: 'سبتمبر', value: 8 },
    { label: 'أكتوبر', value: 9 },
    { label: 'نوفمبر', value: 10 },
    { label: 'ديسمبر', value: 11 },
  ];

  const yearsOptions = Array.from({ length: maxYear - minYear + 1 }, (_, i) => {
    const y = maxYear - i;
    return { label: y.toString(), value: y };
  });

  const handleDayChange = (v: number | string) => {
    const newDate = new Date(date);
    newDate.setDate(Number(v));
    onChange(newDate);
  };

  const handleMonthChange = (v: number | string) => {
    const m = Number(v);
    const newDate = new Date(date);
    // Adjust day if month has fewer days
    const maxDay = getDaysInMonth(m, currentYear);
    if (currentDay > maxDay) newDate.setDate(maxDay);
    newDate.setMonth(m);
    onChange(newDate);
  };

  const handleYearChange = (v: number | string) => {
    const y = Number(v);
    const newDate = new Date(date);
    const maxDay = getDaysInMonth(currentMonth, y);
    if (currentDay > maxDay) newDate.setDate(maxDay);
    newDate.setFullYear(y);
    onChange(newDate);
  };

  return (
    <div className={cn("flex flex-row-reverse items-center justify-between bg-slate-900/40 rounded-2xl border border-slate-700/50 p-4 gap-2", className)} dir="ltr">
      {/* Day */}
      <WheelPicker 
        options={daysOptions} 
        value={currentDay} 
        onChange={handleDayChange} 
        className="flex-1"
        align="center"
      />
      
      {/* Month */}
      <WheelPicker 
        options={monthsOptions} 
        value={currentMonth} 
        onChange={handleMonthChange} 
        className="flex-[1.5]"
        align="center"
      />
      
      {/* Year */}
      <WheelPicker 
        options={yearsOptions} 
        value={currentYear} 
        onChange={handleYearChange} 
        className="flex-1"
        align="center"
      />
    </div>
  );
}
