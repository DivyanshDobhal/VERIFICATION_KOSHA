import React, { useState } from 'react';
import { useKosha } from '../context/KoshaContext';
import { RecognitionReview } from '../types';
import {
  AlertTriangle,
  CheckCircle2,
  XCircle,
  RotateCcw,
  ShieldCheck,
  UserCheck,
  Building2,
  Clock,
  ArrowRight,
} from 'lucide-react';

export const RecognitionReviewScreen: React.FC = () => {
  const { reviews, resolveReview, setSelectedWorkerId, setSecondaryScreen } = useKosha();

  const [activeReviewId, setActiveReviewId] = useState<string | null>(null);
  const [confirmDialog, setConfirmDialog] = useState<{
    open: boolean;
    reviewId: string;
    action: 'confirm' | 'reject' | 'recapture';
    title: string;
    desc: string;
  } | null>(null);

  const pendingReviews = reviews.filter((r) => r.status === 'Pending Review');
  const resolvedReviews = reviews.filter((r) => r.status !== 'Pending Review');

  const handleActionClick = (
    reviewId: string,
    action: 'confirm' | 'reject' | 'recapture'
  ) => {
    const titles = {
      confirm: 'Confirm Identity Match?',
      reject: 'Reject Match Discrepancy?',
      recapture: 'Request Biometric Recapture?',
    };
    const descs = {
      confirm: 'Supervisor sign-off confirms this identity and will record an approved shift session.',
      reject: 'Match will be discarded. Worker will be routed to registration if unregistered.',
      recapture: 'Clean sensor window and instruct worker to re-position finger.',
    };

    setConfirmDialog({
      open: true,
      reviewId,
      action,
      title: titles[action],
      desc: descs[action],
    });
  };

  const handleExecuteDialog = () => {
    if (confirmDialog) {
      resolveReview(confirmDialog.reviewId, confirmDialog.action);
      setConfirmDialog(null);
    }
  };

  return (
    <div className="flex-1 w-full bg-slate-900 text-slate-100 overflow-y-auto no-scrollbar p-4 space-y-4 pb-24">
      {/* Overview Card */}
      <div className="bg-gradient-to-r from-amber-950/40 to-slate-800 border border-amber-500/30 rounded-3xl p-4 shadow-lg space-y-1.5">
        <div className="flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-amber-400" />
          <span className="text-xs font-mono font-bold uppercase tracking-wider text-amber-400">
            Manual Verification Queue
          </span>
        </div>
        <h2 className="text-base font-bold text-white">
          Recognition Discrepancy Review
        </h2>
        <p className="text-xs text-slate-300">
          Field biometric scans with similarity between 50% and 80% require manual supervisor confirmation to prevent mistaken identity or fraudulent buddy punch.
        </p>
      </div>

      {/* Pending Reviews Section */}
      <div className="space-y-3">
        <div className="flex items-center justify-between px-1">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
            Pending Discrepancies ({pendingReviews.length})
          </h3>
          <span className="text-[11px] font-mono text-amber-400">
            Requires Action
          </span>
        </div>

        {pendingReviews.length === 0 ? (
          <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-8 text-center space-y-2">
            <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto" />
            <h4 className="text-sm font-bold text-white">Review Queue Clean</h4>
            <p className="text-xs text-slate-400 max-w-xs mx-auto">
              All biometric recognition scans are resolved. Zero pending identity ambiguities.
            </p>
          </div>
        ) : (
          pendingReviews.map((review) => (
            <div
              key={review.id}
              className="bg-slate-800/90 border-2 border-amber-500/40 rounded-3xl p-4 space-y-3 shadow-lg"
            >
              {/* Header */}
              <div className="flex items-center justify-between pb-2 border-b border-slate-700/60">
                <div className="flex items-center gap-2">
                  <span className="font-mono font-bold text-xs bg-slate-700 text-white px-2 py-0.5 rounded">
                    {review.id}
                  </span>
                  <span className="text-xs text-slate-300">
                    Scanned {review.scannedFinger}
                  </span>
                </div>

                <div className="flex items-center gap-1.5 font-mono text-xs">
                  <span className="text-slate-400">Confidence:</span>
                  <span className="font-bold text-amber-400 bg-amber-500/15 px-2 py-0.5 rounded">
                    {review.confidenceScore}%
                  </span>
                </div>
              </div>

              {/* Candidates Side-by-side or stacked */}
              <div className="space-y-2">
                <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 block">
                  Top Matched Candidate:
                </span>

                <div className="bg-slate-900/90 rounded-2xl p-3 border border-slate-700 flex items-center justify-between text-xs">
                  <div className="flex items-center gap-3">
                    <div
                      className={`w-9 h-9 rounded-xl ${review.primaryCandidate.avatarColor} text-white font-bold flex items-center justify-center`}
                    >
                      {review.primaryCandidate.name
                        .split(' ')
                        .map((n) => n[0])
                        .slice(0, 2)
                        .join('')}
                    </div>
                    <div>
                      <div className="flex items-center gap-1.5">
                        <span className="font-mono font-bold text-emerald-400">
                          {review.primaryCandidate.workerId}
                        </span>
                        <span className="font-semibold text-white">
                          {review.primaryCandidate.name}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-400">
                        {review.primaryCandidate.department} · Enrolled {review.primaryCandidate.enrolledDate}
                      </p>
                    </div>
                  </div>

                  <button
                    onClick={() => {
                      setSelectedWorkerId(review.primaryCandidate.workerId);
                      setSecondaryScreen('worker-detail');
                    }}
                    className="p-1.5 rounded-lg bg-slate-800 text-slate-300 hover:text-white"
                    title="Inspect Profile"
                  >
                    <UserCheck className="w-4 h-4" />
                  </button>
                </div>

                {review.secondaryCandidate && (
                  <>
                    <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 block pt-1">
                      Secondary Possible Candidate:
                    </span>
                    <div className="bg-slate-900/60 rounded-2xl p-2.5 border border-slate-800 flex items-center justify-between text-xs">
                      <div>
                        <span className="font-mono font-bold text-slate-300">
                          {review.secondaryCandidate.workerId}
                        </span>
                        <span className="text-slate-300 ml-2 font-medium">
                          {review.secondaryCandidate.name}
                        </span>
                        <span className="text-[11px] text-slate-500 ml-2">
                          ({review.secondaryCandidate.department})
                        </span>
                      </div>
                      <span className="text-[11px] font-mono text-slate-400">
                        {review.secondaryCandidate.similarity}%
                      </span>
                    </div>
                  </>
                )}
              </div>

              {/* Attempt meta */}
              <div className="pt-2 border-t border-slate-700/60 flex items-center justify-between text-[11px] text-slate-400 font-mono">
                <div className="flex items-center gap-1">
                  <Clock className="w-3 h-3 text-slate-400" />
                  <span>{review.timestamp}</span>
                </div>
                <span>{review.operator}</span>
              </div>

              {/* Supervisor Actions */}
              <div className="grid grid-cols-3 gap-2 pt-1">
                <button
                  onClick={() => handleActionClick(review.id, 'confirm')}
                  className="py-2.5 px-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs flex items-center justify-center gap-1 shadow-sm transition-all"
                >
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Confirm Match</span>
                </button>

                <button
                  onClick={() => handleActionClick(review.id, 'recapture')}
                  className="py-2.5 px-2 rounded-xl bg-slate-700 hover:bg-slate-650 text-slate-200 font-semibold text-xs flex items-center justify-center gap-1 transition-all"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  <span>Recapture</span>
                </button>

                <button
                  onClick={() => handleActionClick(review.id, 'reject')}
                  className="py-2.5 px-2 rounded-xl bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 border border-rose-500/30 font-semibold text-xs flex items-center justify-center gap-1 transition-all"
                >
                  <XCircle className="w-3.5 h-3.5" />
                  <span>Reject</span>
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Resolved Reviews Section */}
      {resolvedReviews.length > 0 && (
        <div className="space-y-2 pt-2">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 px-1">
            Recently Resolved Verifications
          </h3>

          <div className="space-y-2">
            {resolvedReviews.map((rev) => (
              <div
                key={rev.id}
                className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-3 flex items-center justify-between text-xs"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-bold text-slate-300">{rev.id}</span>
                    <span
                      className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                        rev.status === 'Confirmed Match'
                          ? 'bg-emerald-500/20 text-emerald-300'
                          : 'bg-rose-500/20 text-rose-300'
                      }`}
                    >
                      {rev.status}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1">
                    Candidate: {rev.primaryCandidate.name} ({rev.primaryCandidate.workerId})
                  </p>
                </div>
                <div className="text-right text-[10px] text-slate-500 font-mono">
                  <span>Resolved by {rev.resolvedBy}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Native-style Confirmation Dialog */}
      {confirmDialog && confirmDialog.open && (
        <div className="absolute inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-in fade-in duration-150">
          <div className="w-full max-w-sm bg-slate-900 border border-slate-700 rounded-3xl p-5 space-y-4 shadow-2xl">
            <h3 className="font-bold text-base text-white">
              {confirmDialog.title}
            </h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              {confirmDialog.desc}
            </p>

            <div className="grid grid-cols-2 gap-2 pt-2">
              <button
                onClick={() => setConfirmDialog(null)}
                className="py-2.5 rounded-xl bg-slate-800 text-slate-300 font-semibold text-xs hover:bg-slate-700"
              >
                Cancel
              </button>

              <button
                onClick={handleExecuteDialog}
                className={`py-2.5 rounded-xl font-bold text-xs ${
                  confirmDialog.action === 'confirm'
                    ? 'bg-emerald-500 text-slate-950'
                    : confirmDialog.action === 'reject'
                    ? 'bg-rose-500 text-white'
                    : 'bg-amber-500 text-slate-950'
                }`}
              >
                Confirm Decision
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
