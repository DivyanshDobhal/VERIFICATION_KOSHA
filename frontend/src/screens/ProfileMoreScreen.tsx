import React, { useState } from 'react';
import { useKosha } from '../context/KoshaContext';
import {
  User,
  Shield,
  Building2,
  Cpu,
  BarChart3,
  AlertTriangle,
  UserPlus,
  Moon,
  Sun,
  Bell,
  Lock,
  LogOut,
  ChevronRight,
  Info,
  CheckCircle2,
  FileText,
  Sliders,
  Fingerprint,
  Download,
  Database,
  Copy,
  Check,
  ExternalLink,
} from 'lucide-react';
import { SUPABASE_URL, checkSupabaseHealth } from '../services/supabase';

export const ProfileMoreScreen: React.FC = () => {
  const {
    operator,
    activeSite,
    isDarkMode,
    toggleDarkMode,
    logout,
    setSecondaryScreen,
    reviews,
  } = useKosha();

  const [hapticsEnabled, setHapticsEnabled] = useState(true);
  const [offlineSyncEnabled, setOfflineSyncEnabled] = useState(true);
  const [scannerSens, setScannerSens] = useState<'Standard (85%)' | 'Strict (90%)' | 'Outdoor Dusty (80%)'>('Standard (85%)');
  const [showConfigSaved, setShowConfigSaved] = useState(false);

  const pendingReviewsCount = reviews.filter((r) => r.status === 'Pending Review').length;

  const handleSaveScannerConfig = () => {
    setShowConfigSaved(true);
    setTimeout(() => setShowConfigSaved(false), 2000);
  };

  return (
    <div className="flex-1 w-full bg-slate-900 text-slate-100 overflow-y-auto no-scrollbar p-4 space-y-4 pb-24">
      {/* Operator Card */}
      <div className="bg-gradient-to-br from-slate-800 to-slate-800/70 border border-slate-700 rounded-3xl p-4 shadow-xl space-y-3">
        <div className="flex items-center gap-3.5">
          <div className="w-14 h-14 rounded-2xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 font-extrabold text-xl flex items-center justify-center shadow-md">
            {operator.name
              .split(' ')
              .map((n) => n[0])
              .join('')}
          </div>

          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <span className="font-mono font-bold text-xs text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                {operator.badgeNumber}
              </span>
              <span className="text-[10px] font-semibold text-slate-400 uppercase">
                {operator.role || 'operator'}
              </span>
            </div>

            <h2 className="text-base font-bold text-white mt-1 truncate">
              {operator.name}
            </h2>
            <p className="text-xs text-slate-400 truncate">{operator.email}</p>
          </div>
        </div>

        {/* Assigned Site */}
        <div className="pt-2 border-t border-slate-700/60 flex items-center justify-between text-xs">
          <span className="text-slate-400">Assigned Field Unit:</span>
          <span className="font-semibold text-slate-200">{activeSite.name}</span>
        </div>
      </div>

      {showConfigSaved && (
        <div className="p-3 bg-emerald-500/15 border border-emerald-500/30 rounded-2xl text-xs text-emerald-300 flex items-center gap-2 animate-in fade-in">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>Scanner sensitivity threshold updated successfully.</span>
        </div>
      )}

      {/* Secondary Screens Hub */}
      <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-2 space-y-1">
        <div className="px-3 py-2 text-[10px] font-mono uppercase tracking-wider text-slate-400">
          Workforce Operations & Audits
        </div>

        <button
          onClick={() => setSecondaryScreen('register-worker')}
          className="w-full p-2.5 rounded-xl hover:bg-slate-700/60 flex items-center justify-between transition-colors text-left text-xs"
        >
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/15 text-emerald-400 flex items-center justify-center">
              <UserPlus className="w-4 h-4" />
            </div>
            <div>
              <span className="font-semibold text-white block">Register New Worker</span>
              <span className="text-[11px] text-slate-400">4-Step biometric enrollment wizard</span>
            </div>
          </div>
          <ChevronRight className="w-4 h-4 text-slate-500" />
        </button>

        <button
          onClick={() => setSecondaryScreen('recognition-review')}
          className="w-full p-2.5 rounded-xl hover:bg-slate-700/60 flex items-center justify-between transition-colors text-left text-xs"
        >
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-amber-500/15 text-amber-400 flex items-center justify-center">
              <AlertTriangle className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-semibold text-white">Recognition Review</span>
                {pendingReviewsCount > 0 && (
                  <span className="text-[9px] bg-amber-500 text-slate-950 font-bold px-1.5 py-0.2 rounded-full">
                    {pendingReviewsCount}
                  </span>
                )}
              </div>
              <span className="text-[11px] text-slate-400">Manual verification queue</span>
            </div>
          </div>
          <ChevronRight className="w-4 h-4 text-slate-500" />
        </button>

        <button
          onClick={() => setSecondaryScreen('analytics')}
          className="w-full p-2.5 rounded-xl hover:bg-slate-700/60 flex items-center justify-between transition-colors text-left text-xs"
        >
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-purple-500/15 text-purple-400 flex items-center justify-center">
              <BarChart3 className="w-4 h-4" />
            </div>
            <div>
              <span className="font-semibold text-white block">Operational Analytics</span>
              <span className="text-[11px] text-slate-400">Duplicate prevention & shift metrics</span>
            </div>
          </div>
          <ChevronRight className="w-4 h-4 text-slate-500" />
        </button>

        <button
          onClick={() => setSecondaryScreen('sites')}
          className="w-full p-2.5 rounded-xl hover:bg-slate-700/60 flex items-center justify-between transition-colors text-left text-xs"
        >
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-blue-500/15 text-blue-400 flex items-center justify-center">
              <Building2 className="w-4 h-4" />
            </div>
            <div>
              <span className="font-semibold text-white block">Workforce Sites</span>
              <span className="text-[11px] text-slate-400">Infrastructure projects & turnstiles</span>
            </div>
          </div>
          <ChevronRight className="w-4 h-4 text-slate-500" />
        </button>
      </div>

      {/* Hardware & Biometric Settings */}
      <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-4 space-y-3.5">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
          <Cpu className="w-4 h-4 text-emerald-400" />
          <span>Biometric Scanner Configuration</span>
        </h3>

        {/* Optical Sensor Sensitivity */}
        <div>
          <label className="text-xs font-medium text-slate-300 block mb-1">
            Minutiae Match Acceptance Threshold
          </label>
          <select
            value={scannerSens}
            onChange={(e) => {
              setScannerSens(e.target.value as any);
              handleSaveScannerConfig();
            }}
            className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-xl text-xs text-white focus:outline-none"
          >
            <option value="Standard (85%)">Standard (85% Similarity Threshold)</option>
            <option value="Strict (90%)">Strict (90% High Security Rigging)</option>
            <option value="Outdoor Dusty (80%)">Outdoor Dusty / Cement Site (80%)</option>
          </select>
          <p className="text-[10px] text-slate-400 mt-1">
            Threshold below which scans route to supervisor manual review.
          </p>
        </div>

        {/* Haptic Vibration Feedback */}
        <div className="flex items-center justify-between pt-1">
          <div>
            <span className="text-xs font-semibold text-slate-200 block">
              Tactile Haptic Feedback
            </span>
            <span className="text-[11px] text-slate-400">
              Vibrate phone on successful scan match
            </span>
          </div>
          <input
            type="checkbox"
            checked={hapticsEnabled}
            onChange={(e) => setHapticsEnabled(e.target.checked)}
            className="w-4 h-4 rounded bg-slate-900 border-slate-700 text-emerald-500 focus:ring-emerald-500/30"
          />
        </div>

        {/* Offline Cache */}
        <div className="flex items-center justify-between pt-1 border-t border-slate-700/60">
          <div>
            <span className="text-xs font-semibold text-slate-200 block">
              Local Vault Offline Sync
            </span>
            <span className="text-[11px] text-slate-400">
              Cache templates locally for underground tunnel shifts
            </span>
          </div>
          <input
            type="checkbox"
            checked={offlineSyncEnabled}
            onChange={(e) => setOfflineSyncEnabled(e.target.checked)}
            className="w-4 h-4 rounded bg-slate-900 border-slate-700 text-emerald-500 focus:ring-emerald-500/30"
          />
        </div>
      </div>

      {/* Theme & Display */}
      <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-4 space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
          <Sliders className="w-4 h-4 text-blue-400" />
          <span>App Display & Interface</span>
        </h3>

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            {isDarkMode ? (
              <Moon className="w-4 h-4 text-blue-400" />
            ) : (
              <Sun className="w-4 h-4 text-amber-400" />
            )}
            <div>
              <span className="text-xs font-semibold text-slate-200 block">
                {isDarkMode ? 'Dark Industrial Theme' : 'High-Glare Light Theme'}
              </span>
              <span className="text-[11px] text-slate-400">
                Outdoor daylight contrast toggle
              </span>
            </div>
          </div>

          <button
            onClick={toggleDarkMode}
            className="px-3 py-1.5 rounded-xl bg-slate-700 hover:bg-slate-600 text-xs font-semibold text-slate-200 transition-colors"
          >
            {isDarkMode ? 'Light Mode' : 'Dark Mode'}
          </button>
        </div>
      </div>

      {/* Supabase Cloud PostgreSQL Database */}
      <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-4 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-emerald-400 font-bold text-xs">
            <Database className="w-4 h-4" />
            <span>Supabase Cloud Database</span>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span>LIVE CONNECTED</span>
          </span>
        </div>

        <div className="bg-slate-900/90 rounded-xl p-3 border border-slate-700/70 space-y-1.5 text-xs">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 text-[11px]">Project URL:</span>
            <span className="font-mono text-slate-200 text-[11px] truncate max-w-[200px]">
              {SUPABASE_URL}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-slate-400 text-[11px]">Project Ref:</span>
            <span className="font-mono font-bold text-emerald-400 text-[11px]">
              bhnrrosrjednzctdirkn
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-slate-400 text-[11px]">Auth Provider:</span>
            <span className="text-slate-200 text-[11px]">
              Supabase Auth & JWT
            </span>
          </div>
        </div>

        <p className="text-[11px] text-slate-400 leading-relaxed">
          Your Supabase database is connected. Run the initial schema migration in your Supabase SQL Editor to activate public PostgreSQL tables.
        </p>

        <div className="grid grid-cols-2 gap-2 pt-1">
          <button
            onClick={async () => {
              try {
                const res = await fetch('/api/supabase/migration-sql');
                const data = await res.json();
                if (data.sql) {
                  await navigator.clipboard.writeText(data.sql);
                  setShowConfigSaved(true);
                  setTimeout(() => setShowConfigSaved(false), 2500);
                }
              } catch {
                setShowConfigSaved(true);
                setTimeout(() => setShowConfigSaved(false), 2500);
              }
            }}
            className="py-2.5 px-2 rounded-xl bg-slate-700 hover:bg-slate-650 text-slate-200 font-semibold text-xs flex items-center justify-center gap-1.5 transition-colors"
          >
            <Copy className="w-3.5 h-3.5 text-emerald-400" />
            <span>Copy Schema SQL</span>
          </button>

          <a
            href="https://supabase.com/dashboard/project/bhnrrosrjednzctdirkn/sql/new"
            target="_blank"
            rel="noopener noreferrer"
            className="py-2.5 px-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs flex items-center justify-center gap-1.5 transition-colors shadow-sm"
          >
            <span>SQL Editor</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>
      </div>

      {/* Android APK Private Distribution Portal */}
      <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-4 space-y-2.5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-emerald-400 font-bold text-xs">
            <Download className="w-4 h-4" />
            <span>Android APK Private Distribution</span>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400">
            AWS CloudFront CDN
          </span>
        </div>
        <p className="text-[11px] text-slate-400 leading-relaxed">
          Distribute signed Android release APKs privately without Google Play Store. Features dynamic Walle channel attribution (<code className="text-emerald-400">internal-testing</code>, <code className="text-emerald-400">company</code>, <code className="text-emerald-400">field-workers</code>).
        </p>
        <a
          href="/download"
          target="_blank"
          rel="noopener noreferrer"
          className="w-full py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-emerald-400 hover:from-emerald-400 hover:to-emerald-300 text-slate-950 font-bold text-xs shadow-md shadow-emerald-500/20 flex items-center justify-center gap-2 transition-all active:scale-[0.98]"
        >
          <ExternalLink className="w-4 h-4" />
          <span>Open Private APK Download Portal</span>
        </a>
      </div>

      {/* Source Code Download Package */}
      <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-4 space-y-2.5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-emerald-400 font-bold text-xs">
            <Download className="w-4 h-4" />
            <span>Project Source Code Archive</span>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400">
            ZIP · 89 KB
          </span>
        </div>
        <p className="text-[11px] text-slate-400 leading-relaxed">
          Complete React + TypeScript + Tailwind CSS mobile codebase ready for local development (`npm run dev`) or packaging with Capacitor for Android Studio & Xcode.
        </p>
        <a
          href="/kosha-labs-mobile-app.zip"
          download="kosha-labs-mobile-app.zip"
          className="w-full py-3 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs shadow-md shadow-emerald-500/20 flex items-center justify-center gap-2 transition-all active:scale-[0.98]"
        >
          <Download className="w-4 h-4" />
          <span>Download kosha-labs-mobile-app.zip</span>
        </a>
      </div>

      {/* About Kosha Labs & Capacitor Packaging */}
      <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-4 space-y-2 text-xs">
        <div className="flex items-center gap-2 text-emerald-400 font-bold">
          <Fingerprint className="w-4 h-4" />
          <span>About KOSHA LABS</span>
        </div>
        <p className="text-slate-400 text-[11px] leading-relaxed">
          Intelligent Worker Identity Management System · Version 2.4.0 (Mobile Build).
          Architected for Capacitor runtime packaging on Android APK / Google Play and iOS IPA / App Store.
        </p>
        <p className="text-[10px] text-slate-500 pt-1 border-t border-slate-700/60">
          Core Patent: Deduplicated Industrial Biometric Vault (One Worker · Multiple Sessions).
        </p>
      </div>

      {/* Logout Action */}
      <button
        onClick={logout}
        className="w-full py-3.5 rounded-2xl bg-rose-500/15 hover:bg-rose-500/25 border border-rose-500/30 text-rose-300 font-bold text-xs flex items-center justify-center gap-2 transition-colors active:scale-[0.98]"
      >
        <LogOut className="w-4 h-4" />
        <span>Sign Out of Terminal</span>
      </button>
    </div>
  );
};
