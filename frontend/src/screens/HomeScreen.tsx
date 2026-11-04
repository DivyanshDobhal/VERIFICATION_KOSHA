import React from 'react';
import { useKosha } from '../context/KoshaContext';
import {
  Users,
  Clock,
  UserPlus,
  Repeat,
  Fingerprint,
  AlertTriangle,
  ArrowRight,
  TrendingUp,
  ShieldCheck,
  Building2,
  Calendar,
} from 'lucide-react';
import { WorkerCard } from '../components/workers/WorkerCard';
import { SessionCard } from '../components/sessions/SessionCard';

export const HomeScreen: React.FC = () => {
  const {
    operator,
    activeSite,
    workers,
    sessions,
    reviews,
    setCurrentTab,
    setSecondaryScreen,
    setSelectedWorkerId,
  } = useKosha();

  // Metrics
  const totalUniqueWorkers = workers.length;
  const todaySessionsCount = sessions.length;
  const pendingReviewsCount = reviews.filter((r) => r.status === 'Pending Review').length;
  const newRegistrationsCount = workers.filter(
    (w) => w.registrationDate === '2026-11-03' || w.sessionsCount <= 1
  ).length;

  const returningWorkersRatio = Math.round(
    ((workers.filter((w) => w.sessionsCount > 1).length) / (workers.length || 1)) * 100
  );

  const recentWorkers = workers.slice(0, 3);
  const recentSessions = sessions.slice(0, 3);

  return (
    <div className="flex-1 w-full bg-slate-900 text-slate-100 overflow-y-auto no-scrollbar p-4 space-y-5 pb-20">
      {/* Operator Welcome Banner */}
      <div className="bg-gradient-to-br from-slate-800 to-slate-800/60 border border-slate-700/80 rounded-3xl p-4 shadow-lg">
        <div className="flex items-start justify-between">
          <div>
            <span className="text-[11px] font-mono uppercase tracking-wider text-emerald-400 font-semibold">
              Biometric Field Terminal
            </span>
            <h2 className="text-lg font-bold text-white mt-0.5">
              Welcome, {operator.name}
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Badge: <span className="text-slate-200 font-mono">{operator.badgeNumber}</span> · {operator.role}
            </p>
          </div>

          <div className="w-10 h-10 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shrink-0">
            <Building2 className="w-5 h-5" />
          </div>
        </div>

        {/* Current Site Quick Ribbon */}
        <div className="mt-3.5 pt-3 border-t border-slate-700/60 flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-slate-300 font-medium">Assigned: {activeSite.name}</span>
          </div>
          <span className="font-mono text-emerald-400 font-semibold">{activeSite.code}</span>
        </div>
      </div>

      {/* Pending Recognition Review Warning Banner (if any) */}
      {pendingReviewsCount > 0 && (
        <div
          onClick={() => setSecondaryScreen('recognition-review')}
          className="w-full bg-amber-500/10 hover:bg-amber-500/15 border border-amber-500/30 rounded-2xl p-3 flex items-center justify-between text-xs cursor-pointer transition-colors"
        >
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center shrink-0">
              <AlertTriangle className="w-4 h-4" />
            </div>
            <div>
              <span className="font-semibold text-amber-300">
                {pendingReviewsCount} Ambiguous Scans Pending
              </span>
              <p className="text-[11px] text-amber-400/80 mt-0.5">
                Manual identity verification required by supervisor
              </p>
            </div>
          </div>
          <div className="flex items-center gap-1 text-amber-300 font-medium">
            <span>Review</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </div>
        </div>
      )}

      {/* Quick Action Bar */}
      <div className="grid grid-cols-2 gap-2.5">
        <button
          onClick={() => setCurrentTab('recognize')}
          className="p-3.5 rounded-2xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs flex items-center gap-2.5 shadow-lg shadow-emerald-500/20 transition-all active:scale-[0.98]"
        >
          <div className="w-8 h-8 rounded-xl bg-slate-950/20 flex items-center justify-center text-slate-950">
            <Fingerprint className="w-5 h-5 stroke-[2.2]" />
          </div>
          <div className="text-left">
            <div className="text-sm font-bold leading-tight">Scan & Recognize</div>
            <div className="text-[10px] text-emerald-950/80 font-normal">Check-in identity</div>
          </div>
        </button>

        <button
          onClick={() => setSecondaryScreen('register-worker')}
          className="p-3.5 rounded-2xl bg-slate-800 hover:bg-slate-750 border border-slate-700 text-white font-semibold text-xs flex items-center gap-2.5 transition-all active:scale-[0.98]"
        >
          <div className="w-8 h-8 rounded-xl bg-blue-500/20 text-blue-400 flex items-center justify-center">
            <UserPlus className="w-5 h-5" />
          </div>
          <div className="text-left">
            <div className="text-sm font-bold leading-tight">Register Worker</div>
            <div className="text-[10px] text-slate-400 font-normal">4-Step Enrollment</div>
          </div>
        </button>
      </div>

      {/* Statistics 2x2 Grid */}
      <div>
        <div className="flex items-center justify-between mb-2 px-1">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
            Shift & Identity KPIs
          </span>
          <span className="text-[11px] text-emerald-400 font-medium flex items-center gap-1">
            <TrendingUp className="w-3 h-3" />
            <span>0 Duplicate Registrations</span>
          </span>
        </div>

        <div className="grid grid-cols-2 gap-3">
          {/* Total Unique Workers */}
          <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-3.5">
            <div className="flex items-center justify-between text-slate-400 mb-1">
              <span className="text-xs font-medium">Unique Workers</span>
              <Users className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-2xl font-bold font-mono text-white">
              {totalUniqueWorkers}
            </div>
            <div className="text-[10px] text-slate-400 mt-1 flex items-center gap-1">
              <ShieldCheck className="w-3 h-3 text-emerald-400" />
              <span>Permanent IDs active</span>
            </div>
          </div>

          {/* Today's Recording Sessions */}
          <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-3.5">
            <div className="flex items-center justify-between text-slate-400 mb-1">
              <span className="text-xs font-medium">Today's Sessions</span>
              <Clock className="w-4 h-4 text-blue-400" />
            </div>
            <div className="text-2xl font-bold font-mono text-white">
              {todaySessionsCount}
            </div>
            <div className="text-[10px] text-slate-400 mt-1">
              <span>Shift check-ins logged</span>
            </div>
          </div>

          {/* Returning Workers Ratio */}
          <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-3.5">
            <div className="flex items-center justify-between text-slate-400 mb-1">
              <span className="text-xs font-medium">Returning Workers</span>
              <Repeat className="w-4 h-4 text-teal-400" />
            </div>
            <div className="text-2xl font-bold font-mono text-white">
              {returningWorkersRatio}%
            </div>
            <div className="text-[10px] text-slate-400 mt-1">
              <span>Re-checkins to same ID</span>
            </div>
          </div>

          {/* New Registrations */}
          <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-3.5">
            <div className="flex items-center justify-between text-slate-400 mb-1">
              <span className="text-xs font-medium">New Enrolled</span>
              <UserPlus className="w-4 h-4 text-purple-400" />
            </div>
            <div className="text-2xl font-bold font-mono text-white">
              {newRegistrationsCount}
            </div>
            <div className="text-[10px] text-slate-400 mt-1">
              <span>Biometric templates stored</span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Recording Sessions List */}
      <div>
        <div className="flex items-center justify-between mb-2.5 px-1">
          <div className="flex items-center gap-1.5">
            <Clock className="w-4 h-4 text-blue-400" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
              Recent Recording Sessions
            </h3>
          </div>
          <button
            onClick={() => setCurrentTab('sessions')}
            className="text-[11px] font-semibold text-emerald-400 hover:text-emerald-300 flex items-center gap-1"
          >
            <span>View All</span>
            <ArrowRight className="w-3 h-3" />
          </button>
        </div>

        <div className="space-y-2">
          {recentSessions.map((session) => (
            <SessionCard
              key={session.id}
              session={session}
              onClick={() => {
                setSelectedWorkerId(session.workerId);
                setSecondaryScreen('worker-detail');
              }}
            />
          ))}
        </div>
      </div>

      {/* Recent Registered Workers */}
      <div>
        <div className="flex items-center justify-between mb-2.5 px-1">
          <div className="flex items-center gap-1.5">
            <Users className="w-4 h-4 text-emerald-400" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
              Recent Worker Registrations
            </h3>
          </div>
          <button
            onClick={() => setCurrentTab('workers')}
            className="text-[11px] font-semibold text-emerald-400 hover:text-emerald-300 flex items-center gap-1"
          >
            <span>Directory</span>
            <ArrowRight className="w-3 h-3" />
          </button>
        </div>

        <div className="space-y-2">
          {recentWorkers.map((worker) => (
            <WorkerCard
              key={worker.id}
              worker={worker}
              onClick={() => {
                setSelectedWorkerId(worker.id);
                setSecondaryScreen('worker-detail');
              }}
            />
          ))}
        </div>
      </div>

      {/* Multi-Site Deployment Snapshot */}
      <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-4">
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-300">
            Workforce Sites Overview
          </span>
          <button
            onClick={() => setSecondaryScreen('sites')}
            className="text-[11px] text-emerald-400 font-semibold hover:underline"
          >
            Manage Sites
          </button>
        </div>

        <div className="space-y-2.5">
          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400" />
              <span className="text-slate-300">Metro Line 4 Underground</span>
            </div>
            <span className="font-mono font-semibold text-white">184 workers</span>
          </div>

          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-blue-400" />
              <span className="text-slate-300">Terminal 3 Cargo & Logistics</span>
            </div>
            <span className="font-mono font-semibold text-white">112 workers</span>
          </div>

          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-purple-400" />
              <span className="text-slate-300">Harbor Rail Freight Flyover</span>
            </div>
            <span className="font-mono font-semibold text-white">95 workers</span>
          </div>
        </div>
      </div>
    </div>
  );
};
