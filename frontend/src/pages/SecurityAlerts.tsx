import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import type { SecurityAlert } from '../types';
import {
  ShieldAlert,
  CheckCircle,
  Filter,
  RefreshCw,
  Sparkles
} from 'lucide-react';

interface SecurityAlertsProps {
  onGenerateReport?: (alertId: string) => void;
}

export const SecurityAlerts: React.FC<SecurityAlertsProps> = ({ onGenerateReport }) => {
  const [alerts, setAlerts] = useState<SecurityAlert[]>([]);
  const [filterStatus, setFilterStatus] = useState<string>('ALL');
  const [filterCategory, setFilterCategory] = useState<string>('ALL');
  const [loading, setLoading] = useState(true);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const data = await api.getAlerts(filterStatus === 'ALL' ? undefined : filterStatus);
      setAlerts(data);
    } catch (err) {
      console.error('Failed to load alerts', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [filterStatus]);

  const handleStatusChange = async (alertId: string, newStatus: string) => {
    try {
      await api.updateAlertStatus(alertId, newStatus);
      fetchAlerts();
    } catch (err) {
      console.error('Failed to update alert status', err);
    }
  };

  const filtered = alerts.filter((a) => {
    if (filterCategory !== 'ALL' && a.threat_category !== filterCategory) return false;
    return true;
  });

  const categories = Array.from(new Set(alerts.map((a) => a.threat_category)));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold text-white tracking-wide flex items-center space-x-2">
            <ShieldAlert className="w-5 h-5 text-rose-500" />
            <span>Security Threat Alerts & Incidents</span>
          </h1>
          <p className="text-xs text-slate-400">Security violations and anomalous behavior intercepted by firewall</p>
        </div>

        <button
          onClick={fetchAlerts}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg sentinel-subsurface hover:border-cyan-400/30 text-slate-200 text-xs self-start sm:self-auto transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5 text-cyan-400" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Filter Toolbar */}
      <div className="flex flex-wrap items-center gap-3 sentinel-surface p-3 rounded-xl text-xs">
        <div className="flex items-center space-x-1.5 text-slate-400">
          <Filter className="w-3.5 h-3.5" />
          <span>Status:</span>
        </div>
        <div className="flex items-center space-x-1">
          {['ALL', 'NEW', 'INVESTIGATING', 'RESOLVED', 'DISMISSED'].map((st) => (
            <button
              key={st}
              onClick={() => setFilterStatus(st)}
              className={`px-2.5 py-1 rounded font-medium transition-colors ${
                filterStatus === st
                  ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {st}
            </button>
          ))}
        </div>

        <div className="h-4 w-px bg-white/10 hidden sm:block mx-2" />

        <div className="flex items-center space-x-1.5 text-slate-400">
          <span>Category:</span>
        </div>
        <select
          value={filterCategory}
          onChange={(e) => setFilterCategory(e.target.value)}
          className="sentinel-subsurface rounded-lg px-2.5 py-1 text-slate-300 text-xs focus:outline-none"
        >
          <option value="ALL">All Categories</option>
          {categories.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
      </div>

      {/* Alerts Feed */}
      <div className="space-y-3">
        {loading ? (
          <div className="p-12 text-center rounded-xl sentinel-surface text-slate-400 text-xs">
            <RefreshCw className="w-6 h-6 animate-spin text-cyan-400 mx-auto mb-2" />
            <span>Loading security alerts...</span>
          </div>
        ) : filtered.length === 0 ? (
          <div className="p-12 text-center rounded-xl sentinel-surface text-slate-400 text-xs">
            <CheckCircle className="w-8 h-8 text-emerald-500 mx-auto mb-2 opacity-80" />
            <div className="font-semibold text-slate-200">No Security Threats Detected</div>
            <div className="text-[11px] mt-1 text-slate-500">Run scenario B or C to simulate attack attempts.</div>
          </div>
        ) : (
          filtered.map((alert) => (
            <div
              key={alert.id}
              className="p-5 rounded-xl sentinel-surface-interactive space-y-3"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center space-x-2.5">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    alert.severity === 'Critical' ? 'bg-rose-950 text-rose-400 border border-rose-800' :
                    alert.severity === 'High' ? 'bg-orange-950 text-orange-400 border border-orange-800' :
                    'bg-amber-950 text-amber-400 border border-amber-800'
                  }`}>
                    {alert.severity.toUpperCase()}
                  </span>
                  <span className="text-white font-semibold text-sm">{alert.title}</span>
                  <span className="text-[11px] font-mono text-cyan-400">({alert.affected_tool})</span>
                </div>

                <div className="flex items-center space-x-2">
                  <span className="text-slate-500 text-[11px] font-mono">
                    {new Date(alert.created_at).toLocaleString()}
                  </span>
                </div>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed">{alert.description}</p>

              {/* Evidence Snippet */}
              {alert.evidence && (
                <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800/80 font-mono text-[11px] text-rose-300 overflow-x-auto">
                  <span className="text-slate-500 select-none mr-2">EVIDENCE:</span>
                  {alert.evidence.snippet || JSON.stringify(alert.evidence)}
                </div>
              )}

              {/* Status and Action Buttons */}
              <div className="flex flex-wrap items-center justify-between pt-2 border-t border-slate-800/60 gap-2">
                <div className="flex items-center space-x-2 text-xs">
                  <span className="text-slate-400">Status:</span>
                  <span className="font-mono font-semibold text-cyan-400">{alert.status}</span>
                </div>

                <div className="flex items-center space-x-2 text-xs">
                  {onGenerateReport && (
                    <button
                      onClick={() => onGenerateReport(alert.id)}
                      className="flex items-center space-x-1 px-2.5 py-1 rounded bg-violet-950 hover:bg-violet-900 text-violet-300 border border-violet-800 text-[11px]"
                    >
                      <Sparkles className="w-3 h-3" />
                      <span>AI Forensic Report</span>
                    </button>
                  )}

                  {alert.status === 'NEW' && (
                    <button
                      onClick={() => handleStatusChange(alert.id, 'INVESTIGATING')}
                      className="px-2.5 py-1 rounded bg-amber-950 hover:bg-amber-900 text-amber-300 border border-amber-800 text-[11px]"
                    >
                      Mark Investigating
                    </button>
                  )}

                  {alert.status !== 'RESOLVED' && (
                    <button
                      onClick={() => handleStatusChange(alert.id, 'RESOLVED')}
                      className="px-2.5 py-1 rounded bg-emerald-950 hover:bg-emerald-900 text-emerald-300 border border-emerald-800 text-[11px]"
                    >
                      Resolve Alert
                    </button>
                  )}

                  {alert.status !== 'DISMISSED' && (
                    <button
                      onClick={() => handleStatusChange(alert.id, 'DISMISSED')}
                      className="px-2.5 py-1 rounded bg-slate-900 hover:bg-slate-800 text-slate-400 border border-slate-800 text-[11px]"
                    >
                      Dismiss
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
