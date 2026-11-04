import React from 'react';

interface FingerprintIllustrationProps {
  isScanning: boolean;
  quality: number; // 0 - 100
  state: 'idle' | 'scanning' | 'matched' | 'uncertain' | 'nomatch';
  size?: 'normal' | 'large' | 'compact';
}

export const FingerprintIllustration: React.FC<FingerprintIllustrationProps> = ({
  isScanning,
  quality,
  state,
  size = 'normal',
}) => {
  const getStrokeColor = () => {
    switch (state) {
      case 'matched':
        return '#10B981'; // emerald-500
      case 'uncertain':
        return '#F59E0B'; // amber-500
      case 'nomatch':
        return '#EF4444'; // red-500
      case 'scanning':
        return '#34D399'; // emerald-400
      case 'idle':
      default:
        return '#64748B'; // slate-500
    }
  };

  const getContainerGlow = () => {
    switch (state) {
      case 'matched':
        return 'ring-4 ring-emerald-500/40 shadow-xl shadow-emerald-500/20 bg-emerald-950/20';
      case 'uncertain':
        return 'ring-4 ring-amber-500/40 shadow-xl shadow-amber-500/20 bg-amber-950/20';
      case 'nomatch':
        return 'ring-4 ring-red-500/40 shadow-xl shadow-red-500/20 bg-red-950/20';
      case 'scanning':
        return 'ring-4 ring-emerald-400/50 shadow-2xl shadow-emerald-500/30 bg-slate-900';
      case 'idle':
      default:
        return 'border border-slate-700/80 bg-slate-900/60 shadow-lg';
    }
  };

  const dimensionClasses = {
    compact: 'w-24 h-28',
    normal: 'w-44 h-52',
    large: 'w-52 h-60',
  }[size];

  const strokeColor = getStrokeColor();

  return (
    <div
      className={`relative ${dimensionClasses} rounded-3xl flex items-center justify-center transition-all duration-300 overflow-hidden ${getContainerGlow()}`}
    >
      {/* Background Sensor Grid Texture */}
      <div className="absolute inset-0 opacity-15 pointer-events-none">
        <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <pattern id="sensor-grid" width="12" height="12" patternUnits="userSpaceOnUse">
              <path d="M 12 0 L 0 0 0 12" fill="none" stroke="currentColor" strokeWidth="0.5" className="text-slate-400" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#sensor-grid)" />
        </svg>
      </div>

      {/* Target Crosshairs */}
      <div className="absolute top-3 left-3 w-3 h-3 border-t-2 border-l-2 border-slate-600/70 rounded-tl-sm pointer-events-none" />
      <div className="absolute top-3 right-3 w-3 h-3 border-t-2 border-r-2 border-slate-600/70 rounded-tr-sm pointer-events-none" />
      <div className="absolute bottom-3 left-3 w-3 h-3 border-b-2 border-l-2 border-slate-600/70 rounded-bl-sm pointer-events-none" />
      <div className="absolute bottom-3 right-3 w-3 h-3 border-b-2 border-r-2 border-slate-600/70 rounded-br-sm pointer-events-none" />

      {/* Detailed Biometric Fingerprint Ridges */}
      <svg
        viewBox="0 0 100 130"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="w-4/5 h-4/5 transition-transform duration-300"
      >
        <g stroke={strokeColor} strokeWidth="2.8" strokeLinecap="round">
          {/* Outer loop 1 */}
          <path d="M 28 85 C 22 75 20 60 25 45 C 32 25 68 25 75 45 C 80 60 78 75 72 85" />
          {/* Outer loop 2 */}
          <path d="M 22 98 C 14 82 12 55 20 38 C 30 15 70 15 80 38 C 88 55 86 82 78 98" />
          {/* Outer loop 3 (Crown) */}
          <path d="M 35 110 C 26 95 24 85 28 70" />
          <path d="M 72 70 C 76 85 74 95 65 110" />

          {/* Core whorl inner loops */}
          <path d="M 36 78 C 32 68 31 52 38 42 C 44 32 56 32 62 42 C 69 52 68 68 64 78" />
          <path d="M 43 72 C 39 63 40 50 45 44 C 48 39 52 39 55 44 C 60 50 61 63 57 72" />
          
          {/* Central delta core */}
          <path d="M 50 50 C 47 55 47 62 50 66" />
          <path d="M 50 68 L 50 82" />

          {/* Lower ridge splits */}
          <path d="M 42 86 C 42 94 40 102 36 108" />
          <path d="M 50 88 C 50 96 52 104 56 112" />
          <path d="M 58 86 C 60 94 62 102 66 108" />
          <path d="M 28 116 C 35 122 45 125 55 125" />
        </g>
      </svg>

      {/* Optical Laser Sweeper Bar */}
      {isScanning && (
        <div className="absolute inset-x-0 h-1.5 bg-gradient-to-r from-transparent via-emerald-400 to-transparent shadow-[0_0_12px_#34d399] animate-laser-sweep pointer-events-none" />
      )}

      {/* Quality Badge Overlay (Bottom Center) */}
      <div className="absolute bottom-2 inset-x-2 flex justify-center pointer-events-none">
        <div className="px-2 py-0.5 rounded-full bg-slate-950/80 border border-slate-700 backdrop-blur-sm flex items-center gap-1.5 text-[10px] font-mono">
          <span className="text-slate-400">QUALITY</span>
          <span
            className={`font-bold ${
              quality >= 85
                ? 'text-emerald-400'
                : quality >= 60
                ? 'text-amber-400'
                : 'text-slate-400'
            }`}
          >
            {quality}%
          </span>
        </div>
      </div>
    </div>
  );
};
