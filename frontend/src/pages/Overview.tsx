import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import type { DashboardOverview } from '../types';
import {
  ShieldCheck,
  ShieldX,
  Clock,
  Activity,
  Server,
  Zap,
  RefreshCw,
  AlertOctagon
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell
} from 'recharts';

interface OverviewProps {
  onNavigate: (tab: any) => void;
}

export const Overview: React.FC<OverviewProps> = ({ onNavigate }) => {
  const [data, setData] = useState<DashboardOverview | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchOverview = async () => {
    try {
      setLoading(true);
      const overview = await api.getDashboardOverview();
      setData(overview);
    } catch (err) {
      console.error('Failed to load overview data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOverview();
    const interval = setInterval(fetchOverview, 5000); // Polling every 5s
    return () => clearInterval(interval);
  }, []);

  if (loading && !data) {
    return (
      <div className="flex items-center justify-center h-full text-slate-400 space-x-2">
        <RefreshCw className="w-5 h-5 animate-spin text-cyan-400" />
        <span>Loading Sentinel telemetry...</span>
      </div>
    );
  }

  const kpis = data?.kpis;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white tracking-wide">Security Operations Center</h1>
          <p className="text-xs text-slate-400">Continuous AI Agent Tool Execution Monitoring & Threat Interception</p>
        </div>
        <button
          onClick={fetchOverview}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg sentinel-subsurface hover:border-cyan-400/30 text-slate-200 text-xs transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5 text-cyan-400" />
          <span>Refresh</span>
        </button>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {/* Total Invocations */}
        <div className="p-4 rounded-xl sentinel-surface-interactive">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs">Invocations</span>
            <Activity className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold text-white font-mono">{kpis?.total_invocations ?? 0}</div>
          <div className="text-[10px] text-slate-400 mt-1">Total intercepted calls</div>
        </div>

        {/* Allowed */}
        <div className="p-4 rounded-xl sentinel-surface-interactive border-emerald-500/25">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs">Allowed</span>
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-emerald-400 font-mono">{kpis?.allowed_operations ?? 0}</div>
          <div className="text-[10px] text-emerald-400/80 mt-1">Conforming to policy</div>
        </div>

        {/* Blocked */}
        <div className="p-4 rounded-xl sentinel-surface-interactive border-rose-500/25">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs">Blocked</span>
            <ShieldX className="w-4 h-4 text-rose-400" />
          </div>
          <div className="text-2xl font-bold text-rose-400 font-mono">{kpis?.blocked_operations ?? 0}</div>
          <div className="text-[10px] text-rose-400/80 mt-1">Violations denied</div>
        </div>

        {/* Pending Approvals */}
        <div
          onClick={() => onNavigate('approvals')}
          className="p-4 rounded-xl sentinel-surface-interactive border-amber-500/25 cursor-pointer hover:border-amber-400/50"
        >
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs">Approvals</span>
            <Clock className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-amber-400 font-mono">{kpis?.pending_approvals ?? 0}</div>
          <div className="text-[10px] text-amber-400/80 mt-1">Awaiting human review</div>
        </div>

        {/* Critical Alerts */}
        <div
          onClick={() => onNavigate('alerts')}
          className="p-4 rounded-xl sentinel-surface-interactive border-rose-500/35 cursor-pointer hover:border-rose-400/60"
        >
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs">Alerts</span>
            <AlertOctagon className="w-4 h-4 text-rose-500" />
          </div>
          <div className="text-2xl font-bold text-rose-500 font-mono">{kpis?.critical_alerts ?? 0}</div>
          <div className="text-[10px] text-rose-400/80 mt-1">Active critical / high</div>
        </div>

        {/* Average Risk Score */}
        <div className="p-4 rounded-xl sentinel-surface-interactive border-indigo-500/25">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs">Avg Risk</span>
            <Zap className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-bold text-white font-mono">{kpis?.average_risk_score ?? 0}</div>
          <div className="text-[10px] text-slate-400 mt-1">Scale 0 (safe) - 100 (crit)</div>
        </div>
      </div>

      {/* Main Charts & Feed Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Risk Distribution Chart */}
        <div className="p-5 rounded-xl sentinel-surface flex flex-col justify-between">
          <div>
            <h2 className="text-sm font-semibold text-white mb-1">Risk Score Distribution</h2>
            <p className="text-xs text-slate-400 mb-4">Interceptions categorized by severity tiers</p>
          </div>

          <div className="h-52 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data?.risk_distribution || []}>
                <XAxis dataKey="name" stroke="#64748b" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} allowDecimals={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: 'rgba(7, 12, 24, 0.92)', borderColor: 'rgba(56, 189, 248, 0.25)', borderRadius: '8px', fontSize: '12px', backdropFilter: 'blur(12px)' }}
                />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {(data?.risk_distribution || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="flex justify-between items-center text-[11px] text-slate-400 pt-3 border-t border-white/[0.08] mt-2">
            <span>Low: 0-19</span>
            <span>Guarded: 20-39</span>
            <span>Med: 40-59</span>
            <span>High: 60-79</span>
            <span className="text-rose-400 font-semibold">Crit: 80-100</span>
          </div>
        </div>

        {/* Top Risky Tools */}
        <div className="p-5 rounded-xl sentinel-surface">
          <h2 className="text-sm font-semibold text-white mb-1">Top Risky Tool Targets</h2>
          <p className="text-xs text-slate-400 mb-4">Tools triggering highest average risk evaluations</p>

          <div className="space-y-3">
            {(data?.top_risky_tools || []).length === 0 ? (
              <div className="text-xs text-slate-400 text-center py-8">No risky tool invocations recorded yet.</div>
            ) : (
              (data?.top_risky_tools || []).map((t) => (
                <div key={t.tool_name} className="flex items-center justify-between p-2.5 rounded-lg sentinel-subsurface">
                  <div className="flex items-center space-x-2">
                    <Server className="w-3.5 h-3.5 text-slate-400" />
                    <span className="text-xs font-mono font-medium text-slate-200">{t.tool_name}</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <span className="text-[11px] text-slate-400">{t.invocations} calls</span>
                    <span className={`text-xs font-mono font-bold px-2 py-0.5 rounded ${
                      t.average_risk >= 80 ? 'bg-rose-950/80 text-rose-400 border border-rose-500/40' :
                      t.average_risk >= 50 ? 'bg-amber-950/80 text-amber-400 border border-amber-500/40' :
                      'bg-slate-800/80 text-slate-300'
                    }`}>
                      {t.average_risk}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Server Fleet Health */}
        <div className="p-5 rounded-xl sentinel-surface">
          <h2 className="text-sm font-semibold text-white mb-1">MCP Server Fleet Health</h2>
          <p className="text-xs text-slate-400 mb-4">Upstream tool providers connected to gateway</p>

          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 rounded-lg sentinel-subsurface">
              <div className="flex items-center space-x-2.5">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-sm shadow-emerald-400"></span>
                <span className="text-xs text-slate-200">Healthy Connections</span>
              </div>
              <span className="text-xs font-mono font-bold text-emerald-400">{kpis?.server_status.healthy ?? 0}</span>
            </div>

            <div className="flex items-center justify-between p-3 rounded-lg sentinel-subsurface">
              <div className="flex items-center space-x-2.5">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-500 shadow-sm shadow-amber-400"></span>
                <span className="text-xs text-slate-200">Degraded Providers</span>
              </div>
              <span className="text-xs font-mono font-bold text-amber-400">{kpis?.server_status.degraded ?? 0}</span>
            </div>

            <div className="flex items-center justify-between p-3 rounded-lg sentinel-subsurface">
              <div className="flex items-center space-x-2.5">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-500 shadow-sm shadow-rose-400"></span>
                <span className="text-xs text-slate-200">Offline Servers</span>
              </div>
              <span className="text-xs font-mono font-bold text-rose-400">{kpis?.server_status.offline ?? 0}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Security Interceptions Feed */}
      <div className="p-5 rounded-xl sentinel-surface">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-sm font-semibold text-white">Live Interception Stream</h2>
            <p className="text-xs text-slate-400">Real-time tool invocations passing through MCP Sentinel gate</p>
          </div>
          <button
            onClick={() => onNavigate('monitoring')}
            className="text-xs text-cyan-400 hover:text-cyan-300 font-medium"
          >
            View Live Monitoring →
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/55 text-slate-400 uppercase text-[10px] tracking-wider border-b border-white/[0.08]">
              <tr>
                <th className="py-2.5 px-3">Timestamp</th>
                <th className="py-2.5 px-3">Target Server</th>
                <th className="py-2.5 px-3">Tool Name</th>
                <th className="py-2.5 px-3">Risk Score</th>
                <th className="py-2.5 px-3">Classification</th>
                <th className="py-2.5 px-3">Enforcement Decision</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.06] text-slate-300">
              {(data?.recent_events || []).length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-6 text-center text-slate-400">
                    No recent events. Run demo scenarios to see real-time interceptions.
                  </td>
                </tr>
              ) : (
                (data?.recent_events || []).map((e) => (
                  <tr key={e.id} className="hover:bg-white/[0.03] transition-colors">
                    <td className="py-2.5 px-3 font-mono text-[11px] text-slate-400">
                      {new Date(e.timestamp).toLocaleTimeString()}
                    </td>
                    <td className="py-2.5 px-3 font-mono text-cyan-300">{e.server_id}</td>
                    <td className="py-2.5 px-3 font-mono font-medium text-white">{e.tool_name}</td>
                    <td className="py-2.5 px-3 font-mono font-bold">{e.risk_score}</td>
                    <td className="py-2.5 px-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                        e.risk_classification === 'Critical' ? 'bg-rose-950 text-rose-400 border border-rose-800' :
                        e.risk_classification === 'High' ? 'bg-orange-950 text-orange-400 border border-orange-800' :
                        e.risk_classification === 'Medium' ? 'bg-amber-950 text-amber-400 border border-amber-800' :
                        'bg-emerald-950 text-emerald-400 border border-emerald-800'
                      }`}>
                        {e.risk_classification}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 font-semibold">
                      <span className={`px-2 py-0.5 rounded text-[10px] ${
                        e.decision === 'ALLOW' ? 'bg-emerald-900/50 text-emerald-300' :
                        e.decision === 'BLOCK' ? 'bg-rose-900/50 text-rose-300' :
                        'bg-amber-900/50 text-amber-300'
                      }`}>
                        {e.decision}
                      </span>
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
