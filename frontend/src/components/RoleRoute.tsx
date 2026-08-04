import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { getStoredRole, getRoleHome, canAccessPath } from '../lib/roles';

interface RoleRouteProps {
  children: React.ReactNode;
  roles?: string[];
}

/**
 * Role-based route guard.
 * - If no roles specified, any authenticated user can access.
 * - If roles specified, the current user's role must be in the list.
 * - If the user lacks permission, redirects to a 403 forbidden page.
 */
export default function RoleRoute({ children, roles }: RoleRouteProps) {
  const location = useLocation();
  const role = getStoredRole();

  // If roles are specified and the user's role isn't allowed, -> 403
  if (roles && role && !roles.includes(role)) {
    return <Navigate to="/403" replace state={{ from: location.pathname }} />;
  }

  // If the path isn't in the role's nav access, -> 403 (except admin)
  if (role && !canAccessPath(role, location.pathname)) {
    return <Navigate to="/403" replace state={{ from: location.pathname }} />;
  }

  return <>{children}</>;
}

// Export a helper to redirect to the role's home page
export function useRoleHome() {
  const role = getStoredRole();
  return getRoleHome(role);
}
