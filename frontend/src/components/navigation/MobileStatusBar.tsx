import React, { useState, useEffect } from 'react';
import { Wifi, Battery } from 'lucide-react';

export const MobileStatusBar: React.FC = () => {
  const [time, setTime] = useState<string>('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTime(
        now.toLocaleTimeString([], {
          hour: '2-digit',
          minute: '2-digit',
          hour12: false,
        })
      );
    };
    updateTime();
    const interval = setInterval(updateTime, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="w-full h-8 px-6 pt-1 flex items-center justify-between text-xs text-slate-300 dark:text-slate-300 font-medium select-none z-40 shrink-0">
      {/* Time */}
      <span className="font-semibold text-xs tracking-tight">{time || '09:41'}</span>

      {/* Status Icons */}
      <div className="flex items-center gap-1.5 text-slate-300">
        <div className="flex items-end gap-0.5 h-2.5">
          <span className="w-0.5 h-1 bg-current rounded-sm" />
          <span className="w-0.5 h-1.5 bg-current rounded-sm" />
          <span className="w-0.5 h-2 bg-current rounded-sm" />
          <span className="w-0.5 h-2.5 bg-current rounded-sm" />
        </div>
        <Wifi className="w-3.5 h-3.5" />
        <div className="flex items-center gap-0.5 ml-1">
          <span className="text-[10px] font-mono">98%</span>
          <Battery className="w-4 h-4 fill-emerald-500 text-emerald-500" />
        </div>
      </div>
    </div>
  );
};
