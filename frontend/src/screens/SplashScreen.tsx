import React, { useEffect, useState } from 'react';
import { Fingerprint, Shield, Sparkles } from 'lucide-react';

interface SplashScreenProps {
  onFinish: () => void;
}

export const SplashScreen: React.FC<SplashScreenProps> = ({ onFinish }) => {
  const [progress, setProgress] = useState(15);

  useEffect(() => {
    const timer1 = setTimeout(() => setProgress(55), 400);
    const timer2 = setTimeout(() => setProgress(90), 800);
    const timer3 = setTimeout(() => {
      setProgress(100);
      setTimeout(onFinish, 300);
    }, 1100);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
    };
  }, [onFinish]);

  return (
    <div className="absolute inset-0 bg-slate-950 flex flex-col items-center justify-between p-8 z-50 select-none">
      <div className="w-full flex justify-end">
        <span className="text-[10px] font-mono text-slate-500 uppercase tracking-widest">
          v2.4.0 · CAPACITOR READY
        </span>
      </div>

      <div className="flex flex-col items-center text-center">
        {/* Animated Brand Emblem */}
        <div className="relative mb-6">
          <div className="w-24 h-24 rounded-3xl bg-slate-900 border border-emerald-500/30 flex items-center justify-center shadow-2xl shadow-emerald-500/20">
            <Fingerprint className="w-14 h-14 text-emerald-400 stroke-[1.8]" />
          </div>
          <div className="absolute -bottom-2 -right-2 w-8 h-8 rounded-full bg-slate-900 border border-emerald-500/40 flex items-center justify-center text-emerald-400">
            <Shield className="w-4 h-4 fill-emerald-500/20" />
          </div>
        </div>

        {/* Wordmark & Tagline */}
        <h1 className="text-2xl font-extrabold tracking-tight text-white">
          KOSHA LABS
        </h1>
        <p className="text-xs font-medium text-emerald-400 tracking-wide mt-1">
          Intelligent Worker Identity Management System
        </p>

        <div className="mt-4 px-3 py-1 rounded-full bg-slate-900/80 border border-slate-800 text-[11px] text-slate-400">
          One Worker · One Identity · Multiple Sessions
        </div>
      </div>

      {/* Progress & Initializing status */}
      <div className="w-full max-w-xs space-y-3 pb-6">
        <div className="flex justify-between items-center text-[11px] font-mono text-slate-400">
          <span>Initializing Optical Biometrics Engine</span>
          <span className="text-emerald-400 font-bold">{progress}%</span>
        </div>

        <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-emerald-500 to-teal-400 rounded-full transition-all duration-300 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>

        <p className="text-[10px] text-center text-slate-500">
          Securing industrial field workforce identity
        </p>
      </div>
    </div>
  );
};
