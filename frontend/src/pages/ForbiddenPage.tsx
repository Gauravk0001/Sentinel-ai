import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ShieldX, ArrowLeft, Home } from 'lucide-react';
import { getStoredRole, ROLE_META, getRoleHome } from '../lib/roles';

export default function ForbiddenPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const role = getStoredRole();
  const roleMeta = role ? ROLE_META[role] : null;
  const home = getRoleHome(role);
  const from = (location.state as { from?: string })?.from;

  return (
    <div className="min-h-[70vh] flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="text-center max-w-md"
      >
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="flex justify-center mb-6"
        >
          <div className="w-24 h-24 rounded-2xl bg-red-500/10 border border-red-500/30 flex items-center justify-center">
            <ShieldX className="w-12 h-12 text-red-400" />
          </div>
        </motion.div>

        <h1 className="text-5xl font-bold text-gray-200 mb-2">403</h1>
        <h2 className="text-xl font-semibold text-gray-300 mb-3">Access Denied</h2>
        <p className="text-gray-500 mb-6">
          You don't have permission to access this page.
          {from && (
            <span className="block mt-1 text-sm text-gray-600 font-mono">{from}</span>
          )}
        </p>

        {roleMeta && (
          <div className={`p-4 rounded-xl bg-gradient-to-br ${roleMeta.color} bg-opacity-10 mb-6`}>
            <p className="text-sm font-medium text-gray-200">{roleMeta.label} access</p>
            <p className="text-xs text-gray-400 mt-1">{roleMeta.description}</p>
          </div>
        )}

        <div className="flex items-center justify-center gap-3">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 px-4 py-2.5 glass-button text-sm"
          >
            <ArrowLeft className="w-4 h-4" />
            Go Back
          </button>
          <button
            onClick={() => navigate(home)}
            className="flex items-center gap-2 px-4 py-2.5 glass-button-primary text-sm"
          >
            <Home className="w-4 h-4" />
            Go to {roleMeta?.label || 'Home'}
          </button>
        </div>
      </motion.div>
    </div>
  );
}
