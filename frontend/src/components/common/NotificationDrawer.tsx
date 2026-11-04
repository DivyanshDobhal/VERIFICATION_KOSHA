import React from 'react';
import { useKosha } from '../../context/KoshaContext';
import { X, Bell, CheckCircle2, AlertTriangle, Info, Trash2 } from 'lucide-react';

export const NotificationDrawer: React.FC = () => {
  const { notificationTrayOpen, setNotificationTrayOpen, notifications, dismissNotification } = useKosha();

  if (!notificationTrayOpen) return null;

  return (
    <div className="absolute inset-0 bg-black/60 backdrop-blur-sm z-50 flex flex-col justify-end animate-in fade-in duration-200">
      <div className="bg-slate-900 border-t border-slate-700/80 rounded-t-3xl max-h-[85%] flex flex-col overflow-hidden shadow-2xl">
        {/* Header */}
        <div className="px-5 py-4 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <Bell className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-bold text-sm text-white">System & Audit Alerts</h3>
              <p className="text-[11px] text-slate-400">Live biometric and identity log</p>
            </div>
          </div>

          <button
            onClick={() => setNotificationTrayOpen(false)}
            className="w-8 h-8 rounded-full bg-slate-800 hover:bg-slate-700 text-slate-300 flex items-center justify-center transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Notifications List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-2.5">
          {notifications.length === 0 ? (
            <div className="text-center py-10 text-slate-500 text-xs">
              No recent notifications or alerts.
            </div>
          ) : (
            notifications.map((item) => (
              <div
                key={item.id}
                className="bg-slate-800/80 border border-slate-700/70 rounded-2xl p-3.5 flex items-start gap-3 relative group"
              >
                <div className="mt-0.5 shrink-0">
                  {item.type === 'success' && (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  )}
                  {item.type === 'warning' && (
                    <AlertTriangle className="w-4 h-4 text-amber-400" />
                  )}
                  {item.type === 'info' && (
                    <Info className="w-4 h-4 text-blue-400" />
                  )}
                </div>

                <div className="flex-1 min-w-0 pr-6">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-semibold text-slate-200">
                      {item.title}
                    </h4>
                    <span className="text-[10px] text-slate-500 font-mono">
                      {item.time}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">
                    {item.desc}
                  </p>
                </div>

                <button
                  onClick={() => dismissNotification(item.id)}
                  title="Dismiss"
                  className="absolute top-3 right-3 text-slate-500 hover:text-slate-300 transition-colors"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-900/90 pb-safe">
          <button
            onClick={() => setNotificationTrayOpen(false)}
            className="w-full py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 font-semibold text-xs text-slate-200 transition-colors"
          >
            Close Alerts
          </button>
        </div>
      </div>
    </div>
  );
};
