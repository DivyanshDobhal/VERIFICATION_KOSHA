import React from 'react';
import { useKosha } from '../context/KoshaContext';
import { Building2, MapPin, Users, Clock, Check, ChevronRight } from 'lucide-react';

export const SitesScreen: React.FC = () => {
  const { sites, operator, updateActiveSite, setSecondaryScreen } = useKosha();

  return (
    <div className="flex-1 w-full bg-slate-900 text-slate-100 overflow-y-auto no-scrollbar p-4 space-y-4 pb-24">
      <div>
        <h2 className="text-base font-bold text-white flex items-center gap-2">
          <span>Infrastructure Construction Sites</span>
        </h2>
        <p className="text-xs text-slate-400 mt-0.5">
          Select site to switch active field turnstile and check-in roster
        </p>
      </div>

      <div className="space-y-3">
        {sites.map((site) => {
          const isActive = site.id === operator.activeSiteId;
          return (
            <div
              key={site.id}
              onClick={() => updateActiveSite(site.id)}
              role="button"
              tabIndex={0}
              className={`w-full p-4 rounded-3xl border transition-all text-left cursor-pointer ${
                isActive
                  ? 'bg-slate-800/95 border-emerald-500 shadow-xl shadow-emerald-500/10'
                  : 'bg-slate-800/80 border-slate-700/80 hover:bg-slate-800'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div
                    className={`w-11 h-11 rounded-2xl flex items-center justify-center font-bold text-sm ${
                      isActive
                        ? 'bg-emerald-500 text-slate-950'
                        : 'bg-slate-700 text-slate-300'
                    }`}
                  >
                    <Building2 className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono font-bold text-xs text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                        {site.code}
                      </span>
                      {isActive && (
                        <span className="text-[10px] bg-emerald-500/20 text-emerald-300 px-2 py-0.5 rounded-full font-semibold">
                          CURRENTLY ACTIVE
                        </span>
                      )}
                    </div>
                    <h3 className="font-bold text-sm text-white mt-1">
                      {site.name}
                    </h3>
                  </div>
                </div>

                {isActive ? (
                  <Check className="w-5 h-5 text-emerald-400 mt-1" />
                ) : (
                  <ChevronRight className="w-5 h-5 text-slate-500 mt-1" />
                )}
              </div>

              <div className="mt-3 pt-3 border-t border-slate-700/60 flex items-center justify-between text-xs text-slate-400">
                <div className="flex items-center gap-1.5">
                  <MapPin className="w-3.5 h-3.5 text-slate-400" />
                  <span className="truncate max-w-[170px]">{site.location}</span>
                </div>

                <div className="flex items-center gap-3 font-mono">
                  <span className="text-slate-300">{site.activeWorkers} workers</span>
                  <span className="text-emerald-400 font-semibold">{site.todaySessions} today</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
