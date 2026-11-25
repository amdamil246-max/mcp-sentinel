import React from 'react';
import { Shield, Terminal } from 'lucide-react';

interface NavbarProps {
  onOpenDemo: () => void;
  activeScenarioRunning?: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ onOpenDemo, activeScenarioRunning }) => {
  return (
    <header className="h-16 sentinel-shell-navbar px-6 flex items-center justify-between sticky top-0 z-40">
      <div className="flex items-center space-x-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500/90 via-blue-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-cyan-500/25 border border-cyan-300/30">
          <Shield className="w-5 h-5 text-white drop-shadow" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <span className="font-bold text-lg tracking-wider bg-gradient-to-r from-white via-cyan-100 to-slate-300 bg-clip-text text-transparent">
              MCP SENTINEL
            </span>
            <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-400/30">
              v1.0-GATEWAY
            </span>
          </div>
          <p className="text-xs text-slate-400">Security Firewall & Execution Protection for AI Agents</p>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        {/* Status indicator */}
        <div className="hidden sm:flex items-center space-x-2 px-3 py-1.5 rounded-full sentinel-subsurface text-xs">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span className="text-slate-200 font-medium">Gateway Active</span>
          <span className="text-slate-500 font-mono">| 8000</span>
        </div>

        {/* Quick Demo Trigger */}
        <button
          onClick={onOpenDemo}
          className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
            activeScenarioRunning
              ? 'bg-amber-600/20 text-amber-300 border border-amber-500/40 animate-pulse'
              : 'bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white shadow-lg shadow-cyan-500/20 border border-cyan-300/20'
          }`}
        >
          <Terminal className="w-3.5 h-3.5" />
          <span>Demo Scenarios (A-F)</span>
        </button>

        {/* User Badge */}
        <div className="flex items-center space-x-2 border-l border-white/10 pl-4">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-slate-800 to-slate-900 flex items-center justify-center text-cyan-300 font-bold text-xs border border-cyan-400/25 shadow-inner">
            SA
          </div>
          <div className="hidden md:block text-left text-xs">
            <div className="font-semibold text-slate-200">Security Admin</div>
            <div className="text-[10px] text-emerald-400 font-mono">ENFORCING</div>
          </div>
        </div>
      </div>
    </header>
  );
};
