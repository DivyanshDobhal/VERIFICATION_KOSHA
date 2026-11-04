import React from 'react';
import { useKosha } from '../../context/KoshaContext';
import { Home, Users, Fingerprint, Clock, UserCheck } from 'lucide-react';
import { NavigationTab } from '../../types';

export const BottomNavigation: React.FC = () => {
  const { currentTab, setCurrentTab, secondaryScreen, setSecondaryScreen } = useKosha();

  const handleTabClick = (tab: NavigationTab) => {
    setCurrentTab(tab);
    if (secondaryScreen !== 'none') {
      setSecondaryScreen('none');
    }
  };

  const navItems = [
    { id: 'home' as NavigationTab, label: 'Home', icon: Home },
    { id: 'workers' as NavigationTab, label: 'Workers', icon: Users },
    { id: 'recognize' as NavigationTab, label: 'Recognize', icon: Fingerprint, isCenter: true },
    { id: 'sessions' as NavigationTab, label: 'Sessions', icon: Clock },
    { id: 'profile' as NavigationTab, label: 'More', icon: UserCheck },
  ];

  return (
    <nav aria-label="Primary mobile navigation" className="w-full bg-slate-900/95 dark:bg-slate-900/95 backdrop-blur-lg border-t border-slate-800/90 pb-safe shrink-0 z-40">
      <div className="grid grid-cols-5 items-center h-16 px-1 relative">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id && secondaryScreen === 'none';

          if (item.isCenter) {
            return (
              <div key={item.id} className="relative flex justify-center items-center">
                <button
                  onClick={() => handleTabClick(item.id)}
                  aria-label="Recognize Worker Biometrics"
                  className={`-top-5 absolute w-14 h-14 rounded-full flex flex-col items-center justify-center transition-all duration-200 shadow-lg active:scale-95 ${
                    isActive
                      ? 'bg-emerald-500 text-slate-950 shadow-emerald-500/40 ring-4 ring-slate-900'
                      : 'bg-emerald-600 hover:bg-emerald-500 text-slate-950 shadow-emerald-600/30 ring-4 ring-slate-900'
                  }`}
                >
                  <Icon className="w-7 h-7 stroke-[2.2]" />
                  <span className="text-[9px] font-bold tracking-tight uppercase mt-0.5">
                    Scan
                  </span>
                </button>
              </div>
            );
          }

          return (
            <button
              key={item.id}
              onClick={() => handleTabClick(item.id)}
              className={`flex flex-col items-center justify-center h-full min-h-[44px] min-w-[44px] transition-colors ${
                isActive
                  ? 'text-emerald-400 font-semibold'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Icon className={`w-5 h-5 transition-transform ${isActive ? 'scale-110' : ''}`} />
              <span className={`text-[10px] tracking-tight mt-1 ${isActive ? 'font-bold text-emerald-400' : 'font-medium'}`}>
                {item.label}
              </span>
            </button>
          );
        })}
      </div>
    </nav>
  );
};
