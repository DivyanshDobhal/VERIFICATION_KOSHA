import React, { useState, useMemo } from 'react';
import { useKosha } from '../context/KoshaContext';
import { WorkerCard } from '../components/workers/WorkerCard';
import {
  Search,
  Filter,
  UserPlus,
  ArrowUpDown,
  Building2,
  X,
  Fingerprint,
  Check,
} from 'lucide-react';

export const WorkersScreen: React.FC = () => {
  const { workers, sites, setSelectedWorkerId, setSecondaryScreen } = useKosha();

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSiteFilter, setSelectedSiteFilter] = useState('ALL');
  const [selectedStatusFilter, setSelectedStatusFilter] = useState('ALL');
  const [sortBy, setSortBy] = useState<'id' | 'name' | 'sessions'>('id');
  const [filterDrawerOpen, setFilterDrawerOpen] = useState(false);

  // Filtered & Sorted Workers
  const filteredWorkers = useMemo(() => {
    return workers
      .filter((worker) => {
        const matchesQuery =
          worker.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          worker.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
          worker.department.toLowerCase().includes(searchQuery.toLowerCase());

        const matchesSite =
          selectedSiteFilter === 'ALL' || worker.siteId === selectedSiteFilter;

        const matchesStatus =
          selectedStatusFilter === 'ALL' || worker.status === selectedStatusFilter;

        return matchesQuery && matchesSite && matchesStatus;
      })
      .sort((a, b) => {
        if (sortBy === 'name') return a.name.localeCompare(b.name);
        if (sortBy === 'sessions') return b.sessionsCount - a.sessionsCount;
        return a.id.localeCompare(b.id);
      });
  }, [workers, searchQuery, selectedSiteFilter, selectedStatusFilter, sortBy]);

  return (
    <div className="flex-1 w-full bg-slate-900 text-slate-100 flex flex-col overflow-hidden">
      {/* Search Bar & Filter Strip */}
      <div className="p-4 bg-slate-900/95 border-b border-slate-800/80 space-y-3 shrink-0">
        <div className="flex items-center gap-2">
          {/* Search Input */}
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by Worker ID (WK-...) or Name"
              className="w-full pl-10 pr-9 py-2.5 bg-slate-800 border border-slate-700 rounded-xl text-xs text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500/40 focus:border-emerald-500"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          {/* Filter Drawer Trigger */}
          <button
            onClick={() => setFilterDrawerOpen(true)}
            className={`p-2.5 rounded-xl border flex items-center justify-center transition-colors ${
              selectedSiteFilter !== 'ALL' || selectedStatusFilter !== 'ALL'
                ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40'
                : 'bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-750'
            }`}
            title="Filter Workers"
          >
            <Filter className="w-4 h-4" />
          </button>

          {/* Register Worker Action */}
          <button
            onClick={() => setSecondaryScreen('register-worker')}
            className="p-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold flex items-center justify-center transition-colors shadow-sm"
            title="Register New Worker"
          >
            <UserPlus className="w-4 h-4" />
          </button>
        </div>

        {/* Quick Sorting & Active Filter Pills */}
        <div className="flex items-center justify-between text-xs text-slate-400 pt-0.5">
          <div className="flex items-center gap-1.5 overflow-x-auto no-scrollbar">
            <span className="font-mono text-[11px] text-slate-300">
              {filteredWorkers.length} {filteredWorkers.length === 1 ? 'Worker' : 'Workers'} Listed
            </span>
            {selectedSiteFilter !== 'ALL' && (
              <span className="text-[10px] bg-slate-800 px-2 py-0.5 rounded text-emerald-400 border border-slate-700">
                Site: {selectedSiteFilter}
              </span>
            )}
          </div>

          {/* Sort selector */}
          <div className="flex items-center gap-1 text-[11px]">
            <ArrowUpDown className="w-3 h-3 text-slate-400" />
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="bg-slate-800 text-slate-200 border border-slate-700 rounded-lg px-2 py-1 text-[11px] focus:outline-none"
            >
              <option value="id">Sort: Worker ID</option>
              <option value="name">Sort: Name (A-Z)</option>
              <option value="sessions">Sort: Most Sessions</option>
            </select>
          </div>
        </div>
      </div>

      {/* Workers List Feed */}
      <div className="flex-1 overflow-y-auto no-scrollbar p-4 space-y-3 pb-24">
        {filteredWorkers.length === 0 ? (
          <div className="text-center py-12 px-4 space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-500 mx-auto">
              <Search className="w-6 h-6" />
            </div>
            <h3 className="text-sm font-bold text-white">No Matching Workers</h3>
            <p className="text-xs text-slate-400 max-w-xs mx-auto">
              No worker record matches "{searchQuery}". Register this worker or clear filters.
            </p>
            <button
              onClick={() => {
                setSearchQuery('');
                setSelectedSiteFilter('ALL');
                setSelectedStatusFilter('ALL');
              }}
              className="px-4 py-2 rounded-xl bg-slate-800 text-emerald-400 text-xs font-semibold hover:bg-slate-700"
            >
              Reset Filters
            </button>
          </div>
        ) : (
          filteredWorkers.map((worker) => (
            <WorkerCard
              key={worker.id}
              worker={worker}
              onClick={() => {
                setSelectedWorkerId(worker.id);
                setSecondaryScreen('worker-detail');
              }}
            />
          ))
        )}
      </div>

      {/* Filter Bottom Sheet Modal */}
      {filterDrawerOpen && (
        <div className="absolute inset-0 bg-black/60 backdrop-blur-sm z-50 flex flex-col justify-end animate-in fade-in duration-150">
          <div className="bg-slate-900 border-t border-slate-700 rounded-t-3xl p-5 space-y-4 max-h-[80%] overflow-y-auto">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800">
              <h3 className="font-bold text-sm text-white">Filter Directory</h3>
              <button
                onClick={() => setFilterDrawerOpen(false)}
                className="w-8 h-8 rounded-full bg-slate-800 text-slate-300 flex items-center justify-center"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Site Filter */}
            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-2">
                Construction Site
              </label>
              <div className="space-y-1.5">
                <button
                  onClick={() => setSelectedSiteFilter('ALL')}
                  className={`w-full text-left px-3 py-2 rounded-xl text-xs flex items-center justify-between ${
                    selectedSiteFilter === 'ALL'
                      ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-semibold'
                      : 'bg-slate-800 text-slate-300'
                  }`}
                >
                  <span>All Sites ({workers.length})</span>
                  {selectedSiteFilter === 'ALL' && <Check className="w-4 h-4 text-emerald-400" />}
                </button>
                {sites.map((site) => (
                  <button
                    key={site.id}
                    onClick={() => setSelectedSiteFilter(site.id)}
                    className={`w-full text-left px-3 py-2 rounded-xl text-xs flex items-center justify-between ${
                      selectedSiteFilter === site.id
                        ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-semibold'
                        : 'bg-slate-800 text-slate-300'
                    }`}
                  >
                    <span>{site.name}</span>
                    {selectedSiteFilter === site.id && <Check className="w-4 h-4 text-emerald-400" />}
                  </button>
                ))}
              </div>
            </div>

            {/* Status Filter */}
            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-2">
                Worker Status
              </label>
              <div className="grid grid-cols-3 gap-2">
                {['ALL', 'Active', 'Under Review'].map((st) => (
                  <button
                    key={st}
                    onClick={() => setSelectedStatusFilter(st)}
                    className={`py-2 px-2 rounded-xl text-xs font-medium text-center ${
                      selectedStatusFilter === st
                        ? 'bg-emerald-500 text-slate-950 font-bold'
                        : 'bg-slate-800 text-slate-300'
                    }`}
                  >
                    {st}
                  </button>
                ))}
              </div>
            </div>

            <button
              onClick={() => setFilterDrawerOpen(false)}
              className="w-full py-3 rounded-xl bg-emerald-500 text-slate-950 font-bold text-xs"
            >
              Apply Filters
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
