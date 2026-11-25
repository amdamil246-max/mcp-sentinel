import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import type { ApprovalRequest } from '../types';
import {
  CheckSquare,
  ShieldCheck,
  ShieldX,
  Clock,
  RefreshCw,
  Hash
} from 'lucide-react';

export const ApprovalCenter: React.FC = () => {
  const [approvals, setApprovals] = useState<ApprovalRequest[]>([]);
  const [selectedStatus, setSelectedStatus] = useState<string>('PENDING');
  const [loading, setLoading] = useState(true);
  const [actionInProgress, setActionInProgress] = useState<string | null>(null);

  const fetchApprovals = async () => {
    try {
      setLoading(true);
      const data = await api.getApprovals(selectedStatus === 'ALL' ? undefined : selectedStatus);
      setApprovals(data);
    } catch (err) {
      console.error('Failed to load approvals', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApprovals();
    const interval = setInterval(fetchApprovals, 4000);
    return () => clearInterval(interval);
  }, [selectedStatus]);

  const handleDecision = async (id: string, decision: 'APPROVE' | 'REJECT') => {
    try {
      setActionInProgress(id);
      if (decision === 'APPROVE') {
        await api.approveRequest(id, 'Authorized by security admin');
      } else {
        await api.rejectRequest(id, 'Denied by security admin policy review');
      }
      fetchApprovals();
    } catch (err: any) {
      alert(`Decision error: ${err.message}`);
    } finally {
      setActionInProgress(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold text-white tracking-wide flex items-center space-x-2">
            <CheckSquare className="w-5 h-5 text-amber-400" />
            <span>Human-in-the-Loop Approval Center</span>
          </h1>
          <p className="text-xs text-slate-400">
            Cryptographically verified authorization checkpoint for sensitive & high-impact AI operations
          </p>
        </div>

        <button
          onClick={fetchApprovals}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg sentinel-subsurface hover:border-cyan-400/30 text-slate-200 text-xs self-start sm:self-auto transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5 text-cyan-400" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center space-x-2 sentinel-surface p-1.5 rounded-xl text-xs w-fit">
        {['PENDING', 'APPROVED', 'REJECTED', 'ALL'].map((st) => (
          <button
            key={st}
            onClick={() => setSelectedStatus(st)}
            className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
              selectedStatus === st
                ? 'bg-amber-500/20 text-amber-300 border border-amber-400/35'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            {st}
          </button>
        ))}
      </div>

      {/* Approvals List */}
      <div className="space-y-4">
        {loading ? (
          <div className="p-12 text-center rounded-xl sentinel-surface text-slate-400 text-xs">
            <RefreshCw className="w-6 h-6 animate-spin text-cyan-400 mx-auto mb-2" />
            <span>Loading approval requests...</span>
          </div>
        ) : approvals.length === 0 ? (
          <div className="p-12 text-center rounded-xl sentinel-surface text-slate-400 text-xs">
            <ShieldCheck className="w-8 h-8 text-slate-500 mx-auto mb-2" />
            <div className="font-semibold text-slate-200">No {selectedStatus} Approvals</div>
            <div className="text-[11px] mt-1 text-slate-500">
              Run Scenario E to generate a live sensitive operation approval request.
            </div>
          </div>
        ) : (
          approvals.map((req) => (
            <div
              key={req.id}
              className="p-5 rounded-xl sentinel-surface-interactive space-y-4"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    req.status === 'PENDING' ? 'bg-amber-950 text-amber-300 border border-amber-800 animate-pulse' :
                    req.status === 'APPROVED' ? 'bg-emerald-950 text-emerald-300 border border-emerald-800' :
                    'bg-rose-950 text-rose-300 border border-rose-800'
                  }`}>
                    {req.status}
                  </span>
                  <span className="font-mono text-sm font-bold text-white">{req.tool_name}</span>
                  <span className="text-[11px] text-slate-400">on {req.server_name}</span>
                </div>

                <div className="flex items-center space-x-3 text-xs font-mono text-slate-400">
                  <div className="flex items-center space-x-1">
                    <Clock className="w-3.5 h-3.5 text-amber-400" />
                    <span>Expires: {new Date(req.expires_at).toLocaleTimeString()}</span>
                  </div>
                </div>
              </div>

              {/* Reasons & Risk */}
              <div className="p-3 sentinel-subsurface rounded-lg space-y-1.5 text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400 font-semibold text-[11px] uppercase tracking-wider">
                    Risk Assessment & Detection Reasons
                  </span>
                  <span className="font-mono text-amber-400 font-bold">
                    Risk Score: {req.risk_score} / 100
                  </span>
                </div>
                <ul className="list-disc list-inside text-slate-300 text-xs space-y-1">
                  {req.reasons.map((r, idx) => (
                    <li key={idx}>{r}</li>
                  ))}
                </ul>
              </div>

              {/* Redacted Arguments & Anti-Tamper Hash */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-[11px]">
                  <span className="text-slate-400 font-semibold uppercase tracking-wider">
                    Requested Parameters (Secrets Redacted)
                  </span>
                  <div className="flex items-center space-x-1 text-cyan-400 font-mono text-[10px]">
                    <Hash className="w-3 h-3" />
                    <span>Arg Hash: {req.arguments_hash.substring(0, 16)}...</span>
                  </div>
                </div>
                <pre className="p-3 sentinel-subsurface rounded-lg font-mono text-[11px] text-cyan-300 overflow-x-auto">
                  {JSON.stringify(req.redacted_arguments, null, 2)}
                </pre>
              </div>

              {/* Action Buttons for Pending */}
              {req.status === 'PENDING' && (
                <div className="flex items-center justify-end space-x-3 pt-2 border-t border-slate-800/60">
                  <button
                    disabled={actionInProgress === req.id}
                    onClick={() => handleDecision(req.id, 'REJECT')}
                    className="flex items-center space-x-1.5 px-3 py-1.5 bg-rose-950 hover:bg-rose-900 text-rose-300 border border-rose-800 rounded-lg text-xs font-semibold transition-colors disabled:opacity-50"
                  >
                    <ShieldX className="w-3.5 h-3.5" />
                    <span>Reject Request</span>
                  </button>

                  <button
                    disabled={actionInProgress === req.id}
                    onClick={() => handleDecision(req.id, 'APPROVE')}
                    className="flex items-center space-x-1.5 px-4 py-1.5 bg-emerald-950 hover:bg-emerald-900 text-emerald-300 border border-emerald-800 rounded-lg text-xs font-semibold transition-colors shadow-lg shadow-emerald-950/50 disabled:opacity-50"
                  >
                    <ShieldCheck className="w-3.5 h-3.5" />
                    <span>Authorize Execution</span>
                  </button>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};
