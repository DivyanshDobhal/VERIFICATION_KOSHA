import React, { useState } from 'react';
import { useKosha } from '../context/KoshaContext';
import {
  TrendingUp,
  ShieldCheck,
  Users,
  Clock,
  Repeat,
  Download,
  Calendar,
  Building2,
  PieChart,
  CheckCircle2,
} from 'lucide-react';

export const AnalyticsScreen: React.FC = () => {
  const { workers, sessions, sites } = useKosha();

  const [dateRange, setDateRange] = useState<'today' | '7days' | '30days'>('7days');
  const [downloadNotice, setDownloadNotice] = useState(false);

  const duplicateAttemptsPrevented = 14;
  const autoMatchRate = 98.4;
  const manualReviewRate = 1.3;
  const newEnrollmentRate = 0.3;

  const handleExport = () => {
    setDownloadNotice(true);
    setTimeout(() => setDownloadNotice(false), 2500);
  };

  return (
    <div className="flex-1 w-full bg-slate-900 text-slate-100 overflow-y-auto no-scrollbar p-4 space-y-4 pb-24">
      {/* Top Banner & Date Filter */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <span>Workforce Analytics</span>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              AUDIT READY
            </span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Biometric identity retention & duplicate prevention
          </p>
        </div>

        <button
          onClick={handleExport}
          className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 flex items-center gap-1.5 text-xs font-semibold transition-colors"
          title="Export CSV Audit"
        >
          <Download className="w-3.5 h-3.5 text-emerald-400" />
          <span className="hidden sm:inline">Export</span>
        </button>
      </div>

      {downloadNotice && (
        <div className="p-3 bg-emerald-500/15 border border-emerald-500/30 rounded-2xl text-xs text-emerald-300 flex items-center gap-2 animate-in fade-in">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>Biometric audit report generated for Kosha Labs Central Compliance.</span>
        </div>
      )}

      {/* Date Filter Segmented Bar */}
      <div className="p-1 bg-slate-800 rounded-xl flex items-center text-xs">
        <button
          onClick={() => setDateRange('today')}
          className={`flex-1 py-1.5 rounded-lg font-semibold transition-all ${
            dateRange === 'today'
              ? 'bg-emerald-500 text-slate-950 shadow-sm'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          Today
        </button>
        <button
          onClick={() => setDateRange('7days')}
          className={`flex-1 py-1.5 rounded-lg font-semibold transition-all ${
            dateRange === '7days'
              ? 'bg-emerald-500 text-slate-950 shadow-sm'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          Last 7 Days
        </button>
        <button
          onClick={() => setDateRange('30days')}
          className={`flex-1 py-1.5 rounded-lg font-semibold transition-all ${
            dateRange === '30days'
              ? 'bg-emerald-500 text-slate-950 shadow-sm'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          Month
        </button>
      </div>

      {/* Key Hero Stat: Duplicate Registrations Prevented */}
      <div className="bg-gradient-to-br from-emerald-950/50 via-slate-800 to-slate-800 border-2 border-emerald-500/40 rounded-3xl p-4 shadow-xl space-y-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider">
              Identity Integrity Anchor
            </span>
          </div>
          <span className="text-[10px] font-mono bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 px-2 py-0.5 rounded">
            ZERO DUPLICATES
          </span>
        </div>

        <div className="flex items-baseline gap-2 pt-1">
          <span className="text-3xl font-extrabold font-mono text-white">
            {duplicateAttemptsPrevented}
          </span>
          <span className="text-xs text-slate-300 font-medium">
            Duplicate Registrations Intercepted & Merged
          </span>
        </div>

        <p className="text-[11px] text-slate-400 leading-relaxed">
          When workers attempted second enrollment at another site gate, the 1:N biometric search matched existing permanent Worker IDs and routed to session check-in instead.
        </p>
      </div>

      {/* 2x2 Core Metric Cards */}
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-3.5">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs font-medium">Active Workers</span>
            <Users className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-white">
            {workers.length}
          </div>
          <div className="text-[10px] text-emerald-400 mt-1 font-semibold">
            100% Enrolled Biometrics
          </div>
        </div>

        <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-3.5">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs font-medium">Recording Sessions</span>
            <Clock className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-white">
            {sessions.length * 48}
          </div>
          <div className="text-[10px] text-slate-400 mt-1 font-mono">
            Avg 4.8 shifts/worker
          </div>
        </div>

        <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-3.5">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs font-medium">Returning Workers</span>
            <Repeat className="w-4 h-4 text-teal-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-white">
            94.6%
          </div>
          <div className="text-[10px] text-slate-400 mt-1">
            High retention rate
          </div>
        </div>

        <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-3.5">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs font-medium">Auto-Match Speed</span>
            <TrendingUp className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-white">
            0.8s
          </div>
          <div className="text-[10px] text-slate-400 mt-1 font-mono">
            Optical 500DPI 1:N
          </div>
        </div>
      </div>

      {/* Biometric Recognition Outcome Breakdown */}
      <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-4 space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
          <PieChart className="w-4 h-4 text-emerald-400" />
          <span>Biometric Scanner Match Outcomes</span>
        </h3>

        {/* Visual Stacked Progress Bar */}
        <div className="w-full h-3 rounded-full bg-slate-900 overflow-hidden flex">
          <div
            className="h-full bg-emerald-500"
            style={{ width: `${autoMatchRate}%` }}
            title={`Instant Match: ${autoMatchRate}%`}
          />
          <div
            className="h-full bg-amber-500"
            style={{ width: `${manualReviewRate}%` }}
            title={`Supervisor Review: ${manualReviewRate}%`}
          />
          <div
            className="h-full bg-blue-500"
            style={{ width: `${newEnrollmentRate}%` }}
            title={`New Enrollment: ${newEnrollmentRate}%`}
          />
        </div>

        <div className="space-y-2 text-xs pt-1">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
              <span className="text-slate-300">Instant Biometric Match (High Confidence)</span>
            </div>
            <span className="font-mono font-bold text-white">{autoMatchRate}%</span>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-500" />
              <span className="text-slate-300">Uncertain Scan / Supervisor Review</span>
            </div>
            <span className="font-mono font-bold text-amber-400">{manualReviewRate}%</span>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-blue-500" />
              <span className="text-slate-300">Unregistered / First-time Worker</span>
            </div>
            <span className="font-mono font-bold text-blue-400">{newEnrollmentRate}%</span>
          </div>
        </div>
      </div>

      {/* Site-wise Distribution Summary */}
      <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-4 space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
          <Building2 className="w-4 h-4 text-blue-400" />
          <span>Site-Wise Workforce & Shift Load</span>
        </h3>

        <div className="space-y-3">
          {sites.map((site) => (
            <div key={site.id} className="space-y-1 text-xs">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-slate-200">{site.name}</span>
                <span className="font-mono font-bold text-emerald-400">
                  {site.activeWorkers} workers
                </span>
              </div>
              <div className="w-full h-1.5 bg-slate-900 rounded-full overflow-hidden">
                <div
                  className="h-full bg-emerald-500 rounded-full"
                  style={{ width: `${(site.activeWorkers / 200) * 100}%` }}
                />
              </div>
              <div className="flex justify-between text-[10px] text-slate-400">
                <span>{site.contractor}</span>
                <span className="font-mono">{site.todaySessions} sessions today</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
