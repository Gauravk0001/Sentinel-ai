// Core types for SentinelAI

export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  role: 'admin' | 'analyst' | 'compliance' | 'viewer';
  department: string;
  is_active: boolean;
  created_at: string;
}

export interface Employee {
  employee_id: string;
  name: string;
  email: string;
  department: string;
  position: string;
  location: string;
  is_remote: boolean;
  risk_profile: 'normal' | 'malicious';
  tenure_days: number;
  working_hours_start: number;
  working_hours_end: number;
  manager: string;
  clearance_level: string;
  has_vpn: boolean;
  os: string;
  is_monitored: boolean;
  current_risk_score: number;
  current_threat_level: ThreatLevel;
  risk_history?: RiskHistoryEntry[];
  recent_activities?: Activity[];
}

export interface RiskHistoryEntry {
  date: string;
  risk_score: number;
  threat_level: ThreatLevel;
  events_count: number;
}

export interface Activity {
  id: string;
  type: string;
  description: string;
  risk_score: number;
  timestamp: string;
  is_suspicious: boolean;
  metadata?: Record<string, unknown>;
}

export interface Alert {
  id: string;
  employee_id: string;
  employee_name: string;
  department: string;
  type: string;
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  risk_score: number;
  status: string;
  is_read: boolean;
  is_acknowledged: boolean;
  created_at: string;
  acknowledged_by: string | null;
  resolved_at: string | null;
  metadata: Record<string, unknown>;
}

export interface Incident {
  incident_id: string;
  employee_id: string;
  employee_name: string;
  department: string;
  title: string;
  description: string;
  type: string;
  severity: string;
  status: 'open' | 'investigating' | 'contained' | 'resolved' | 'false_positive';
  risk_score: number;
  confidence: number;
  assigned_to: string | null;
  related_activities: number;
  evidence_count: number;
  created_at: string;
  detected_at: string;
  updated_at: string;
  resolved_at: string | null;
  evidence?: EvidenceItem[];
  timeline?: TimelineEvent[];
  ai_explanation?: AIExplanation;
  suggested_actions?: string[];
  remediation_steps?: string[];
}

export interface EvidenceItem {
  type: string;
  description: string;
  timestamp: string;
  severity: string;
}

export interface TimelineEvent {
  time: string;
  event: string;
  type: string;
}

export interface AIExplanation {
  risk_score: number;
  threat_level: string;
  confidence: number;
  reasons: string[];
}

export interface DashboardStats {
  active_users: number;
  online_now: number;
  high_risk_employees: number;
  critical_risk_employees: number;
  total_employees: number;
  total_alerts_today: number;
  open_incidents: number;
  average_risk_score: number;
  avg_response_time_minutes: number;
  threats_blocked_today: number;
  system_health: string;
  last_updated: string;
}

export interface RiskDistribution {
  safe: number;
  low: number;
  medium: number;
  high: number;
  critical: number;
}

export interface RiskTrend {
  date: string;
  avg_risk: number;
  max_risk: number;
  high_risk_count: number;
  incidents: number;
}

export type ThreatLevel = 'Safe' | 'Low' | 'Medium' | 'High' | 'Critical';

// === AI Engine Types ===

export interface AIPrediction {
  employee_id: string;
  risk_score: number;
  threat_level: ThreatLevel;
  confidence: number;
  reasons: string[];
  recommended_actions: string[];
  evidence: EvidenceItem[];
  correlation?: {
    correlated: boolean;
    scenario?: string;
    correlation_score: number;
    severity: string;
    signals: string[];
  };
  model_version: string;
  timestamp: string;
  ml_risk_score?: number;
  anomaly_score?: number;
  correlation_score?: number;
}

export interface AIEmployeeRisk {
  employee_id: string;
  risk_score: number;
  threat_level: ThreatLevel;
  confidence: number;
  model_version: string;
  timestamp: string;
}

export interface AIRiskHistoryEntry {
  date: string;
  risk_score: number;
  threat_level: ThreatLevel;
}

export interface AIAlert {
  id: string;
  employee_id: string;
  type: string;
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  risk_score: number;
  confidence: number;
  status: string;
  is_read: boolean;
  created_at: string;
  metadata: {
    source: string;
    model_version: string;
    reasons: string[];
    recommended_actions: string[];
  };
}

export interface AITimelineEvent {
  time: string;
  event: string;
  type: string;
  severity: string;
}

export interface ModelInfo {
  active_model: {
    model_version: string;
    training_date: string;
    metrics: Record<string, unknown>;
    features: string[];
  } | null;
  versions: Array<{
    model_version: string;
    training_date: string;
    status: string;
    metrics: Record<string, unknown>;
  }>;
}

export const THREAT_COLORS: Record<ThreatLevel, string> = {
  Safe: '#00e676',
  Low: '#42a5f5',
  Medium: '#ffbb33',
  High: '#ff9100',
  Critical: '#ff3366',
};

export const THREAT_BG_COLORS: Record<ThreatLevel, string> = {
  Safe: 'bg-green-500/10',
  Low: 'bg-blue-500/10',
  Medium: 'bg-yellow-500/10',
  High: 'bg-orange-500/10',
  Critical: 'bg-red-500/10',
};

export const THREAT_TEXT_COLORS: Record<ThreatLevel, string> = {
  Safe: 'text-green-400',
  Low: 'text-blue-400',
  Medium: 'text-yellow-400',
  High: 'text-orange-400',
  Critical: 'text-red-400',
};

