import React from 'react';
import { ShieldCheck, Cpu, CheckCircle2, AlertTriangle } from 'lucide-react';

interface ScannerStatusIndicatorProps {
  status?: 'ready' | 'busy' | 'calibrating' | 'disconnected';
  onRunDiagnostics?: () => void;
}

export const ScannerStatusIndicator: React.FC<ScannerStatusIndicatorProps> = ({
  status = 'ready',
  onRunDiagnostics,
}) => {
  return (
    <div className="w-full bg-slate-800/80 border border-slate-700/80 rounded-2xl p-3 flex items-center justify-between text-xs">
      <div className="flex items-center gap-2.5">
        <div className="relative">
          <div className="w-7 h-7 rounded-xl bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
            <Cpu className="w-4 h-4" />
          </div>
          <span className="absolute -bottom-0.5 -right-0.5 w-2 h-2 rounded-full bg-emerald-400 ring-2 ring-slate-900" />
        </div>
        <div>
          <div className="flex items-center gap-1.5 font-medium text-slate-200">
            <span>SecuGen Optical 500DPI</span>
            <span className="text-[10px] font-mono px-1 py-0.2 rounded bg-slate-700/80 text-emerald-400">
              READY
            </span>
          </div>
          <div className="text-[11px] text-slate-400 flex items-center gap-2 mt-0.5">
            <span>USB-OTG Attached</span>
            <span aria-hidden="true">·</span>
            <span>Latency: 14ms</span>
          </div>
        </div>
      </div>

      {onRunDiagnostics && (
        <button
          onClick={onRunDiagnostics}
          className="px-2.5 py-1 rounded-lg bg-slate-700 hover:bg-slate-600 text-[11px] font-medium text-slate-200 transition-colors"
        >
          Check Sensor
        </button>
      )}
    </div>
  );
};
