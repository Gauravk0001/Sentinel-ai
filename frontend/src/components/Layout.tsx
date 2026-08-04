import React, { useState } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Shield,
  LogOut,
  Menu,
  X,
  Search,
  Activity,
  ChevronDown,
  ShieldCheck,
} from 'lucide-react';
import { getStoredUser, getNavItemsForRole, getStoredRole, ROLE_META } from '../lib/roles';

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  const user = getStoredUser();
  const role = getStoredRole();
  const roleMeta = role ? ROLE_META[role] : undefined;
  const navItems = getNavItemsForRole(role);

  const handleLogout = () => {
    localStorage.removeItem('sentinelai_token');
    localStorage.removeItem('sentinelai_user');
    navigate('/login');
  };

  return (
    <div className="flex h-screen bg-cyber-dark overflow-hidden">
      {/* Sidebar */}
      <motion.aside
        initial={{ x: -280 }}
        animate={{ x: sidebarOpen ? 0 : -280 }}
        className="fixed lg:static lg:translate-x-0 z-50 w-72 h-full bg-cyber-darker border-r border-cyber-border/50 backdrop-blur-xl"
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="p-6 border-b border-cyber-border/30">
            <Link to="/dashboard" className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-cyan-500 flex items-center justify-center">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold gradient-text">SentinelAI</h1>
                <p className="text-xs text-gray-500">Insider Threat Detection</p>
              </div>
            </Link>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
            {navItems.map((item) => {
              const isActive = location.pathname.startsWith(item.path);
              return (
                <Link key={item.path} to={item.path} onClick={() => setSidebarOpen(false)}>
                  <motion.div
                    whileHover={{ x: 4 }}
                    className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                      isActive
                        ? 'bg-primary-600/20 text-primary-300 border border-primary-500/30'
                        : 'text-gray-400 hover:text-gray-200 hover:bg-cyber-card/50'
                    }`}
                  >
                    <item.icon className="w-5 h-5" />
                    <span className="font-medium">{item.label}</span>
                  </motion.div>
                </Link>
              );
            })}

            {/* Status Indicator */}
            <div className="mt-8 p-4 rounded-lg bg-cyber-card/50 border border-cyber-border/30">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                <span className="text-xs text-gray-400">System Status</span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-500">AI Engine</span>
                <span className="text-green-400">Active</span>
              </div>
              <div className="flex items-center justify-between text-xs mt-1">
                <span className="text-gray-500">Monitoring</span>
                <span className="text-cyan-400">1,000 users</span>
              </div>
            </div>
          </nav>

          {/* User */}
          <div className="p-4 border-t border-cyber-border/30">
            <div className="flex items-center gap-3">
              <div className={`w-10 h-10 rounded-full bg-gradient-to-br ${roleMeta?.color || 'from-primary-400 to-purple-500'} flex items-center justify-center text-white font-bold`}>
                {user.full_name?.charAt(0) || 'U'}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-200 truncate">{user.full_name || 'User'}</p>
                <p className="text-xs text-gray-500 capitalize">{roleMeta?.label || user.role || 'Analyst'}</p>
              </div>
              <button onClick={handleLogout} className="p-2 hover:bg-cyber-card rounded-lg transition-colors">
                <LogOut className="w-4 h-4 text-gray-400" />
              </button>
            </div>
          </div>
        </div>
      </motion.aside>

      {/* Overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 bg-black/50 z-40 lg:hidden" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="h-16 bg-cyber-darker/80 backdrop-blur-xl border-b border-cyber-border/30 flex items-center justify-between px-6">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden p-2 hover:bg-cyber-card rounded-lg"
            >
              {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>

            {/* Search */}
            <div className="hidden md:flex items-center gap-2 px-4 py-2 bg-cyber-card/50 border border-cyber-border/30 rounded-lg">
              <Search className="w-4 h-4 text-gray-500" />
              <input
                type="text"
                placeholder="Search employees, alerts, incidents..."
                className="bg-transparent border-none outline-none text-sm text-gray-300 placeholder-gray-600 w-80"
              />
            </div>
          </div>

          <div className="flex items-center gap-4">
            {/* Quick Status */}
            <div className="hidden md:flex items-center gap-4 text-xs">
              <div className="flex items-center gap-1.5">
                <div className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
                <span className="text-gray-400">28 Online</span>
              </div>
              <div className="flex items-center gap-1.5">
                <Activity className="w-3.5 h-3.5 text-red-400 animate-pulse" />
                <span className="text-red-400">3 Alerts</span>
              </div>
            </div>

            {/* Role Badge */}
            <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 bg-primary-500/10 border border-primary-500/20 rounded-full">
              <ShieldCheck className="w-3.5 h-3.5 text-primary-400" />
              <span className="text-xs text-primary-300 capitalize">{roleMeta?.label || role || 'User'}</span>
            </div>

            {/* User Menu */}
            <div className="relative">
              <button
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                className="flex items-center gap-2 p-2 hover:bg-cyber-card rounded-lg transition-colors"
              >
                <div className={`w-8 h-8 rounded-full bg-gradient-to-br ${roleMeta?.color || 'from-primary-400 to-purple-500'} flex items-center justify-center text-white text-sm font-bold`}>
                  {user.full_name?.charAt(0) || 'U'}
                </div>
                <ChevronDown className="w-4 h-4 text-gray-400" />
              </button>

              <AnimatePresence>
                {userMenuOpen && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="absolute right-0 mt-2 w-56 bg-cyber-card border border-cyber-border rounded-xl shadow-xl overflow-hidden"
                  >
                    <div className="p-4 border-b border-cyber-border/30">
                      <p className="font-medium text-gray-200">{user.full_name}</p>
                      <p className="text-xs text-gray-500">{user.email}</p>
                      <span className="inline-block mt-2 px-2 py-0.5 text-xs bg-primary-500/10 text-primary-300 rounded-full">
                        {roleMeta?.label || role}
                      </span>
                    </div>
                    <div className="p-2">
                      <button
                        onClick={handleLogout}
                        className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
                      >
                        <LogOut className="w-4 h-4" />
                        Sign Out
                      </button>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Outlet />
          </motion.div>
        </main>
      </div>
    </div>
  );
}
