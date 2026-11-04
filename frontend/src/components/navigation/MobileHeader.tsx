import React, { useState } from 'react';
import { useKosha } from '../../context/KoshaContext';
import {
  ChevronLeft,
  Bell,
  MapPin,
  ChevronDown,
  Fingerprint,
  Check,
  Building2,
} from 'lucide-react';

export const MobileHeader: React.FC = () => {
  const {
    currentTab,
    secondaryScreen,
    setSecondaryScreen,
    setSelectedWorkerId,
    operator,
    activeSite,
    sites,
    updateActiveSite,
    setNotificationTrayOpen,
    notifications,
  } = useKosha();

  const [siteDropdownOpen, setSiteDropdownOpen] = useState(false);

  const handleBack = () => {
    setSecondaryScreen('none');
    setSelectedWorkerId(null);
  };

  const getScreenTitle = () => {
    if (secondaryScreen === 'register-worker') return 'Register New Worker';
    if (secondaryScreen === 'worker-detail') return 'Worker Profile';
    if (secondaryScreen === 'create-session') return 'New Recording Session';
    if (secondaryScreen === 'recognition-review') return 'Recognition Review';
    if (secondaryScreen === 'sites') return 'Workforce Sites';
    if (secondaryScreen === 'analytics') return 'Operational Analytics';
    if (secondaryScreen === 'settings') return 'System Settings';
    if (secondaryScreen === 'scanner-diagnostics') return 'Scanner Diagnostics';

    switch (currentTab) {
      case 'home':
        return 'KOSHA LABS';
      case 'workers':
        return 'Worker Directory';
      case 'recognize':
        return 'Biometric Recognition';
      case 'sessions':
        return 'Recording Sessions';
      case 'profile':
        return 'Operator Profile';
      default:
        return 'KOSHA LABS';
    }
  };

  return (
    <header className="relative w-full bg-slate-900/95 dark:bg-slate-900/95 backdrop-blur-md border-b border-slate-800/80 px-4 py-3 flex items-center justify-between z-30 shrink-0">
      {/* Left Slot: Back Button OR Brand Emblem */}
      <div className="flex items-center gap-2.5">
        {secondaryScreen !== 'none' ? (
          <button
            onClick={handleBack}
            className="w-9 h-9 rounded-xl bg-slate-800 text-slate-200 hover:text-white hover:bg-slate-700 flex items-center justify-center transition-colors border border-slate-700/60 active:scale-95"
            aria-label="Go back"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
        ) : (
          <div className="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
            <Fingerprint className="w-5 h-5" />
          </div>
        )}

        <div>
          <h1 className="text-base font-bold tracking-tight text-white flex items-center gap-1.5 leading-none">
            {secondaryScreen !== 'none' ? (
              getScreenTitle()
            ) : (
              <>
                <span>KOSHA LABS</span>
                <span className="text-[10px] font-mono font-medium px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                  BIO-ID
                </span>
              </>
            )}
          </h1>
          {secondaryScreen === 'none' && (
            <p className="text-[11px] text-slate-400 leading-none mt-1">
              One Worker · One Identity · Multiple Sessions
            </p>
          )}
        </div>
      </div>

      {/* Right Slot: Site Selector Pill & Notification Bell */}
      <div className="flex items-center gap-2">
        {/* Quick Site Switch Pill */}
        <div className="relative">
          <button
            onClick={() => setSiteDropdownOpen(!siteDropdownOpen)}
            className="flex items-center gap-1.5 bg-slate-800/90 hover:bg-slate-800 border border-slate-700/80 rounded-full px-2.5 py-1 text-xs text-slate-200 transition-colors"
            title="Switch Active Construction Site"
          >
            <MapPin className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
            <span className="font-mono font-medium text-[11px] max-w-[85px] truncate">
              {activeSite.code}
            </span>
            <ChevronDown className="w-3 h-3 text-slate-400" />
          </button>

          {/* Site Selector Dropdown */}
          {siteDropdownOpen && (
            <div className="absolute right-0 mt-2 w-64 bg-slate-800 border border-slate-700 rounded-2xl shadow-xl shadow-black/60 p-2 z-50 animate-in fade-in slide-in-from-top-2 duration-150">
              <div className="px-2 py-1.5 border-b border-slate-700/60 mb-1">
                <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400">
                  Switch Active Site Location
                </span>
              </div>
              <div className="space-y-1">
                {sites.map((site) => {
                  const isSelected = site.id === operator.activeSiteId;
                  return (
                    <button
                      key={site.id}
                      onClick={() => {
                        updateActiveSite(site.id);
                        setSiteDropdownOpen(false);
                      }}
                      className={`w-full text-left p-2 rounded-xl flex items-start justify-between gap-2 transition-colors ${
                        isSelected
                          ? 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/30'
                          : 'hover:bg-slate-700/60 text-slate-200'
                      }`}
                    >
                      <div className="min-w-0">
                        <div className="flex items-center gap-1.5">
                          <Building2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                          <span className="text-xs font-semibold truncate">
                            {site.code}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-400 truncate mt-0.5">
                          {site.name}
                        </p>
                      </div>
                      {isSelected && (
                        <Check className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Notifications Tray Trigger */}
        <button
          onClick={() => setNotificationTrayOpen(true)}
          className="relative w-9 h-9 rounded-xl bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 flex items-center justify-center transition-colors border border-slate-700/60"
          aria-label="View notifications"
        >
          <Bell className="w-4 h-4" />
          {notifications.length > 0 && (
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-emerald-500 ring-2 ring-slate-900" />
          )}
        </button>
      </div>
    </header>
  );
};
