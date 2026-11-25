import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import type { Policy } from '../types';
import {
  Sliders,
  Shield,
  Lock,
  RefreshCw,
  SlidersHorizontal
} from 'lucide-react';

export const PolicyManagement: React.FC = () => {
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [loading, setLoading] = useState(true);
  const [autoBlockThreshold, setAutoBlockThreshold] = useState(80);
  const [approvalThreshold, setApprovalThreshold] = useState(50);

  const fetchPolicies = async () => {
    try {
      setLoading(true);
      const data = await api.getPolicies();
      setPolicies(data);
    } catch (err) {
      console.error('Failed to load policies', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPolicies();
  }, []);

  const handleTogglePolicy = async (policy: Policy) => {
    try {
      await api.updatePolicy(policy.id, {
        is_active: !policy.is_active,
        change_summary: `Toggled policy state to ${!policy.is_active}`
      });
      fetchPolicies();
    } catch (err) {
      console.error('Failed to update policy', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold text-white tracking-wide flex items-center space-x-2">
            <Sliders className="w-5 h-5 text-cyan-400" />
            <span>Policy Enforcement Engine Configuration</span>
          </h1>
          <p className="text-xs text-slate-400">
            Define mandatory security rules, risk threshold boundaries, and containment baselines
          </p>
        </div>

        <button
          onClick={fetchPolicies}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg sentinel-subsurface hover:border-cyan-400/30 text-slate-200 text-xs self-start sm:self-auto transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5 text-cyan-400" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Threshold Controls */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Auto Block Slider */}
        <div className="p-4 rounded-xl sentinel-surface-interactive border-rose-500/25 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Shield className="w-4 h-4 text-rose-400" />
              <span className="text-xs font-semibold text-white">Auto-Block Critical Threshold</span>
            </div>
            <span className="text-sm font-mono font-bold text-rose-400">{autoBlockThreshold} / 100</span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Tool invocations evaluating to or above this score are blocked instantly without hitting destination servers.
          </p>
          <input
            type="range"
            min="60"
            max="100"
            value={autoBlockThreshold}
            onChange={(e) => setAutoBlockThreshold(Number(e.target.value))}
            className="w-full accent-rose-500 cursor-pointer"
          />
        </div>

        {/* Require Approval Slider */}
        <div className="p-4 rounded-xl sentinel-surface-interactive border-amber-500/25 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Lock className="w-4 h-4 text-amber-400" />
              <span className="text-xs font-semibold text-white">Human Approval Threshold</span>
            </div>
            <span className="text-sm font-mono font-bold text-amber-400">{approvalThreshold} / 100</span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Operations scoring between this threshold and auto-block require explicit administrator sign-off.
          </p>
          <input
            type="range"
            min="30"
            max="79"
            value={approvalThreshold}
            onChange={(e) => setApprovalThreshold(Number(e.target.value))}
            className="w-full accent-amber-500 cursor-pointer"
          />
        </div>
      </div>

      {/* Active Baseline Security Policies */}
      <div className="space-y-3">
        <h2 className="text-sm font-semibold text-white flex items-center space-x-2">
          <SlidersHorizontal className="w-4 h-4 text-cyan-400" />
          <span>Active Enforcement Rules</span>
        </h2>

        <div className="space-y-3">
          {loading ? (
            <div className="p-8 text-center text-xs text-slate-400">Loading security policies...</div>
          ) : policies.map((pol) => (
            <div
              key={pol.id}
              className={`p-4 rounded-xl transition-all ${pol.is_active
                  ? 'sentinel-surface-interactive'
                  : 'sentinel-subsurface opacity-60'
                }`}
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center space-x-2.5">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${pol.rule_type === 'deny' ? 'bg-rose-950 text-rose-300 border border-rose-800' :
                      pol.rule_type === 'require_approval' ? 'bg-amber-950 text-amber-300 border border-amber-800' :
                        'bg-cyan-950 text-cyan-300 border border-cyan-800'
                    }`}>
                    {pol.rule_type.toUpperCase()}
                  </span>
                  <span className="font-semibold text-white text-sm">{pol.name}</span>
                  <span className="text-[11px] font-mono text-cyan-400">({pol.id})</span>
                </div>

                <div className="flex items-center space-x-3">
                  <span className="text-[11px] font-mono text-slate-400 uppercase">
                    Priority: {pol.priority}
                  </span>
                  <button
                    onClick={() => handleTogglePolicy(pol)}
                    className={`px-3 py-1 rounded text-xs font-semibold transition-colors ${pol.is_active
                        ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                        : 'bg-slate-900 text-slate-500 border border-slate-800'
                      }`}
                  >
                    {pol.is_active ? 'ACTIVE' : 'DISABLED'}
                  </button>
                </div>
              </div>

              <p className="text-xs text-slate-300 mt-2">{pol.description}</p>

              {pol.configuration && (
                <div className="mt-3 p-2 bg-slate-950 rounded border border-slate-800/80 font-mono text-[11px] text-cyan-400 overflow-x-auto">
                  Config: {JSON.stringify(pol.configuration)}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
