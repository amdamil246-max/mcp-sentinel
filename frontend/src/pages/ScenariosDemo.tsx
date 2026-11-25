import React, { useState } from 'react';
import { api } from '../services/api';
import {
  Play,
  PlayCircle,
  Terminal,
  RefreshCw,
  CheckCircle2
} from 'lucide-react';

interface ScenarioMeta {
  id: string;
  name: string;
  category: string;
  expectedDecision: string;
  description: string;
  badgeColor: string;
}

const SCENARIOS: ScenarioMeta[] = [
  {
    id: 'A',
    name: 'Normal Operation',
    category: 'System Diagnostics',
    expectedDecision: 'ALLOW',
    description: 'AI agent queries system performance and firewall status. Risk score evaluates to Low and execution is allowed.',
    badgeColor: 'bg-emerald-950 text-emerald-300 border-emerald-800'
  },
  {
    id: 'B',
    name: 'Dangerous Destructive Command',
    category: 'Command Injection Defense',
    expectedDecision: 'BLOCK',
    description: 'AI agent attempts recursive filesystem wipe (rm -rf /) and download-execute pipeline. Intercepted and blocked before reaching server.',
    badgeColor: 'bg-rose-950 text-rose-300 border-rose-800'
  },
  {
    id: 'C',
    name: 'Sensitive File Access',
    category: 'Filesystem Boundary Protection',
    expectedDecision: 'BLOCK',
    description: 'AI agent attempts directory traversal (../../app/.env) to exfiltrate secret environment credentials. Denied at firewall gateway.',
    badgeColor: 'bg-rose-950 text-rose-300 border-rose-800'
  },
  {
    id: 'D',
    name: 'Prompt Injection in Tool Response',
    category: 'Response Inspection Engine',
    expectedDecision: 'BLOCK_RESPONSE',
    description: 'External tool payload contains hostile jailbreak instructions attempting to hijack agent behavior. Blocked at response firewall.',
    badgeColor: 'bg-orange-950 text-orange-300 border-orange-800'
  },
  {
    id: 'E',
    name: 'Human Approval for Sensitive Action',
    category: 'Human-in-the-Loop Workflow',
    expectedDecision: 'REQUIRE_APPROVAL',
    description: 'High-impact write operation requires explicit human administrator authorization before execution.',
    badgeColor: 'bg-amber-950 text-amber-300 border-amber-800'
  },
  {
    id: 'F',
    name: 'Secret Exposure and Auto-Redaction',
    category: 'Data Exfiltration Defense',
    expectedDecision: 'REDACT_SENSITIVE_DATA',
    description: 'Tool response returns simulated third-party API keys. Redaction engine scrubs credentials before returning output.',
    badgeColor: 'bg-cyan-950 text-cyan-300 border-cyan-800'
  }
];

export const ScenariosDemo: React.FC = () => {
  const [runningId, setRunningId] = useState<string | null>(null);
  const [results, setResults] = useState<Record<string, any>>({});
  const [activeOutputScenario, setActiveOutputScenario] = useState<string | null>('A');

  const executeScenario = async (id: string) => {
    try {
      setRunningId(id);
      const res = await api.runDemoScenario(id);
      setResults((prev) => ({ ...prev, [id]: res }));
      setActiveOutputScenario(id);
    } catch (err: any) {
      setResults((prev) => ({ ...prev, [id]: { error: err.message } }));
    } finally {
      setRunningId(null);
    }
  };

  const handleRunAll = async () => {
    for (const sc of SCENARIOS) {
      await executeScenario(sc.id);
    }
  };

  const currentResult = activeOutputScenario ? results[activeOutputScenario] : null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold text-white tracking-wide flex items-center space-x-2">
            <PlayCircle className="w-5 h-5 text-cyan-400" />
            <span>Master Demonstration Environment</span>
          </h1>
          <p className="text-xs text-slate-400">
            Reproducible end-to-end security scenarios demonstrating real-time threat interception
          </p>
        </div>

        <button
          onClick={handleRunAll}
          disabled={runningId !== null}
          className="flex items-center space-x-1.5 px-4 py-2 bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white rounded-lg text-xs font-semibold shadow-lg shadow-cyan-950/40 transition-all disabled:opacity-50"
        >
          <Play className="w-3.5 h-3.5" />
          <span>Execute All Scenarios (A - F)</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Scenarios Selection List */}
        <div className="space-y-3">
          {SCENARIOS.map((sc) => {
            const hasResult = !!results[sc.id];
            const isSelected = activeOutputScenario === sc.id;
            const isCurrentRunning = runningId === sc.id;

            return (
              <div
                key={sc.id}
                onClick={() => setActiveOutputScenario(sc.id)}
                className={`p-4 rounded-xl cursor-pointer transition-all ${
                  isSelected
                    ? 'sentinel-surface border-cyan-400/60 shadow-lg shadow-cyan-500/15'
                    : 'sentinel-surface-interactive opacity-90 hover:opacity-100'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2.5">
                    <span className="w-6 h-6 rounded-md sentinel-subsurface flex items-center justify-center font-mono font-bold text-xs text-cyan-300">
                      {sc.id}
                    </span>
                    <span className="font-semibold text-white text-sm">{sc.name}</span>
                  </div>

                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-semibold ${sc.badgeColor}`}>
                      {sc.expectedDecision}
                    </span>
                    <button
                      disabled={runningId !== null}
                      onClick={(e) => {
                        e.stopPropagation();
                        executeScenario(sc.id);
                      }}
                      className="px-2.5 py-1 bg-cyan-500/15 hover:bg-cyan-500/25 text-cyan-300 border border-cyan-400/35 rounded text-xs flex items-center space-x-1 transition-colors"
                    >
                      <Play className={`w-3 h-3 ${isCurrentRunning ? 'animate-spin' : ''}`} />
                      <span>{isCurrentRunning ? 'Testing...' : 'Run'}</span>
                    </button>
                  </div>
                </div>

                <p className="text-xs text-slate-300 mt-2 leading-relaxed">{sc.description}</p>

                {hasResult && (
                  <div className="flex items-center space-x-1.5 mt-2.5 text-[11px] text-emerald-400 font-mono">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Scenario executed. Click to inspect live output.</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Live Execution Output Panel */}
        <div className="p-5 rounded-xl sentinel-surface flex flex-col justify-between">
          <div className="space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-white/[0.08]">
              <div className="flex items-center space-x-2">
                <Terminal className="w-4 h-4 text-cyan-400" />
                <span className="font-semibold text-white text-sm">
                  Live Gateway Telemetry {activeOutputScenario ? `(Scenario ${activeOutputScenario})` : ''}
                </span>
              </div>
              {runningId && (
                <span className="text-xs text-cyan-400 flex items-center space-x-1 animate-pulse font-mono">
                  <RefreshCw className="w-3 h-3 animate-spin" />
                  <span>Evaluating Policies...</span>
                </span>
              )}
            </div>

            {!currentResult ? (
              <div className="py-20 text-center text-slate-400 text-xs">
                Select a scenario and click "Run" to view intercepted tool telemetry, risk scores, and enforcement decisions.
              </div>
            ) : (
              <div className="space-y-3 text-xs">
                {/* Result Status Highlights */}
                {currentResult.execution && (
                  <div className="grid grid-cols-2 gap-2 sentinel-subsurface p-3 rounded-lg font-mono text-[11px]">
                    <div>
                      <span className="text-slate-400 block text-[10px]">ENFORCEMENT DECISION</span>
                      <span className={`font-bold ${
                        currentResult.execution.decision === 'ALLOW' ? 'text-emerald-400' :
                        currentResult.execution.decision === 'BLOCK' ? 'text-rose-400' :
                        'text-amber-400'
                      }`}>
                        {currentResult.execution.decision}
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-400 block text-[10px]">RISK SCORE</span>
                      <span className="text-white font-bold">{currentResult.execution.risk_score} / 100</span>
                    </div>
                  </div>
                )}

                {/* Response Inspection Highlights */}
                {currentResult.inspection_result && (
                  <div className="sentinel-subsurface p-3 rounded-lg font-mono text-[11px] space-y-1">
                    <div className="text-cyan-400 font-bold">
                      RESPONSE ACTION: {currentResult.inspection_result.action}
                    </div>
                    <div className="text-slate-300">
                      {currentResult.inspection_result.explanation}
                    </div>
                  </div>
                )}

                {/* Detailed Raw Payload */}
                <div>
                  <div className="text-slate-400 text-[11px] uppercase font-semibold mb-1">
                    Telemetry JSON Payload
                  </div>
                  <pre className="p-3 sentinel-subsurface rounded-lg font-mono text-[11px] text-cyan-300 overflow-x-auto max-h-80">
                    {JSON.stringify(currentResult, null, 2)}
                  </pre>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
