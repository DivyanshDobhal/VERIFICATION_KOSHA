import React from 'react';
import { Session } from '../../types';
import { Clock, ShieldCheck, MapPin, ChevronRight, Fingerprint } from 'lucide-react';

interface SessionCardProps {
  session: Session;
  onClick?: () => void;
}

export const SessionCard: React.FC<SessionCardProps> = ({ session, onClick }) => {
  return (
    <div
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      className="w-full bg-slate-800/90 hover:bg-slate-800 border border-slate-700/80 rounded-2xl p-3.5 transition-all text-left"
    >
      <div className="flex items-start justify-between gap-2">
        <div>
          {/* Top Identifiers: Session ID + Linked Permanent Worker ID */}
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-mono font-bold text-xs text-white bg-slate-700 px-2 py-0.5 rounded">
              {session.id}
            </span>
            <span className="text-slate-500 text-xs">→</span>
            <span className="font-mono font-bold text-xs text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
              {session.workerId}
            </span>
            <span
              className={`text-[10px] font-medium px-2 py-0.5 rounded-full ${
                session.status === 'Verified & Active'
                  ? 'bg-emerald-500/20 text-emerald-300'
                  : 'bg-blue-500/20 text-blue-300'
              }`}
            >
              {session.status}
            </span>
          </div>

          <h4 className="font-semibold text-sm text-slate-100 mt-1.5">
            {session.workerName}
          </h4>

          <div className="flex items-center gap-2 text-xs text-slate-400 mt-1">
            <span className="font-medium text-slate-300">{session.shift}</span>
          </div>
        </div>

        {onClick && (
          <ChevronRight className="w-4 h-4 text-slate-500 mt-1 shrink-0" />
        )}
      </div>

      {/* Meta Footer */}
      <div className="mt-3 pt-2.5 border-t border-slate-700/60 flex items-center justify-between text-[11px] text-slate-400">
        <div className="flex items-center gap-1.5">
          <MapPin className="w-3.5 h-3.5 text-slate-400" />
          <span className="truncate max-w-[150px]">{session.gate}</span>
        </div>

        <div className="flex items-center gap-1 text-slate-300 font-mono">
          <Clock className="w-3 h-3 text-emerald-400" />
          <span>{session.timestamp}</span>
        </div>
      </div>
    </div>
  );
};
