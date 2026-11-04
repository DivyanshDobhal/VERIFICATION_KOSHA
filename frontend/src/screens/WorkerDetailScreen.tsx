import React, { useState } from 'react';
import { useKosha } from '../context/KoshaContext';
import { SessionCard } from '../components/sessions/SessionCard';
import {
  Fingerprint,
  Calendar,
  Clock,
  Phone,
  ShieldCheck,
  Building2,
  Plus,
  Edit3,
  User,
  Heart,
  FileText,
  X,
  Check,
} from 'lucide-react';

export const WorkerDetailScreen: React.FC = () => {
  const {
    selectedWorkerId,
    workers,
    sessions,
    setSecondaryScreen,
    setPreselectedWorkerForSession,
  } = useKosha();

  const [editModalOpen, setEditModalOpen] = useState(false);

  const worker = workers.find((w) => w.id === selectedWorkerId) || workers[0];

  // All recording sessions strictly tied to this permanent Worker ID!
  const workerSessions = sessions.filter((s) => s.workerId === worker.id);

  // Edit metadata form local states
  const [editContact, setEditContact] = useState(worker.contact);
  const [editEmergency, setEditEmergency] = useState(worker.emergencyContact);
  const [editDepartment, setEditDepartment] = useState(worker.department);
  const [editNotes, setEditNotes] = useState(worker.notes || '');

  const handleStartSessionForWorker = () => {
    setPreselectedWorkerForSession(worker);
    setSecondaryScreen('create-session');
  };

  const handleSaveMetadata = (e: React.FormEvent) => {
    e.preventDefault();
    worker.contact = editContact;
    worker.emergencyContact = editEmergency;
    worker.department = editDepartment;
    worker.notes = editNotes;
    setEditModalOpen(false);
  };

  return (
    <div className="flex-1 w-full bg-slate-900 text-slate-100 overflow-y-auto no-scrollbar p-4 space-y-4 pb-24">
      {/* Worker Header Card */}
      <div className="bg-gradient-to-b from-slate-800 to-slate-800/80 border border-slate-700 rounded-3xl p-4 shadow-xl space-y-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div
              className={`w-14 h-14 rounded-2xl ${worker.avatarColor} text-white font-extrabold text-xl flex items-center justify-center shadow-lg`}
            >
              {worker.name
                .split(' ')
                .map((n) => n[0])
                .slice(0, 2)
                .join('')}
            </div>

            <div>
              <div className="flex items-center gap-2">
                <span className="font-mono font-bold text-xs text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                  {worker.id}
                </span>
                <span
                  className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                    worker.status === 'Active'
                      ? 'bg-emerald-500/20 text-emerald-300'
                      : 'bg-amber-500/20 text-amber-300'
                  }`}
                >
                  {worker.status}
                </span>
              </div>

              <h2 className="text-lg font-bold text-white mt-1 leading-snug">
                {worker.name}
              </h2>
              <p className="text-xs text-slate-400">
                {worker.department} · {worker.category}
              </p>
            </div>
          </div>

          <button
            onClick={() => setEditModalOpen(true)}
            className="p-2 rounded-xl bg-slate-700/80 hover:bg-slate-700 text-slate-300 transition-colors"
            title="Edit Metadata"
          >
            <Edit3 className="w-4 h-4" />
          </button>
        </div>

        {/* Permanent Identity Tagline banner */}
        <div className="bg-slate-950/60 rounded-2xl p-2.5 border border-slate-800 flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span className="text-slate-300 font-medium">Single Permanent Identity</span>
          </div>
          <span className="font-mono text-emerald-400 font-bold">{worker.id}</span>
        </div>
      </div>

      {/* Primary Action Button: Create Session for This Worker */}
      <button
        onClick={handleStartSessionForWorker}
        className="w-full py-3.5 px-4 rounded-2xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs shadow-lg shadow-emerald-500/20 flex items-center justify-center gap-2 transition-all active:scale-[0.98]"
      >
        <Plus className="w-4 h-4 stroke-[2.5]" />
        <span>Create New Recording Session for {worker.id}</span>
      </button>

      {/* Personal & Deployment Details */}
      <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-4 space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
          <User className="w-3.5 h-3.5 text-blue-400" />
          <span>Worker Demographics & Work Profile</span>
        </h3>

        <div className="grid grid-cols-2 gap-3 text-xs">
          <div className="bg-slate-900/60 p-2.5 rounded-xl border border-slate-800">
            <span className="text-[10px] text-slate-400 block">Age & Gender</span>
            <span className="font-semibold text-slate-200">{worker.age} years · {worker.gender}</span>
          </div>

          <div className="bg-slate-900/60 p-2.5 rounded-xl border border-slate-800">
            <span className="text-[10px] text-slate-400 block">Body Weight</span>
            <span className="font-semibold text-slate-200">{worker.weight} kg</span>
          </div>

          <div className="bg-slate-900/60 p-2.5 rounded-xl border border-slate-800">
            <span className="text-[10px] text-slate-400 block">Blood Group</span>
            <span className="font-semibold text-slate-200 flex items-center gap-1">
              <Heart className="w-3 h-3 text-rose-400" />
              <span>{worker.bloodGroup}</span>
            </span>
          </div>

          <div className="bg-slate-900/60 p-2.5 rounded-xl border border-slate-800">
            <span className="text-[10px] text-slate-400 block">Assigned Site</span>
            <span className="font-semibold text-slate-200 truncate block">{worker.siteName}</span>
          </div>

          <div className="col-span-2 bg-slate-900/60 p-2.5 rounded-xl border border-slate-800">
            <span className="text-[10px] text-slate-400 block">Primary Contact Phone</span>
            <span className="font-mono font-medium text-slate-200">{worker.contact}</span>
          </div>

          <div className="col-span-2 bg-slate-900/60 p-2.5 rounded-xl border border-slate-800">
            <span className="text-[10px] text-slate-400 block">Emergency Contact</span>
            <span className="font-medium text-slate-200">{worker.emergencyContact}</span>
          </div>
        </div>
      </div>

      {/* Biometric Templates Section */}
      <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-4 space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
            <Fingerprint className="w-4 h-4 text-emerald-400" />
            <span>Enrolled Fingerprint Templates</span>
          </h3>
          <span className="text-[11px] font-mono text-emerald-400 font-bold">
            {worker.enrolledFingers.length} Templates Active
          </span>
        </div>

        <div className="space-y-2">
          {worker.enrolledFingers.map((item, idx) => (
            <div
              key={idx}
              className="bg-slate-900/70 border border-slate-800 rounded-xl p-2.5 flex items-center justify-between text-xs"
            >
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400 font-bold text-xs">
                  {idx + 1}
                </div>
                <div>
                  <span className="font-semibold text-slate-200">{item.finger}</span>
                  <span className="text-[10px] text-slate-400 block font-mono">
                    Enrolled on {item.enrolledAt}
                  </span>
                </div>
              </div>

              <div className="text-right">
                <span className="text-[10px] font-mono uppercase text-slate-400 block">Quality</span>
                <span className="font-mono font-bold text-emerald-400 text-xs">
                  {item.quality}% Matchable
                </span>
              </div>
            </div>
          ))}
        </div>

        <div className="p-2 rounded-xl bg-slate-900/60 border border-slate-800 text-[10px] text-slate-400">
          <p>
            🔒 Privacy Standard: Biometric templates stored as non-invertible ISO/IEC 19794-2 feature vectors. Raw ridge image files are purged post-enrollment.
          </p>
        </div>
      </div>

      {/* Linked Recording Sessions Timeline */}
      <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-4 space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
              <Clock className="w-4 h-4 text-blue-400" />
              <span>Linked Recording Sessions</span>
            </h3>
            <p className="text-[11px] text-slate-400 mt-0.5">
              History of daily shifts linked to permanent ID {worker.id}
            </p>
          </div>
          <span className="font-mono text-xs font-bold text-white bg-slate-700 px-2 py-0.5 rounded">
            {workerSessions.length} Total
          </span>
        </div>

        {workerSessions.length === 0 ? (
          <div className="text-center py-6 text-slate-500 text-xs">
            No recording sessions logged yet for this worker.
          </div>
        ) : (
          <div className="space-y-2">
            {workerSessions.map((session) => (
              <SessionCard key={session.id} session={session} />
            ))}
          </div>
        )}
      </div>

      {/* Edit Worker Metadata Modal */}
      {editModalOpen && (
        <div className="absolute inset-0 bg-black/60 backdrop-blur-sm z-50 flex flex-col justify-end animate-in fade-in duration-150">
          <div className="bg-slate-900 border-t border-slate-700 rounded-t-3xl p-5 space-y-4 max-h-[85%] overflow-y-auto">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800">
              <h3 className="font-bold text-sm text-white">Edit Worker Metadata</h3>
              <button
                onClick={() => setEditModalOpen(false)}
                className="w-8 h-8 rounded-full bg-slate-800 text-slate-300 flex items-center justify-center"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleSaveMetadata} className="space-y-3">
              <div>
                <label className="text-xs font-medium text-slate-300 block mb-1">
                  Department
                </label>
                <input
                  type="text"
                  value={editDepartment}
                  onChange={(e) => setEditDepartment(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-xs text-white"
                />
              </div>

              <div>
                <label className="text-xs font-medium text-slate-300 block mb-1">
                  Contact Phone
                </label>
                <input
                  type="text"
                  value={editContact}
                  onChange={(e) => setEditContact(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-xs text-white"
                />
              </div>

              <div>
                <label className="text-xs font-medium text-slate-300 block mb-1">
                  Emergency Contact
                </label>
                <input
                  type="text"
                  value={editEmergency}
                  onChange={(e) => setEditEmergency(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-xs text-white"
                />
              </div>

              <div>
                <label className="text-xs font-medium text-slate-300 block mb-1">
                  Site Notes
                </label>
                <textarea
                  value={editNotes}
                  onChange={(e) => setEditNotes(e.target.value)}
                  rows={2}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-xs text-white resize-none"
                />
              </div>

              <button
                type="submit"
                className="w-full py-3 rounded-xl bg-emerald-500 text-slate-950 font-bold text-xs"
              >
                Save Changes
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
