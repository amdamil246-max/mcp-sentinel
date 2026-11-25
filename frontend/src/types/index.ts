export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string | null;
  role: string;
  is_active: boolean;
  created_at: string;
}

export interface MCPServer {
  id: string;
  name: string;
  description: string | null;
  connection_type: string;
  command: string | null;
  args: string[];
  url: string | null;
  is_enabled: boolean;
  health_status: 'healthy' | 'degraded' | 'offline';
  last_connected_at: string | null;
  tool_count: number;
  created_at: string;
  updated_at: string;
}

export interface RegisteredTool {
  id: string;
  server_id: string;
  name: string;
  description: string | null;
  input_schema: Record<string, any>;
  permission_level: 'read' | 'write' | 'execute' | 'admin';
  trust_level: 'trusted' | 'monitored' | 'untrusted' | 'blocked';
  is_enabled: boolean;
  requires_approval: boolean;
  created_at: string;
  updated_at: string;
}

export interface ToolInvocation {
  id: string;
  session_id: string | null;
  user_id: string | null;
  server_id: string;
  tool_name: string;
  arguments: Record<string, any>;
  status: string;
  risk_score: number;
  risk_classification: 'Low' | 'Guarded' | 'Medium' | 'High' | 'Critical';
  decision: 'ALLOW' | 'BLOCK' | 'REQUIRE_APPROVAL';
  approval_status: string;
  execution_status: string;
  response_data: any;
  execution_duration_ms: number;
  created_at: string;
}

export interface SecurityAlert {
  id: string;
  invocation_id: string | null;
  threat_category: string;
  severity: 'Low' | 'Guarded' | 'Medium' | 'High' | 'Critical';
  title: string;
  description: string;
  evidence: Record<string, any>;
  affected_tool: string;
  status: 'NEW' | 'INVESTIGATING' | 'RESOLVED' | 'DISMISSED';
  created_at: string;
  resolved_at: string | null;
}

export interface ApprovalRequest {
  id: string;
  invocation_id: string;
  tool_name: string;
  server_name: string;
  arguments_hash: string;
  redacted_arguments: Record<string, any>;
  risk_score: number;
  reasons: string[];
  requested_by: string | null;
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'EXPIRED' | 'CANCELLED';
  decided_by: string | null;
  decision_reason: string | null;
  expires_at: string;
  created_at: string;
  decided_at: string | null;
}

export interface Policy {
  id: string;
  name: string;
  description: string | null;
  category: string;
  rule_type: string;
  configuration: Record<string, any>;
  is_active: boolean;
  priority: number;
  change_summary?: string;
  created_at: string;
  updated_at: string;
}

export interface AuditLog {
  id: string;
  event_type: string;
  actor: string;
  target_resource: string;
  action: string;
  details: Record<string, any>;
  ip_address: string | null;
  previous_hash: string | null;
  entry_hash: string;
  created_at: string;
}

export interface DashboardOverview {
  kpis: {
    total_invocations: number;
    allowed_operations: number;
    blocked_operations: number;
    pending_approvals: number;
    critical_alerts: number;
    average_risk_score: number;
    server_status: {
      total: number;
      healthy: number;
      degraded: number;
      offline: number;
    };
  };
  risk_distribution: { name: string; count: number; color: string }[];
  recent_events: {
    id: string;
    tool_name: string;
    server_id: string;
    risk_score: number;
    risk_classification: string;
    decision: string;
    status: string;
    timestamp: string;
  }[];
  top_risky_tools: {
    tool_name: string;
    average_risk: number;
    invocations: number;
  }[];
}
