import React from 'react';
import { Worker } from '../../types';
import { ChevronRight, Fingerprint, Calendar, Clock, ShieldCheck } from 'lucide-react';

interface WorkerCardProps {
  worker: Worker;
  onClick: () => void;
}

export const WorkerCard: React.FC<WorkerCardProps> = ({ worker, onClick }) => {
  return (
    <div
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick();
        }
      }}
      className="w-full bg-slate-800/90 hover:bg-slate-800 border border-slate-700/80 rounded-2xl p-3.5 transition-all active:scale-[0.99] text-left cursor-pointer group"
    >
      <div className="flex items-start justify-between gap-3">
        {/* Left: Avatar + Identification */}
        <div className="flex items-center gap-3 min-w-0">
          <div
            className={`w-11 h-11 rounded-2xl ${worker.avatarColor} text-white font-bold text-sm flex items-center justify-center shrink-0 shadow-md`}
          >
            {worker.name
              .split(' ')
              .map((n) => n[0])
              .slice(0, 2)
              .join('')}
          </div>

          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <span className="font-mono font-bold text-xs text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20">
                {worker.id}
              </span>
              <span
                className={`text-[10px] font-medium px-2 py-0.5 rounded-full ${
                  worker.status === 'Active'
                    ? 'bg-emerald-500/20 text-emerald-300'
                    : worker.status === 'Under Review'
                    ? 'bg-amber-500/20 text-amber-300'
                    : 'bg-slate-700 text-slate-300'
                }`}
              >
                {worker.status}
              </span>
            </div>

            <h3 className="font-semibold text-sm text-slate-100 truncate mt-1 group-hover:text-emerald-300 transition-colors">
              {worker.name}
            </h3>

            <p className="text-xs text-slate-400 truncate mt-0.5">
              {worker.department} · {worker.category}
            </p>
          </div>
        </div>

        {/* Right: Chevron */}
        <ChevronRight className="w-5 h-5 text-slate-500 group-hover:text-slate-300 transition-colors shrink-0 mt-2" />
      </div>

      {/* Footer Metrics Strip */}
      <div className="mt-3 pt-2.5 border-t border-slate-700/60 flex items-center justify-between text-[11px] text-slate-400">
        <div className="flex items-center gap-1.5 text-slate-300">
          <Fingerprint className="w-3.5 h-3.5 text-emerald-400" />
          <span>{worker.enrolledFingers.length} Biometric Templates</span>
        </div>

        <div className="flex items-center gap-1.5 font-mono text-slate-300">
          <Clock className="w-3.5 h-3.5 text-blue-400" />
          <span className="font-semibold text-emerald-400">{worker.sessionsCount}</span>
          <span>sessions</span>
        </div>
      </div>
    </div>
  );
};
