import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import type { MCPServer, RegisteredTool } from '../types';
import {
  Server,
  RefreshCw,
  Layers,
  Lock,
  Eye
} from 'lucide-react';

export const ToolRegistry: React.FC = () => {
  const [servers, setServers] = useState<MCPServer[]>([]);
  const [tools, setTools] = useState<RegisteredTool[]>([]);
  const [selectedServer, setSelectedServer] = useState<string>('ALL');
  const [selectedToolSchema, setSelectedToolSchema] = useState<RegisteredTool | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [srvList, toolList] = await Promise.all([
        api.getServers(),
        api.getTools(selectedServer === 'ALL' ? undefined : selectedServer)
      ]);
      setServers(srvList);
      setTools(toolList);
    } catch (err) {
      console.error('Failed to load tool registry data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [selectedServer]);

  const handleToggleApproval = async (tool: RegisteredTool) => {
    try {
      await api.updateToolPermissions(tool.id, {
        requires_approval: !tool.requires_approval
      });
      fetchData();
    } catch (err) {
      console.error('Failed to update approval requirement', err);
    }
  };

  const handleTrustChange = async (toolId: string, newTrust: any) => {
    try {
      await api.updateToolPermissions(toolId, { trust_level: newTrust });
      fetchData();
    } catch (err) {
      console.error('Failed to update trust level', err);
    }
  };

  const handlePermissionChange = async (toolId: string, newPerm: any) => {
    try {
      await api.updateToolPermissions(toolId, { permission_level: newPerm });
      fetchData();
    } catch (err) {
      console.error('Failed to update permission level', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold text-white tracking-wide flex items-center space-x-2">
            <Server className="w-5 h-5 text-cyan-400" />
            <span>MCP Server & Tool Registry</span>
          </h1>
          <p className="text-xs text-slate-400">Discover, configure trust boundaries, and enforce permissions on AI agent tools</p>
        </div>

        <button
          onClick={fetchData}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg sentinel-subsurface hover:border-cyan-400/30 text-slate-200 text-xs self-start sm:self-auto transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5 text-cyan-400" />
          <span>Refresh Fleet</span>
        </button>
      </div>

      {/* Upstream MCP Servers Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {servers.map((srv) => (
          <div key={srv.id} className="p-4 rounded-xl sentinel-surface-interactive space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2.5">
                <div className="w-8 h-8 rounded-lg bg-cyan-500/15 border border-cyan-400/30 flex items-center justify-center text-cyan-300">
                  <Server className="w-4 h-4" />
                </div>
                <div>
                  <div className="font-semibold text-white text-sm">{srv.name}</div>
                  <div className="text-[11px] font-mono text-cyan-400">{srv.id}</div>
                </div>
              </div>

              <div className="flex items-center space-x-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-500 shadow-sm shadow-emerald-400"></span>
                <span className="text-[11px] font-mono text-emerald-400 uppercase">{srv.health_status}</span>
              </div>
            </div>

            <p className="text-xs text-slate-400">{srv.description}</p>

            <div className="flex items-center justify-between pt-2 border-t border-white/[0.08] text-[11px] text-slate-400 font-mono">
              <span>Transport: {srv.connection_type.toUpperCase()}</span>
              <span>Registered Tools: {srv.tool_count}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Registered Tools Table */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-white flex items-center space-x-2">
            <Layers className="w-4 h-4 text-cyan-400" />
            <span>Active Tool Policies & Trust Tiers</span>
          </h2>

          <select
            value={selectedServer}
            onChange={(e) => setSelectedServer(e.target.value)}
            className="sentinel-subsurface rounded-lg px-2.5 py-1 text-slate-300 text-xs focus:outline-none"
          >
            <option value="ALL">All MCP Servers</option>
            {servers.map((s) => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
          </select>
        </div>

        <div className="rounded-xl sentinel-surface overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/60 text-slate-400 uppercase text-[10px] tracking-wider border-b border-white/[0.08]">
                <tr>
                  <th className="py-3 px-3">Tool Name</th>
                  <th className="py-3 px-3">Server Origin</th>
                  <th className="py-3 px-3">Capability</th>
                  <th className="py-3 px-3">Trust Tier</th>
                  <th className="py-3 px-3">Human Approval</th>
                  <th className="py-3 px-3 text-right">Schema</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.06] text-slate-300">
                {loading ? (
                  <tr>
                    <td colSpan={6} className="py-8 text-center text-slate-400">Loading tools...</td>
                  </tr>
                ) : tools.map((tool) => (
                  <tr key={tool.id} className="hover:bg-white/[0.03] transition-colors">
                    <td className="py-3 px-3 font-mono font-medium text-white">{tool.name}</td>
                    <td className="py-3 px-3 font-mono text-cyan-400">{tool.server_id}</td>
                    <td className="py-3 px-3">
                      <select
                        value={tool.permission_level}
                        onChange={(e) => handlePermissionChange(tool.id, e.target.value)}
                        className="bg-slate-950 border border-slate-800 rounded px-2 py-0.5 text-[11px] font-mono text-slate-300"
                      >
                        <option value="read">read</option>
                        <option value="write">write</option>
                        <option value="execute">execute</option>
                        <option value="admin">admin</option>
                      </select>
                    </td>
                    <td className="py-3 px-3">
                      <select
                        value={tool.trust_level}
                        onChange={(e) => handleTrustChange(tool.id, e.target.value)}
                        className={`border rounded px-2 py-0.5 text-[11px] font-mono font-semibold ${
                          tool.trust_level === 'trusted' ? 'bg-emerald-950 text-emerald-300 border-emerald-800' :
                          tool.trust_level === 'monitored' ? 'bg-blue-950 text-blue-300 border-blue-800' :
                          tool.trust_level === 'untrusted' ? 'bg-amber-950 text-amber-300 border-amber-800' :
                          'bg-rose-950 text-rose-300 border-rose-800'
                        }`}
                      >
                        <option value="trusted">trusted</option>
                        <option value="monitored">monitored</option>
                        <option value="untrusted">untrusted</option>
                        <option value="blocked">blocked</option>
                      </select>
                    </td>
                    <td className="py-3 px-3">
                      <button
                        onClick={() => handleToggleApproval(tool)}
                        className={`px-2.5 py-1 rounded text-[11px] font-mono transition-colors flex items-center space-x-1.5 ${
                          tool.requires_approval
                            ? 'bg-amber-950 text-amber-300 border border-amber-800'
                            : 'bg-slate-900 text-slate-400 border border-slate-800'
                        }`}
                      >
                        <Lock className="w-3 h-3" />
                        <span>{tool.requires_approval ? 'REQUIRED' : 'AUTO-ENFORCED'}</span>
                      </button>
                    </td>
                    <td className="py-3 px-3 text-right">
                      <button
                        onClick={() => setSelectedToolSchema(tool)}
                        className="p-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300"
                      >
                        <Eye className="w-3.5 h-3.5 text-cyan-400" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Schema Modal */}
      {selectedToolSchema && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-md flex items-center justify-center p-4">
          <div className="w-full max-w-lg sentinel-surface rounded-2xl p-5 shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-white/[0.08]">
              <span className="font-semibold text-white text-sm">Tool JSON Schema ({selectedToolSchema.name})</span>
              <button
                onClick={() => setSelectedToolSchema(null)}
                className="text-slate-400 hover:text-white"
              >
                ✕
              </button>
            </div>
            <pre className="p-3 sentinel-subsurface rounded-lg text-cyan-300 font-mono text-[11px] overflow-x-auto max-h-72">
              {JSON.stringify(selectedToolSchema.input_schema, null, 2)}
            </pre>
            <div className="flex justify-end">
              <button
                onClick={() => setSelectedToolSchema(null)}
                className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
