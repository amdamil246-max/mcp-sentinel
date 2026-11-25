import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import type { AuditLog } from '../types';
import {
  FileText,
  ShieldCheck,
  ShieldAlert,
  Hash,
  RefreshCw,
  Search,
  CheckCircle2,
  X
} from 'lucide-react';

export const AuditLogs: React.FC = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [verificationResult, setVerificationResult] = useState<any | null>(null);
  const [verifying, setVerifying] = useState(false);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const data = await api.getAuditLogs(100);
      setLogs(data);
    } catch (err) {
      console.error('Failed to load audit logs', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  const handleVerifyChain = async () => {
    try {
      setVerifying(true);
      const res = await api.verifyAuditChain();
      setVerificationResult(res);
    } catch (err: any) {
      alert(`Verification error: ${err.message}`);
    } finally {
      setVerifying(false);
    }
  };

  const filtered = logs.filter((l) => {
    if (!search) return true;
    const q = search.toLowerCase();
    return (
      l.target_resource.toLowerCase().includes(q) ||
      l.actor.toLowerCase().includes(q) ||
      l.action.toLowerCase().includes(q) ||
      l.entry_hash.toLowerCase().includes(q)
    );
  });

  return (
    <div className="space-y-6">
      {/* Header & Verify Action */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold text-white tracking-wide flex items-center space-x-2">
            <FileText className="w-5 h-5 text-cyan-400" />
            <span>Cryptographic Audit & Forensics Ledger</span>
          </h1>
          <p className="text-xs text-slate-400">
            Append-only, SHA-256 chained audit logs ensuring mathematical non-repudiation
          </p>
        </div>

        <div className="flex items-center space-x-2 self-start sm:self-auto">
          <button
            onClick={handleVerifyChain}
            disabled={verifying}
            className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-xs font-semibold shadow-lg shadow-emerald-950/40 transition-all disabled:opacity-50"
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>{verifying ? 'Verifying Chain...' : 'Verify Hash Chain'}</span>
          </button>

          <button
            onClick={fetchLogs}
            className="p-1.5 rounded-lg sentinel-subsurface hover:border-cyan-400/30 text-slate-200 transition-colors"
          >
            <RefreshCw className="w-4 h-4 text-cyan-400" />
          </button>
        </div>
      </div>

      {/* Verification Result Banner */}
      {verificationResult && (
        <div className={`p-4 rounded-xl border backdrop-blur-md flex items-center justify-between transition-all ${
          verificationResult.status === 'VERIFIED'
            ? 'bg-emerald-950/35 border-emerald-500/35 text-emerald-300'
            : 'bg-rose-950/40 border-rose-500/40 text-rose-300'
        }`}>
          <div className="flex items-center space-x-3">
            {verificationResult.status === 'VERIFIED' ? (
              <CheckCircle2 className="w-6 h-6 text-emerald-400 flex-shrink-0" />
            ) : (
              <ShieldAlert className="w-6 h-6 text-rose-400 flex-shrink-0" />
            )}
            <div>
              <div className="font-bold text-sm">
                Cryptographic Integrity: {verificationResult.status}
              </div>
              <div className="text-xs text-slate-400 font-mono mt-0.5">
                {verificationResult.message} ({verificationResult.total_records} records verified from GENESIS)
              </div>
              {verificationResult.chain_head_hash && (
                <div className="text-[10px] text-cyan-400 font-mono mt-1">
                  Head Hash: {verificationResult.chain_head_hash}
                </div>
              )}
            </div>
          </div>

          <button
            onClick={() => setVerificationResult(null)}
            className="p-1 rounded text-slate-400 hover:text-white"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Search Input */}
      <div className="relative">
        <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
        <input
          type="text"
          placeholder="Search by target resource, actor, action, or SHA-256 hash..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pl-9 pr-4 py-2 sentinel-surface rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-400/50"
        />
      </div>

      {/* Audit Log Table */}
      <div className="rounded-xl sentinel-surface overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/60 text-slate-400 uppercase text-[10px] tracking-wider border-b border-white/[0.08]">
              <tr>
                <th className="py-3 px-3">Timestamp</th>
                <th className="py-3 px-3">Event Type</th>
                <th className="py-3 px-3">Actor</th>
                <th className="py-3 px-3">Target Resource</th>
                <th className="py-3 px-3">Action</th>
                <th className="py-3 px-3">SHA-256 Hash Pointer</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.06] text-slate-300">
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-slate-400">
                    {loading ? 'Loading audit records...' : 'No matching audit log records.'}
                  </td>
                </tr>
              ) : (
                filtered.map((log) => (
                  <tr key={log.id} className="hover:bg-white/[0.03] transition-colors">
                    <td className="py-3 px-3 font-mono text-[11px] text-slate-400">
                      {new Date(log.created_at).toLocaleString()}
                    </td>
                    <td className="py-3 px-3 font-mono text-cyan-400 text-[11px]">{log.event_type}</td>
                    <td className="py-3 px-3 font-mono text-slate-300">{log.actor}</td>
                    <td className="py-3 px-3 font-mono font-medium text-white">{log.target_resource}</td>
                    <td className="py-3 px-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                        log.action === 'ALLOW' || log.action === 'APPROVED' ? 'bg-emerald-950 text-emerald-300 border border-emerald-800' :
                        log.action === 'BLOCK' || log.action === 'REJECTED' ? 'bg-rose-950 text-rose-300 border border-rose-800' :
                        'bg-amber-950 text-amber-300 border border-amber-800'
                      }`}>
                        {log.action}
                      </span>
                    </td>
                    <td className="py-3 px-3 font-mono text-[10px] text-slate-400">
                      <div className="flex items-center space-x-1" title={log.entry_hash}>
                        <Hash className="w-3 h-3 text-cyan-500 flex-shrink-0" />
                        <span>{log.entry_hash.substring(0, 16)}...</span>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
