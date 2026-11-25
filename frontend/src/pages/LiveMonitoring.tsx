import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import type { ToolInvocation } from '../types';
import {
  Activity,
  Search,
  Eye,
  X,
  Sparkles,
  Terminal
} from 'lucide-react';

interface LiveMonitoringProps {
  onAskAi?: (invocationId: string) => void;
}

export const LiveMonitoring: React.FC<LiveMonitoringProps> = ({ onAskAi }) => {
  const [invocations, setInvocations] = useState<ToolInvocation[]>([]);
  const [selectedInv, setSelectedInv] = useState<any | null>(null);
  const [filterDecision, setFilterDecision] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchInvocations = async () => {
    try {
      const data = await api.getInvocations({
        decision: filterDecision === 'ALL' ? undefined : filterDecision,
        limit: 100,
      });
      setInvocations(data);
    } catch (err) {
      console.error('Failed to fetch invocations', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInvocations();
    const interval = setInterval(fetchInvocations, 3000);
    return () => clearInterval(interval);
  }, [filterDecision]);

  const handleInspect = async (id: string) => {
    try {
      const details = await api.getInvocationDetails(id);
      setSelectedInv(details);
    } catch (err) {
      console.error('Failed to load invocation inspection', err);
    }
  };

  const filtered = invocations.filter((inv) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      inv.tool_name.toLowerCase().includes(q) ||
      inv.server_id.toLowerCase().includes(q) ||
      inv.id.toLowerCase().includes(q)
    );
  });

  return (
    <div className="space-y-4">
      {/* Header and Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold text-white tracking-wide flex items-center space-x-2">
            <Activity className="w-5 h-5 text-cyan-400" />
            <span>Live MCP Execution Monitor</span>
          </h1>
          <p className="text-xs text-slate-400">Stream of all intercepted MCP protocol tool requests</p>
        </div>

        <div className="flex items-center space-x-2">
          {/* Decision Filter */}
          <div className="flex items-center space-x-1 sentinel-surface rounded-lg p-1 text-xs">
            {['ALL', 'ALLOW', 'BLOCK', 'REQUIRE_APPROVAL'].map((dec) => (
              <button
                key={dec}
                onClick={() => setFilterDecision(dec)}
                className={`px-2.5 py-1 rounded font-medium transition-colors ${
                  filterDecision === dec
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400/35'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {dec}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Search Bar */}
      <div className="relative">
        <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
        <input
          type="text"
          placeholder="Filter by tool name, server ID, or invocation ID..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pl-9 pr-4 py-2 sentinel-surface rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-400/50"
        />
      </div>

      {/* Invocations Table */}
      <div className="rounded-xl sentinel-surface overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/60 text-slate-400 uppercase text-[10px] tracking-wider border-b border-white/[0.08]">
              <tr>
                <th className="py-3 px-3">Time</th>
                <th className="py-3 px-3">Invocation ID</th>
                <th className="py-3 px-3">Server</th>
                <th className="py-3 px-3">Tool Call</th>
                <th className="py-3 px-3">Risk Score</th>
                <th className="py-3 px-3">Decision</th>
                <th className="py-3 px-3">Status</th>
                <th className="py-3 px-3 text-right">Inspect</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.06] text-slate-300">
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-slate-400">
                    {loading ? 'Loading tool invocations...' : 'No matching tool invocations recorded.'}
                  </td>
                </tr>
              ) : (
                filtered.map((inv) => (
                  <tr
                    key={inv.id}
                    onClick={() => handleInspect(inv.id)}
                    className="hover:bg-white/[0.04] cursor-pointer transition-colors"
                  >
                    <td className="py-2.5 px-3 font-mono text-[11px] text-slate-400">
                      {new Date(inv.created_at).toLocaleTimeString()}
                    </td>
                    <td className="py-2.5 px-3 font-mono text-cyan-400 text-[11px]">{inv.id}</td>
                    <td className="py-2.5 px-3 font-mono text-slate-400">{inv.server_id}</td>
                    <td className="py-2.5 px-3 font-mono font-medium text-white">{inv.tool_name}</td>
                    <td className="py-2.5 px-3 font-mono">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        inv.risk_score >= 80 ? 'bg-rose-950 text-rose-400 border border-rose-800' :
                        inv.risk_score >= 50 ? 'bg-amber-950 text-amber-400 border border-amber-800' :
                        'bg-slate-800 text-slate-300'
                      }`}>
                        {inv.risk_score}
                      </span>
                    </td>
                    <td className="py-2.5 px-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                        inv.decision === 'ALLOW' ? 'bg-emerald-950 text-emerald-300 border border-emerald-800' :
                        inv.decision === 'BLOCK' ? 'bg-rose-950 text-rose-300 border border-rose-800' :
                        'bg-amber-950 text-amber-300 border border-amber-800'
                      }`}>
                        {inv.decision}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 font-mono text-[11px] text-slate-400 uppercase">
                      {inv.status}
                    </td>
                    <td className="py-2.5 px-3 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleInspect(inv.id);
                        }}
                        className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-[11px] inline-flex items-center space-x-1"
                      >
                        <Eye className="w-3 h-3 text-cyan-400" />
                        <span>Inspect</span>
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Inspection Modal Drawer */}
      {selectedInv && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-md flex items-center justify-center p-4">
          <div className="w-full max-w-2xl sentinel-surface rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[85vh]">
            {/* Modal Header */}
            <div className="p-4 bg-slate-950/70 border-b border-white/[0.08] flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Terminal className="w-4 h-4 text-cyan-400" />
                <span className="font-semibold text-sm text-white">Invocation Security Deep-Dive</span>
                <span className="font-mono text-xs text-slate-400">({selectedInv.invocation.id})</span>
              </div>
              <button
                onClick={() => setSelectedInv(null)}
                className="p-1 rounded text-slate-400 hover:text-white hover:bg-white/10"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-5 space-y-4 overflow-y-auto text-xs">
              {/* Meta Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 sentinel-subsurface p-3 rounded-lg font-mono text-[11px]">
                <div>
                  <div className="text-slate-400 text-[10px]">TOOL TARGET</div>
                  <div className="text-white font-semibold">{selectedInv.invocation.tool_name}</div>
                </div>
                <div>
                  <div className="text-slate-400 text-[10px]">MCP SERVER</div>
                  <div className="text-cyan-300">{selectedInv.invocation.server_id}</div>
                </div>
                <div>
                  <div className="text-slate-400 text-[10px]">RISK SCORE</div>
                  <div className={`font-bold ${
                    selectedInv.invocation.risk_score >= 80 ? 'text-rose-400' : 'text-emerald-400'
                  }`}>
                    {selectedInv.invocation.risk_score} / 100
                  </div>
                </div>
                <div>
                  <div className="text-slate-400 text-[10px]">ENFORCEMENT</div>
                  <div className="font-bold text-white">{selectedInv.invocation.decision}</div>
                </div>
              </div>

              {/* Arguments */}
              <div>
                <div className="text-slate-400 font-semibold mb-1 text-[11px] uppercase tracking-wider">
                  Raw Invocation Arguments
                </div>
                <pre className="p-3 bg-slate-950 rounded-lg border border-slate-800 font-mono text-[11px] text-cyan-300 overflow-x-auto">
                  {JSON.stringify(selectedInv.invocation.arguments, null, 2)}
                </pre>
              </div>

              {/* Security Analysis & Triggered Rules */}
              {selectedInv.security_analysis && (
                <div>
                  <div className="text-slate-400 font-semibold mb-1 text-[11px] uppercase tracking-wider">
                    Triggered Security Rules & Threat Evidence
                  </div>
                  <div className="space-y-2">
                    {selectedInv.security_analysis.triggered_rules.length === 0 ? (
                      <div className="p-3 bg-slate-950 rounded-lg text-emerald-400 border border-emerald-950">
                        ✓ No malicious security patterns or policy violations detected.
                      </div>
                    ) : (
                      selectedInv.security_analysis.triggered_rules.map((rule: any, idx: number) => (
                        <div key={idx} className="p-2.5 bg-rose-950/20 border border-rose-900/60 rounded-lg">
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-rose-300 font-mono text-[11px]">
                              [{rule.threat_category}] {rule.rule_name}
                            </span>
                            <span className="px-1.5 py-0.2 rounded text-[10px] bg-rose-900 text-rose-200">
                              Score: {rule.risk_score}
                            </span>
                          </div>
                          <p className="text-slate-400 text-[11px] mt-1">{rule.description}</p>
                          {(rule.command_snippet || rule.matched_text || rule.target_path) && (
                            <div className="mt-1 font-mono text-[10px] text-rose-400 bg-rose-950/60 p-1 rounded">
                              Evidence: {rule.command_snippet || rule.matched_text || rule.target_path}
                            </div>
                          )}
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}

              {/* Output / Response Data */}
              <div>
                <div className="text-slate-400 font-semibold mb-1 text-[11px] uppercase tracking-wider">
                  Tool Execution Result / Sanitized Output
                </div>
                <pre className="p-3 bg-slate-950 rounded-lg border border-slate-800 font-mono text-[11px] text-slate-300 overflow-x-auto max-h-36">
                  {JSON.stringify(selectedInv.invocation.response_data, null, 2)}
                </pre>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="p-4 bg-slate-900/80 border-t border-slate-800 flex items-center justify-between">
              <span className="text-[11px] text-slate-400 font-mono">
                Duration: {selectedInv.invocation.execution_duration_ms} ms
              </span>
              <div className="flex space-x-2">
                {onAskAi && (
                  <button
                    onClick={() => {
                      onAskAi(selectedInv.invocation.id);
                      setSelectedInv(null);
                    }}
                    className="flex items-center space-x-1.5 px-3 py-1.5 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white rounded-lg text-xs font-medium"
                  >
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>Explain with AI Analyst</span>
                  </button>
                )}
                <button
                  onClick={() => setSelectedInv(null)}
                  className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
