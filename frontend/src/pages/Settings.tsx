import React from 'react';
import {
  Settings as SettingsIcon,
  Server,
  Database,
  Users,
  Sparkles
} from 'lucide-react';

export const Settings: React.FC = () => {
  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-white tracking-wide flex items-center space-x-2">
          <SettingsIcon className="w-5 h-5 text-cyan-400" />
          <span>Platform & Security Engine Settings</span>
        </h1>
        <p className="text-xs text-slate-400">
          Environment configuration, AI advisory engine, and gateway runtime parameters
        </p>
      </div>

      {/* Grid of Settings Categories */}
      <div className="space-y-4">
        {/* Gateway Config */}
        <div className="p-5 rounded-xl sentinel-surface space-y-3">
          <div className="flex items-center space-x-2 text-white font-semibold text-sm">
            <Server className="w-4 h-4 text-cyan-400" />
            <span>MCP Security Gateway Configuration</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs font-mono">
            <div className="p-3 sentinel-subsurface rounded-lg">
              <span className="text-slate-400 text-[10px] block">GATEWAY HOST</span>
              <span className="text-cyan-300 font-bold">0.0.0.0</span>
            </div>
            <div className="p-3 sentinel-subsurface rounded-lg">
              <span className="text-slate-400 text-[10px] block">LISTEN PORT</span>
              <span className="text-cyan-300 font-bold">8000</span>
            </div>
            <div className="p-3 sentinel-subsurface rounded-lg">
              <span className="text-slate-400 text-[10px] block">APPROVAL TIMEOUT</span>
              <span className="text-cyan-300 font-bold">300 seconds</span>
            </div>
          </div>
        </div>

        {/* AI Provider Config */}
        <div className="p-5 rounded-xl sentinel-surface space-y-3">
          <div className="flex items-center space-x-2 text-white font-semibold text-sm">
            <Sparkles className="w-4 h-4 text-violet-400" />
            <span>AI Security Analyst Integration</span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Provider abstraction layer. Supports Google Gemini API, OpenAI, and local/heuristic advisory models.
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs font-mono">
            <div className="p-3 sentinel-subsurface rounded-lg">
              <span className="text-slate-400 text-[10px] block">ACTIVE PROVIDER</span>
              <span className="text-violet-300 font-bold">gemini / heuristic</span>
            </div>
            <div className="p-3 sentinel-subsurface rounded-lg">
              <span className="text-slate-400 text-[10px] block">DEFAULT MODEL</span>
              <span className="text-violet-300 font-bold">gemini-1.5-pro</span>
            </div>
            <div className="p-3 sentinel-subsurface rounded-lg">
              <span className="text-slate-400 text-[10px] block">SECRET SCRUBBING</span>
              <span className="text-emerald-400 font-bold">ACTIVE (Pre-LLM)</span>
            </div>
          </div>
        </div>

        {/* Database & Audit Retention */}
        <div className="p-5 rounded-xl sentinel-surface space-y-3">
          <div className="flex items-center space-x-2 text-white font-semibold text-sm">
            <Database className="w-4 h-4 text-emerald-400" />
            <span>Persistence & Tamper-Evident Forensics</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs font-mono">
            <div className="p-3 sentinel-subsurface rounded-lg">
              <span className="text-slate-400 text-[10px] block">DATABASE ENGINE</span>
              <span className="text-emerald-300 font-bold">SQLite / PostgreSQL</span>
            </div>
            <div className="p-3 sentinel-subsurface rounded-lg">
              <span className="text-slate-400 text-[10px] block">AUDIT RETENTION</span>
              <span className="text-emerald-300 font-bold">365 Days (Append-Only)</span>
            </div>
            <div className="p-3 sentinel-subsurface rounded-lg">
              <span className="text-slate-400 text-[10px] block">HASH CHAINING</span>
              <span className="text-emerald-400 font-bold">SHA-256 GENESIS</span>
            </div>
          </div>
        </div>

        {/* Active RBAC Roles */}
        <div className="p-5 rounded-xl sentinel-surface space-y-3">
          <div className="flex items-center space-x-2 text-white font-semibold text-sm">
            <Users className="w-4 h-4 text-cyan-400" />
            <span>Role-Based Access Control (RBAC)</span>
          </div>
          <div className="space-y-2 text-xs">
            <div className="flex items-center justify-between p-2.5 rounded-lg sentinel-subsurface">
              <div>
                <span className="font-bold text-white font-mono">ADMINISTRATOR</span>
                <p className="text-[11px] text-slate-400">Full platform control, policy modifications, tool authorization authority.</p>
              </div>
              <span className="text-emerald-400 font-mono text-[10px] bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/30">ACTIVE</span>
            </div>
            <div className="flex items-center justify-between p-2.5 rounded-lg sentinel-subsurface">
              <div>
                <span className="font-bold text-white font-mono">SECURITY_ANALYST</span>
                <p className="text-[11px] text-slate-400">Investigate alerts, run payload scans, generate incident reports.</p>
              </div>
              <span className="text-cyan-400 font-mono text-[10px] bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/30">ACTIVE</span>
            </div>
            <div className="flex items-center justify-between p-2.5 rounded-lg sentinel-subsurface">
              <div>
                <span className="font-bold text-white font-mono">VIEWER</span>
                <p className="text-[11px] text-slate-400">Read-only monitoring dashboard access.</p>
              </div>
              <span className="text-slate-400 font-mono text-[10px] bg-slate-800/70 px-2 py-0.5 rounded border border-white/10">ACTIVE</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
