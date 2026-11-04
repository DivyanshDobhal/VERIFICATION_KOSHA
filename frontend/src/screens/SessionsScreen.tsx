import React, { useState, useMemo } from 'react';
import { useKosha } from '../context/KoshaContext';
import { SessionCard } from '../components/sessions/SessionCard';
import { Search, Filter, Clock, Calendar, X, Building2, Plus } from 'lucide-react';

export const SessionsScreen: React.FC = () => {
  const {
    sessions,
    sites,
    setSelectedWorkerId,
    setSecondaryScreen,
  } = useKosha();

  const [activeTab, setActiveTab] = useState<'today' | 'all'>('today');
  const [searchQuery, setSearchQuery] = useState('');
  const [siteFilter, setSiteFilter] = useState('ALL');

  // Filtered Sessions
  const filteredSessions = useMemo(() => {
    return sessions.filter((s) => {
      const matchesSearch =
        s.workerId.toLowerCase().includes(searchQuery.toLowerCase()) ||
        s.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
        s.workerName.toLowerCase().includes(searchQuery.toLowerCase());

      const matchesSite = siteFilter === 'ALL' || s.siteId === siteFilter;

      const matchesToday =
        activeTab === 'all' ||
        s.timestamp.includes('Today') ||
        s.timestamp.includes('2026-11-03');

      return matchesSearch && matchesSite && matchesToday;
    });
  }, [sessions, searchQuery, siteFilter, activeTab]);

  return (
    <div className="flex-1 w-full bg-slate-900 text-slate-100 flex flex-col overflow-hidden pb-20">
      {/* Top Controls Strip */}
      <div className="p-4 bg-slate-900/95 border-b border-slate-800 space-y-3 shrink-0">
        {/* Today vs All Segmented Control */}
        <div className="p-1 bg-slate-800 rounded-xl flex items-center">
          <button
            onClick={() => setActiveTab('today')}
            className={`flex-1 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'today'
                ? 'bg-emerald-500 text-slate-950 shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Today's Sessions ({sessions.filter((s) => s.timestamp.includes('2026-11-03') || s.timestamp.includes('Today')).length})
          </button>
          <button
            onClick={() => setActiveTab('all')}
            className={`flex-1 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'all'
                ? 'bg-emerald-500 text-slate-950 shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            All Historical Sessions ({sessions.length})
          </button>
        </div>

        {/* Search & Site Filter */}
        <div className="flex items-center gap-2">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Filter by Worker ID (WK-...) or Session"
              className="w-full pl-9 pr-8 py-2 bg-slate-800 border border-slate-700 rounded-xl text-xs text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500/40"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          <button
            onClick={() => setSecondaryScreen('create-session')}
            className="p-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold flex items-center justify-center transition-colors"
            title="Log New Session"
          >
            <Plus className="w-4 h-4" />
          </button>
        </div>

        {/* Site Quick Filter Bar */}
        <div className="flex items-center gap-1.5 overflow-x-auto no-scrollbar pt-1 text-xs">
          <button
            onClick={() => setSiteFilter('ALL')}
            className={`px-2.5 py-1 rounded-lg font-medium whitespace-nowrap transition-colors ${
              siteFilter === 'ALL'
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                : 'bg-slate-800/80 text-slate-400 border border-slate-700/60'
            }`}
          >
            All Sites
          </button>
          {sites.map((site) => (
            <button
              key={site.id}
              onClick={() => setSiteFilter(site.id)}
              className={`px-2.5 py-1 rounded-lg font-medium whitespace-nowrap transition-colors ${
                siteFilter === site.id
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                  : 'bg-slate-800/80 text-slate-400 border border-slate-700/60'
              }`}
            >
              {site.code}
            </button>
          ))}
        </div>
      </div>

      {/* Sessions Feed */}
      <div className="flex-1 overflow-y-auto no-scrollbar p-4 space-y-3 pb-24">
        {filteredSessions.length === 0 ? (
          <div className="text-center py-12 px-4 space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-500 mx-auto">
              <Clock className="w-6 h-6" />
            </div>
            <h3 className="text-sm font-bold text-white">No Sessions Found</h3>
            <p className="text-xs text-slate-400 max-w-xs mx-auto">
              No recording session matching your filter criteria.
            </p>
          </div>
        ) : (
          filteredSessions.map((session) => (
            <SessionCard
              key={session.id}
              session={session}
              onClick={() => {
                setSelectedWorkerId(session.workerId);
                setSecondaryScreen('worker-detail');
              }}
            />
          ))
        )}
      </div>
    </div>
  );
};
