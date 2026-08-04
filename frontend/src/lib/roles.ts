import type { LucideIcon } from 'lucide-react';
import {
  LayoutDashboard,
  Brain,
  Users,
  Bell,
  AlertTriangle,
  Settings,
  ShieldCheck,
  FileText,
  UserCog,
  BarChart3,
} from 'lucide-react';

export type Role = 'admin' | 'analyst' | 'compliance' | 'viewer';

export interface NavItem {
  path: string;
  label: string;
  icon: LucideIcon;
  roles: Role[];
}

export interface UserInfo {
  id?: number;
  email?: string;
  username?: string;
  full_name?: string;
  role?: Role;
  department?: string;
  is_active?: boolean;
}

// Role-based navigation configuration
export const NAV_ITEMS: NavItem[] = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard, roles: ['admin', 'analyst', 'compliance', 'viewer'] },
  { path: '/ai-insights', label: 'AI Insights', icon: Brain, roles: ['admin', 'analyst'] },
  { path: '/employees', label: 'Employees', icon: Users, roles: ['admin', 'analyst', 'compliance'] },
  { path: '/alerts', label: 'Alerts', icon: Bell, roles: ['admin', 'analyst', 'compliance'] },
  { path: '/incidents', label: 'Incidents', icon: AlertTriangle, roles: ['admin', 'analyst'] },
  { path: '/reports', label: 'Reports', icon: BarChart3, roles: ['admin', 'compliance'] },
  { path: '/compliance', label: 'Compliance', icon: ShieldCheck, roles: ['admin', 'compliance'] },
  { path: '/user-management', label: 'User Management', icon: UserCog, roles: ['admin'] },
  { path: '/settings', label: 'Settings', icon: Settings, roles: ['admin'] },
];

// Role-based home page (post-login landing)
export const ROLE_HOME: Record<Role, string> = {
  admin: '/dashboard',
  analyst: '/dashboard',
  compliance: '/compliance',
  viewer: '/dashboard',
};

// Role display metadata
export const ROLE_META: Record<Role, { label: string; description: string; color: string }> = {
  admin: {
    label: 'Administrator',
    description: 'Full platform control, user management and system configuration.',
    color: 'from-primary-400 to-purple-500',
  },
  analyst: {
    label: 'Security Analyst',
    description: 'AI insights, alerts, incidents and employee monitoring.',
    color: 'from-cyan-400 to-blue-500',
  },
  compliance: {
    label: 'Compliance Officer',
    description: 'Compliance reporting, policy oversight and audit management.',
    color: 'from-emerald-400 to-teal-500',
  },
  viewer: {
    label: 'Viewer',
    description: 'Read-only access to dashboards and monitoring statistics.',
    color: 'from-gray-400 to-slate-500',
  },
};

// Helper to get allowed nav items for a role
export function getNavItemsForRole(role: Role | undefined): NavItem[] {
  if (!role) return [];
  return NAV_ITEMS.filter((item) => item.roles.includes(role));
}

// Helper to check if a role can access a path
export function canAccessPath(role: Role | undefined, path: string): boolean {
  if (!role) return false;
  // Always allow admin to access everything
  if (role === 'admin') return true;
  return NAV_ITEMS.some((item) => item.path === path && item.roles.includes(role));
}

// Get the user object from localStorage (safe parse)
export function getStoredUser(): UserInfo {
  try {
    const raw = localStorage.getItem('sentinelai_user');
    if (!raw) return {};
    return JSON.parse(raw) as UserInfo;
  } catch {
    return {};
  }
}

export function getStoredRole(): Role | undefined {
  return getStoredUser().role;
}

export function getRoleHome(role: Role | undefined): string {
  if (!role) return '/dashboard';
  return ROLE_HOME[role] || '/dashboard';
}
