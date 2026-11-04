import React, { useState } from 'react';
import { useKosha } from '../context/KoshaContext';
import { Session, Worker } from '../types';
import {
  Clock,
  ShieldCheck,
  Building2,
  CheckCircle2,
  Fingerprint,
  ArrowRight,
  UserCheck,
  Calendar,
  MapPin,
} from 'lucide-react';

export const CreateSessionScreen: React.FC = () => {
  const {
    preselectedWorkerForSession,
    workers,
    operator,
    activeSite,
    createSession,
    setSecondaryScreen,
    setSelectedWorkerId,
  } = useKosha();

  // If worker was preselected from Recognize or Worker Detail, use that, else default to first worker
  const [selectedWorkerId, setLocalSelectedWorkerId] = useState<string>(
    preselectedWorkerForSession?.id || (workers[0]?.id ?? 'WK-1001')
  );

  const selectedWorker = workers.find((w) => w.id === selectedWorkerId) || workers[0];

  const [shift, setShift] = useState<Session['shift']>('Morning Shift (06:00 - 14:00)');
  const [gate, setGate] = useState('North Gate Turnstile 2');
  const [notes, setNotes] = useState('Standard biometric check-in verified on Optical 500DPI sensor.');
  const [createdSessionResult, setCreatedSessionResult] = useState<Session | null>(null);

  const handleConfirmSession = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedWorker) return;

    const newSession = createSession(selectedWorker.id, shift, gate, notes);
    setCreatedSessionResult(newSession);
  };

  return (
    <div className="flex-1 w-full bg-slate-900 text-slate-100 overflow-y-auto no-scrollbar p-4 space-y-4 pb-24">
      {!createdSessionResult ? (
        <form onSubmit={handleConfirmSession} className="space-y-4">
          {/* Header Card Reinforcing "One Worker. Multiple Sessions." */}
          <div className="bg-gradient-to-r from-emerald-950/40 to-slate-800 border border-emerald-500/30 rounded-3xl p-4 shadow-lg space-y-2.5">
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-emerald-400" />
              <span className="text-xs font-mono font-bold uppercase tracking-wider text-emerald-400">
                One Worker · One Identity · Multiple Sessions
              </span>
            </div>
            <h2 className="text-base font-bold text-white">
              Log New Recording Session
            </h2>
            <p className="text-xs text-slate-300 leading-relaxed">
              This session will be permanently appended to the existing Worker record. A duplicate worker identity is never created.
            </p>
          </div>

          {/* Worker Selector Card */}
          <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-4 space-y-3">
            <label className="text-xs font-bold uppercase tracking-wider text-slate-300 block">
              Recognized Worker
            </label>

            <select
              value={selectedWorkerId}
              onChange={(e) => setLocalSelectedWorkerId(e.target.value)}
              className="w-full px-3 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-xs text-white font-medium focus:outline-none"
            >
              {workers.map((w) => (
                <option key={w.id} value={w.id}>
                  {w.id} — {w.name} ({w.department})
                </option>
              ))}
            </select>

            {/* Selected Worker Mini Profile Card */}
            {selectedWorker && (
              <div className="bg-slate-900/90 rounded-2xl p-3 border border-slate-800 flex items-center justify-between text-xs">
                <div className="flex items-center gap-3">
                  <div
                    className={`w-10 h-10 rounded-xl ${selectedWorker.avatarColor} text-white font-bold flex items-center justify-center shrink-0`}
                  >
                    {selectedWorker.name
                      .split(' ')
                      .map((n) => n[0])
                      .slice(0, 2)
                      .join('')}
                  </div>
                  <div>
                    <div className="flex items-center gap-1.5">
                      <span className="font-mono font-bold text-emerald-400">
                        {selectedWorker.id}
                      </span>
                      <span className="text-slate-400">·</span>
                      <span className="font-semibold text-white truncate max-w-[140px]">
                        {selectedWorker.name}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400">
                      {selectedWorker.department} · {selectedWorker.sessionsCount} prior sessions
                    </p>
                  </div>
                </div>

                <span className="text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded">
                  VERIFIED
                </span>
              </div>
            )}
          </div>

          {/* Session Parameters Card */}
          <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-4 space-y-3.5">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
              <Clock className="w-4 h-4 text-blue-400" />
              <span>Shift & Check-In Details</span>
            </h3>

            {/* Shift selection */}
            <div>
              <label className="text-xs font-medium text-slate-300 block mb-1">
                Designated Shift Schedule
              </label>
              <select
                value={shift}
                onChange={(e) => setShift(e.target.value as any)}
                className="w-full px-3 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-xs text-white focus:outline-none"
              >
                <option value="Morning Shift (06:00 - 14:00)">Morning Shift (06:00 - 14:00)</option>
                <option value="General Shift (08:30 - 17:30)">General Shift (08:30 - 17:30)</option>
                <option value="Night Shift (20:00 - 04:00)">Night Shift (20:00 - 04:00)</option>
              </select>
            </div>

            {/* Gate access point */}
            <div>
              <label className="text-xs font-medium text-slate-300 block mb-1">
                Access Turnstile / Checkpoint Gate
              </label>
              <select
                value={gate}
                onChange={(e) => setGate(e.target.value)}
                className="w-full px-3 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-xs text-white focus:outline-none"
              >
                <option value="North Gate Turnstile 2">North Gate Turnstile 2</option>
                <option value="Shaft 4 Access Bay">Shaft 4 Access Bay</option>
                <option value="Portal 1 Heavy Bay">Portal 1 Heavy Bay</option>
                <option value="West Apron Checkpoint">West Apron Checkpoint</option>
              </select>
            </div>

            {/* Recognition Method & Operator (Read-only metadata) */}
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="bg-slate-900/60 p-2.5 rounded-xl border border-slate-800">
                <span className="text-[10px] text-slate-400 block">Recognition Method</span>
                <span className="font-semibold text-emerald-400 flex items-center gap-1 mt-0.5">
                  <Fingerprint className="w-3.5 h-3.5" />
                  <span>Optical 500DPI</span>
                </span>
              </div>

              <div className="bg-slate-900/60 p-2.5 rounded-xl border border-slate-800">
                <span className="text-[10px] text-slate-400 block">Logging Operator</span>
                <span className="font-semibold text-slate-200 truncate block mt-0.5">
                  {operator.name}
                </span>
              </div>
            </div>

            {/* Session Notes */}
            <div>
              <label className="text-xs font-medium text-slate-300 block mb-1">
                Session Inspection Notes
              </label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={2}
                className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-xl text-xs text-white placeholder-slate-500 resize-none"
              />
            </div>
          </div>

          {/* Primary Action Button */}
          <button
            type="submit"
            className="w-full py-3.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs shadow-lg shadow-emerald-500/25 flex items-center justify-center gap-2 active:scale-[0.98] transition-all"
          >
            <Clock className="w-4 h-4" />
            <span>Create Recording Session</span>
          </button>
        </form>
      ) : (
        /* Session Creation Success State */
        <div className="text-center py-6 space-y-5 animate-in fade-in zoom-in-95 duration-200">
          <div className="w-16 h-16 rounded-3xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 flex items-center justify-center mx-auto shadow-xl shadow-emerald-500/20">
            <CheckCircle2 className="w-10 h-10 stroke-[2.2]" />
          </div>

          <div>
            <span className="text-xs font-mono font-bold uppercase tracking-wider text-emerald-400">
              Session Successfully Created
            </span>
            <h2 className="text-xl font-bold text-white mt-1">
              Shift Recorded for {createdSessionResult.workerId}
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Identity confirmed without duplication.
            </p>
          </div>

          {/* Result Card displaying Permanent Worker ID linkage */}
          <div className="bg-slate-800/90 border-2 border-emerald-500/60 rounded-3xl p-4 shadow-xl text-left space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-slate-700/60">
              <div>
                <span className="text-[10px] font-mono text-slate-400 uppercase">
                  Session ID
                </span>
                <div className="font-mono font-extrabold text-xl text-white">
                  {createdSessionResult.id}
                </div>
              </div>

              <div className="text-right">
                <span className="text-[10px] font-mono text-slate-400 uppercase">
                  Permanent Worker ID
                </span>
                <div className="font-mono font-bold text-base text-emerald-400">
                  {createdSessionResult.workerId}
                </div>
              </div>
            </div>

            <div className="text-xs space-y-1.5 pt-1">
              <div className="flex justify-between">
                <span className="text-slate-400">Worker Name:</span>
                <span className="font-semibold text-white">{createdSessionResult.workerName}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Shift Schedule:</span>
                <span className="text-slate-200">{createdSessionResult.shift}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Gate / Point:</span>
                <span className="text-slate-200">{createdSessionResult.gate}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Timestamp:</span>
                <span className="font-mono text-slate-200">{createdSessionResult.timestamp}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Status:</span>
                <span className="font-semibold text-emerald-400">{createdSessionResult.status}</span>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="space-y-2 pt-2">
            <button
              onClick={() => {
                setSelectedWorkerId(createdSessionResult.workerId);
                setSecondaryScreen('worker-detail');
              }}
              className="w-full py-3.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs shadow-md shadow-emerald-500/20 flex items-center justify-center gap-1.5"
            >
              <UserCheck className="w-4 h-4" />
              <span>View Worker's Session History</span>
            </button>

            <button
              onClick={() => setCreatedSessionResult(null)}
              className="w-full py-2.5 text-xs text-slate-400 hover:text-slate-200 font-medium"
            >
              Log Another Session
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
