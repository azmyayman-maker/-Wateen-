import React from 'react';

type ConnectionMode = 'live' | 'reconnecting' | 'polling' | 'disconnected';

interface ConnectionBadgeProps {
  mode: ConnectionMode;
}

export function ConnectionBadge({ mode }: ConnectionBadgeProps) {
  const getModeConfig = () => {
    switch (mode) {
      case 'live':
        return {
          text: 'مباشر',
          color: 'bg-green-500',
          icon: (
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          ),
        };
      case 'reconnecting':
        return {
          text: 'جارِ الاتصال',
          color: 'bg-amber-500 animate-pulse',
          icon: (
            <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          ),
        };
      case 'polling':
        return {
          text: 'تحديث دوري',
          color: 'bg-blue-500',
          icon: (
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          ),
        };
      case 'disconnected':
        return {
          text: 'غير متصل',
          color: 'bg-red-500',
          icon: (
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          ),
        };
    }
  };

  const config = getModeConfig();

  return (
    <div
      className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-full text-white text-sm font-medium ${config.color}`}
    >
      {config.icon}
      <span className="ltr:ml-1 rtl:mr-1">{config.text}</span>
    </div>
  );
}
