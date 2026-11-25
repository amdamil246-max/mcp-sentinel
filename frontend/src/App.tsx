import { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import type { TabType } from './components/Sidebar';
import { Overview } from './pages/Overview';
import { LiveMonitoring } from './pages/LiveMonitoring';
import { SecurityAlerts } from './pages/SecurityAlerts';
import { ToolRegistry } from './pages/ToolRegistry';
import { ApprovalCenter } from './pages/ApprovalCenter';
import { PolicyManagement } from './pages/PolicyManagement';
import { AuditLogs } from './pages/AuditLogs';
import { AiAnalyst } from './pages/AiAnalyst';
import { ScenariosDemo } from './pages/ScenariosDemo';
import { Settings } from './pages/Settings';
import { api } from './services/api';

export function App() {
  const [currentTab, setCurrentTab] = useState<TabType>('overview');
  const [pendingApprovalsCount, setPendingApprovalsCount] = useState<number>(0);
  const [criticalAlertsCount, setCriticalAlertsCount] = useState<number>(0);

  const refreshBadges = async () => {
    try {
      const [apprList, alertList] = await Promise.all([
        api.getApprovals('PENDING'),
        api.getAlerts('NEW')
      ]);
      setPendingApprovalsCount(apprList.length);
      const crit = alertList.filter((a) => a.severity === 'Critical' || a.severity === 'High');
      setCriticalAlertsCount(crit.length);
    } catch {
      // Ignore background badge errors
    }
  };

  useEffect(() => {
    refreshBadges();
    const interval = setInterval(refreshBadges, 4000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen sentinel-canvas text-slate-100 flex flex-col font-sans relative isolate">
      {/* Atmospheric background layers */}
      <div className="sentinel-aurora-orb sentinel-aurora-orb--cyan" aria-hidden="true" />
      <div className="sentinel-aurora-orb sentinel-aurora-orb--indigo" aria-hidden="true" />
      <div className="sentinel-aurora-orb sentinel-aurora-orb--emerald" aria-hidden="true" />
      <div className="sentinel-grid-overlay" aria-hidden="true" />
      <div className="sentinel-vignette" aria-hidden="true" />

      <div className="relative z-10 flex flex-col min-h-screen">
        <Navbar onOpenDemo={() => setCurrentTab('scenarios')} />

        <div className="flex-1 flex overflow-hidden">
          <Sidebar
            currentTab={currentTab}
            onSelectTab={(tab) => setCurrentTab(tab)}
            pendingApprovalsCount={pendingApprovalsCount}
            criticalAlertsCount={criticalAlertsCount}
          />

          <main className="flex-1 overflow-y-auto p-6 bg-transparent">
            {currentTab === 'overview' && <Overview onNavigate={setCurrentTab} />}
            {currentTab === 'monitoring' && <LiveMonitoring onAskAi={() => setCurrentTab('analyst')} />}
            {currentTab === 'alerts' && <SecurityAlerts onGenerateReport={() => setCurrentTab('analyst')} />}
            {currentTab === 'tools' && <ToolRegistry />}
            {currentTab === 'approvals' && <ApprovalCenter />}
            {currentTab === 'policies' && <PolicyManagement />}
            {currentTab === 'audit' && <AuditLogs />}
            {currentTab === 'analyst' && <AiAnalyst />}
            {currentTab === 'scenarios' && <ScenariosDemo />}
            {currentTab === 'settings' && <Settings />}
          </main>
        </div>
      </div>
    </div>
  );
}

export default App;
