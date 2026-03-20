import React from 'react';

interface StaleGPSBadgeProps {
  isStale: boolean;
}

export function StaleGPSBadge({ isStale }: StaleGPSBadgeProps) {
  if (!isStale) {
    return null;
  }

  return (
    <div
      className="
        inline-flex items-center gap-2 px-3 py-1.5 rounded-full
        bg-amber-100 dark:bg-amber-900/30
        text-amber-700 dark:text-amber-400
        text-sm font-medium
        animate-pulse
      "
    >
      <svg
        className="w-4 h-4"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
        />
      </svg>
      <span className="ltr:ml-1 rtl:mr-1">
        فقدان إشارة مؤقت — يتم تتبع آخر موقع معروف
      </span>
    </div>
  );
}
