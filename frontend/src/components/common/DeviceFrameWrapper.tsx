import React from 'react';
import { useKosha } from '../../context/KoshaContext';
import { Smartphone, Tablet, Monitor, Sun, Moon, ShieldCheck, Sparkles, Download } from 'lucide-react';
import { DeviceFrameMode } from '../../types';
import { Capacitor } from '@capacitor/core';

interface DeviceFrameWrapperProps {
  children: React.ReactNode;
}

export const DeviceFrameWrapper: React.FC<DeviceFrameWrapperProps> = ({ children }) => {
  const { deviceFrame, setDeviceFrame, isDarkMode, toggleDarkMode, activeSite } = useKosha();
  const isNative = typeof window !== 'undefined' && Capacitor.isNativePlatform();

  // Preset dimensions for testing various mobile device form factors
  const getFrameStyles = (mode: DeviceFrameMode) => {
    if (isNative) {
      return {
        wrapper: 'w-full min-h-screen rounded-none border-none shadow-none',
        island: false,
        type: 'fluid',
      };
    }

    switch (mode) {
      case 'iphone':
        return {
          wrapper: 'max-w-[420px] h-[870px] rounded-[52px] border-[10px] border-slate-800 shadow-2xl shadow-black/60',
          island: true,
          type: 'phone',
        };
      case 'pixel':
        return {
          wrapper: 'max-w-[412px] h-[860px] rounded-[44px] border-[8px] border-slate-700 shadow-2xl shadow-black/50',
          island: false,
          type: 'phone',
        };
      case 'tablet':
        return {
          wrapper: 'max-w-[768px] h-[920px] rounded-[36px] border-[12px] border-slate-800 shadow-2xl shadow-black/60',
          island: false,
          type: 'tablet',
        };
      case 'fluid':
      default:
        return {
          wrapper: 'w-full min-h-screen rounded-none border-none shadow-none',
          island: false,
          type: 'fluid',
        };
    }
  };

  const currentFrame = getFrameStyles(deviceFrame);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center justify-start antialiased selection:bg-emerald-500 selection:text-white">
      {/* Top Testing Controls Bar (Only visible on wide desktop viewports and non-native web) */}
      {!isNative && (
        <aside aria-label="Development testing tools" className="w-full bg-slate-900/90 backdrop-blur-md border-b border-slate-800/80 px-4 py-2.5 flex items-center justify-between text-xs shrink-0 z-50">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
            <span className="font-bold tracking-tight text-white flex items-center gap-1.5">
              <span>KOSHA LABS</span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                MOBILE RUNTIME
              </span>
            </span>
          </div>
          <span className="hidden sm:inline text-slate-500">|</span>
          <span className="hidden sm:inline text-slate-400 font-mono">
            Active Site: <strong className="text-slate-200">{activeSite.code}</strong>
          </span>
        </div>

        {/* Device Switcher, ZIP Download & Theme Control */}
        <div className="flex items-center gap-2">
          {/* Direct ZIP Download button */}
          <a
            href="/kosha-labs-mobile-app.zip"
            download="kosha-labs-mobile-app.zip"
            className="px-2.5 py-1.5 rounded-xl bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-500/40 text-emerald-300 font-semibold flex items-center gap-1.5 transition-colors"
            title="Download complete project source ZIP"
          >
            <Download className="w-3.5 h-3.5 text-emerald-400" />
            <span className="hidden sm:inline">Download ZIP</span>
          </a>

          <div className="bg-slate-800/90 p-1 rounded-xl border border-slate-700 flex items-center gap-1">
            <button
              onClick={() => setDeviceFrame('iphone')}
              title="iPhone 16 Pro (393x852)"
              className={`px-2.5 py-1 rounded-lg font-medium flex items-center gap-1.5 transition-all ${
                deviceFrame === 'iphone'
                  ? 'bg-emerald-500 text-slate-950 shadow-sm font-semibold'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <Smartphone className="w-3.5 h-3.5" />
              <span className="hidden md:inline">iPhone</span>
            </button>

            <button
              onClick={() => setDeviceFrame('pixel')}
              title="Pixel 8 (412x860)"
              className={`px-2.5 py-1 rounded-lg font-medium flex items-center gap-1.5 transition-all ${
                deviceFrame === 'pixel'
                  ? 'bg-emerald-500 text-slate-950 shadow-sm font-semibold'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <Smartphone className="w-3.5 h-3.5" />
              <span className="hidden md:inline">Android</span>
            </button>

            <button
              onClick={() => setDeviceFrame('tablet')}
              title="iPad / Tablet (768x920)"
              className={`px-2.5 py-1 rounded-lg font-medium flex items-center gap-1.5 transition-all ${
                deviceFrame === 'tablet'
                  ? 'bg-emerald-500 text-slate-950 shadow-sm font-semibold'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <Tablet className="w-3.5 h-3.5" />
              <span className="hidden md:inline">Tablet</span>
            </button>

            <button
              onClick={() => setDeviceFrame('fluid')}
              title="Fluid Full Viewport"
              className={`px-2.5 py-1 rounded-lg font-medium flex items-center gap-1.5 transition-all ${
                deviceFrame === 'fluid'
                  ? 'bg-emerald-500 text-slate-950 shadow-sm font-semibold'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <Monitor className="w-3.5 h-3.5" />
              <span className="hidden md:inline">Fluid</span>
            </button>
          </div>

          {/* Theme switch */}
          <button
            onClick={toggleDarkMode}
            title={isDarkMode ? 'Switch to Light Theme' : 'Switch to Dark Theme'}
            className="p-1.5 rounded-xl bg-slate-800 border border-slate-700 text-slate-300 hover:text-white hover:bg-slate-700 transition-colors"
          >
            {isDarkMode ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-blue-400" />}
          </button>
        </div>
      </aside>
      )}

      {/* Device Viewport Canvas */}
      <main className="flex-1 w-full flex items-center justify-center p-0 sm:p-4 overflow-hidden">
        <div
          className={`relative w-full overflow-hidden bg-slate-900 transition-all duration-300 flex flex-col ${currentFrame.wrapper}`}
        >
          {/* Hardware Notch / Dynamic Island Simulator */}
          {currentFrame.island && (
            <div className="absolute top-2 left-1/2 -translate-x-1/2 w-28 h-5 bg-black rounded-full z-50 flex items-center justify-end px-2">
              <div className="w-2.5 h-2.5 rounded-full bg-slate-900/90 border border-slate-800 mr-1" />
              <div className="w-2 h-2 rounded-full bg-blue-950/60" />
            </div>
          )}

          {/* Screen Body */}
          <div className="flex-1 flex flex-col w-full h-full overflow-hidden relative">
            {children}
          </div>

          {/* iOS / Android Home Indicator Bar */}
          {deviceFrame !== 'fluid' && (
            <div className="w-full pb-2 pt-1 flex justify-center bg-transparent z-40 pointer-events-none">
              <div className="w-32 h-1 bg-slate-400/40 rounded-full" />
            </div>
          )}
        </div>
      </main>
    </div>
  );
};
