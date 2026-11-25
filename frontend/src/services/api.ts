import type {
  DashboardOverview,
  ToolInvocation,
  SecurityAlert,
  MCPServer,
  RegisteredTool,
  ApprovalRequest,
  Policy,
  AuditLog
} from '../types';

const API_BASE = '/api';

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const token = localStorage.getItem('sentinel_token');
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options?.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.detail || `Request failed with status ${response.status}`);
  }

  return response.json();
}

export const api = {
  // Dashboard
  getDashboardOverview: () => request<DashboardOverview>('/dashboard/overview'),

  // MCP Servers
  getServers: () => request<MCPServer[]>('/mcp/servers'),
  createServer: (data: Partial<MCPServer>) => request<MCPServer>('/mcp/servers', { method: 'POST', body: JSON.stringify(data) }),
  updateServer: (id: string, data: Partial<MCPServer>) => request<MCPServer>(`/mcp/servers/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  deleteServer: (id: string) => request<void>(`/mcp/servers/${id}`, { method: 'DELETE' }),

  // Tools
  getTools: (serverId?: string) => request<RegisteredTool[]>(`/tools${serverId ? `?server_id=${serverId}` : ''}`),
  updateToolPermissions: (id: string, data: Partial<RegisteredTool>) => request<RegisteredTool>(`/tools/${id}/permissions`, { method: 'PATCH', body: JSON.stringify(data) }),

  // Invocations & Live Monitoring
  getInvocations: (params?: { decision?: string; limit?: number }) => {
    const query = new URLSearchParams();
    if (params?.decision) query.append('decision', params.decision);
    if (params?.limit) query.append('limit', params.limit.toString());
    return request<ToolInvocation[]>(`/gateway/invocations?${query.toString()}`);
  },
  getInvocationDetails: (id: string) => request<any>(`/gateway/invocations/${id}`),

  // Approvals
  getApprovals: (status?: string) => request<ApprovalRequest[]>(`/approvals${status ? `?status=${status}` : ''}`),
  approveRequest: (id: string, reason?: string) => request<ApprovalRequest>(`/approvals/${id}/approve`, { method: 'POST', body: JSON.stringify({ decision: 'APPROVE', reason }) }),
  rejectRequest: (id: string, reason?: string) => request<ApprovalRequest>(`/approvals/${id}/reject`, { method: 'POST', body: JSON.stringify({ decision: 'REJECT', reason }) }),

  // Security Alerts
  getAlerts: (status?: string) => request<SecurityAlert[]>(`/security/alerts${status ? `?status=${status}` : ''}`),
  updateAlertStatus: (id: string, status: string) => request<SecurityAlert>(`/security/alerts/${id}`, { method: 'PATCH', body: JSON.stringify({ status }) }),
  scanPayload: (payload: Record<string, any>, tool_name = 'custom_tool') => request<any>(`/security/scan?tool_name=${encodeURIComponent(tool_name)}`, { method: 'POST', body: JSON.stringify(payload) }),

  // Policies
  getPolicies: () => request<Policy[]>('/policies'),
  updatePolicy: (id: string, data: Partial<Policy>) => request<Policy>(`/policies/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),

  // Audit Logs
  getAuditLogs: (limit = 100) => request<AuditLog[]>(`/audit/logs?limit=${limit}`),
  verifyAuditChain: () => request<{ status: string; total_records: number; chain_head_hash?: string; message: string }>('/audit/verify-chain'),

  // AI Security Analyst
  explainInvocation: (id: string) => request<any>(`/ai/explain-invocation/${id}`, { method: 'POST' }),
  askAnalyst: (query: string) => request<any>('/ai/ask', { method: 'POST', body: JSON.stringify({ query }) }),

  // Demonstration Scenarios
  runDemoScenario: (scenarioId: string) => request<any>(`/demo/run-scenario/${scenarioId}`, { method: 'POST' }),
};
