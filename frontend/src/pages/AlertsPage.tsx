import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Bell, AlertTriangle, Filter, Search, CheckCheck,
  Eye, Clock, Shield, MoreHorizontal, ChevronDown
} from 'lucide-react';
import { alertAPI } from '../lib/api';

const severityColors: Record<string, string> = {
  critical: 'bg-red-500/20 text-red-400 border-red-500/30',
  high: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  medium: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  low: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
};

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await alertAPI.getAll({ limit: 50 });
        setAlerts(res.data.alerts || []);
      } catch (err) {
        console.error('Failed to fetch alerts:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const filteredAlerts = filter
    ? alerts.filter(a => a.severity === filter || a.status === filter)
    : alerts;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold gradient-text">Security Alerts</h1>
          <p className="text-gray-500 text-sm mt-1">Monitor and respond to security alerts</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="flex items-center gap-2 px-4 py-2 glass-button text-sm">
            <CheckCheck className="w-4 h-4" />
            Mark All Read
          </button>
        </div>
      </div>

      <div className="glass-card p-4">
        <div className="flex flex-wrap items-center gap-4">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <input type="text" placeholder="Search alerts..." className="glass-input w-full pl-10" />
          </div>
          <select value={filter} onChange={(e) => setFilter(e.target.value)} className="glass-input w-40">
            <option value="">All Severity</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
          <button className="p-3 glass-input"><Filter className="w-4 h-4" /></button>
        </div>
      </div>

      <div className="space-y-3">
        {filteredAlerts.map((alert, index) => (
          <motion.div
            key={alert.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.03 }}
            className="glass-card p-4 hover:border-primary-500/30 transition-all duration-300 cursor-pointer"
          >
            <div className="flex items-start gap-4">
              <div className={`p-2 rounded-lg ${
                alert.severity === 'critical' ? 'bg-red-500/20' :
                alert.severity === 'high' ? 'bg-orange-500/20' :
                'bg-yellow-500/20'
              }`}>
                <AlertTriangle className={`w-5 h-5 ${
                  alert.severity === 'critical' ? 'text-red-400' :
                  alert.severity === 'high' ? 'text-orange-400' :
                  'text-yellow-400'
                }`} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-sm font-medium text-gray-200">{alert.title}</h3>
                    <p className="text-xs text-gray-500 mt-0.5">{alert.description}</p>
                  </div>
                  <span className={`ml-4 px-2.5 py-1 rounded-full text-xs font-medium border ${
                    severityColors[alert.severity] || 'bg-gray-500/20 text-gray-400'
                  }`}>
                    {alert.severity}
                  </span>
                </div>
                <div className="flex items-center gap-4 mt-3 text-xs text-gray-500">
                  <span>{alert.employee_name}</span>
                  <span>•</span>
                  <span>{alert.department}</span>
                  <span>•</span>
                  <div className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {new Date(alert.created_at).toLocaleString()}
                  </div>
                  <span className={`px-1.5 py-0.5 rounded text-xs font-medium ${
                    alert.risk_score > 80 ? 'text-red-400' :
                    alert.risk_score > 60 ? 'text-orange-400' :
                    'text-yellow-400'
                  }`}>
                    Score: {alert.risk_score?.toFixed(0)}
                  </span>
                </div>
              </div>
              <button className="p-1.5 hover:bg-cyber-card rounded transition-colors">
                <MoreHorizontal className="w-4 h-4 text-gray-500" />
              </button>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
