import React from 'react';
import {
  LayoutDashboard,
  Activity,
  AlertTriangle,
  Server,
  CheckSquare,
  Sliders,
  FileText,
  Sparkles,
  PlayCircle,
  Settings as SettingsIcon
} from 'lucide-react';

export type TabType = 
  | 'overview'
  | 'monitoring'
  | 'alerts'
  | 'tools'
  | 'approvals'
  | 'policies'
  | 'audit'
  | 'analyst'
  | 'scenarios'
  | 'settings';

interface SidebarProps {
  currentTab: TabType;
  onSelectTab: (tab: TabType) => void;
  pendingApprovalsCount: number;
  criticalAlertsCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onSelectTab,
  pendingApprovalsCount,
  criticalAlertsCount
}) => {
  const menuItems = [
    { id: 'overview' as TabType, label: 'Overview', icon: LayoutDashboard },
    { id: 'monitoring' as TabType, label: 'Live Monitoring', icon: Activity },
    { 
      id: 'alerts' as TabType, 
      label: 'Security Alerts', 
      icon: AlertTriangle,
      badge: criticalAlertsCount > 0 ? criticalAlertsCount : null,
      badgeColor: 'bg-rose-500 text-white'
    },
    { id: 'tools' as TabType, label: 'Tool Registry', icon: Server },
    { 
      id: 'approvals' as TabType, 
      label: 'Approval Center', 
      icon: CheckSquare,
      badge: pendingApprovalsCount > 0 ? pendingApprovalsCount : null,
      badgeColor: 'bg-amber-500 text-slate-950 font-bold'
    },
    { id: 'policies' as TabType, label: 'Policy Engine', icon: Sliders },
    { id: 'audit' as TabType, label: 'Audit & Forensics', icon: FileText },
    { id: 'analyst' as TabType, label: 'AI Security Analyst', icon: Sparkles },
    { id: 'scenarios' as TabType, label: 'Live Scenarios (A-F)', icon: PlayCircle },
    { id: 'settings' as TabType, label: 'Settings', icon: SettingsIcon },
  ];

  return (
    <aside className="w-64 sentinel-shell-sidebar flex flex-col justify-between p-3 select-none">
      <div className="space-y-1">
        <div className="px-3 py-2 text-[11px] font-semibold tracking-wider text-slate-400/90 uppercase">
          Security Operations
        </div>

        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                isActive
                  ? 'bg-gradient-to-r from-cyan-500/18 via-cyan-500/10 to-indigo-500/10 text-cyan-300 border border-cyan-400/35 shadow-lg shadow-cyan-500/10'
                  : 'text-slate-300 hover:bg-white/[0.04] hover:text-white border border-transparent'
              }`}
            >
              <div className="flex items-center space-x-3">
                <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-300' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </div>

              {item.badge && (
                <span className={`px-1.5 py-0.2 rounded-full text-[10px] ${item.badgeColor}`}>
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      <div className="p-3 rounded-xl sentinel-subsurface text-xs">
        <div className="flex items-center justify-between text-slate-400 mb-1.5 text-[11px]">
          <span>Protection Mode</span>
          <span className="text-emerald-400 font-mono font-semibold">DETERMINISTIC</span>
        </div>
        <p className="text-[11px] text-slate-400 leading-relaxed">
          Zero-trust tool execution enforcement. All MCP calls evaluated against security baselines.
        </p>
      </div>
    </aside>
  );
};
