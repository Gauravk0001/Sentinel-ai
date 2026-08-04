import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  ShieldCheck, FileText, AlertTriangle, CheckCircle2, Clock,
  Download, Eye, Search, Filter, Lock, ScrollText
} from 'lucide-react';
import { dashboardAPI, alertAPI, incidentAPI, reportAPI } from '../lib/api';

const statusCards = [
  { label: 'Compliance Score', value: '0%', icon: ShieldCheck, color: 'from-emerald-500 to-teal-500' },
  { label: 'Open Incidents', value: '0', icon: AlertTriangle, color: 'from-orange-500 to-red-500' },
  { label: 'Audit Trails', value: '0', icon: ScrollText, color: 'from-blue-500 to-cyan-500' },
  { label: 'Policies', value: '0', icon: FileText, color: 'from-purple-500 to-pink-500' },
];

export default function CompliancePage() {
  const [stats, setStats] = useState<any>(null);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [alertsRes, summaryRes] = await Promise.all([
          alertAPI.getAll({ limit: 8 }),
          reportAPI.getDailySummary(),
        ]);
        setAlerts(alertsRes.data.alerts || []);
        setSummary(summaryRes.data);
      } catch (err) {
        console.error('Failed to load compliance data:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const complianceScore = summary?.summary?.average_risk_score
    ? Math.max(0, Math.min(100, Math.round(100 - summary.summary.average_risk_score * 1.5))).toString() + '%'
    : '84%';

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold gradient-text">Compliance Dashboard</h1>
          <p className="text-gray-500 text-sm mt-1">Policy oversight, audit trails and regulatory compliance</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 glass-button-primary text-sm">
          <Download className="w-4 h-4" />
          Export Compliance Report
        </button>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statusCards.map((card, index) => (
          <motion.div
            key={card.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="glass-card p-6 group hover:border-primary-500/30 transition-all duration-300"
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-gray-400">{card.label}</p>
                <p className="text-3xl font-bold gradient-text mt-1">
                  {index === 0 ? complianceScore :
                   index === 1 ? (summary?.summary?.open_incidents || '0') :
                   index === 2 ? (summary?.summary?.suspicious_activities || '0') :
                   (summary?.summary?.threats_blocked || '0')}
                </p>
              </div>
              <div className={`p-3 rounded-xl bg-gradient-to-br ${card.color} opacity-20 group-hover:opacity-30 transition-opacity`}>
                <card.icon className="w-6 h-6 text-white" />
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Compliance Alerts */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="lg:col-span-2 glass-card p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-sm font-medium text-gray-300">Compliance-Relevant Alerts</h3>
            <div className="flex items-center gap-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                <input type="text" placeholder="Search alerts..." className="glass-input pl-10 w-56 text-sm" />
              </div>
              <button className="p-2 glass-input">
                <Filter className="w-4 h-4" />
              </button>
            </div>
          </div>
          <div className="space-y-3">
            {alerts.slice(0, 6).map((alert: any, index: number) => (
              <motion.div
                key={alert.id || index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className="flex items-center gap-4 p-3 rounded-lg bg-cyber-card/30 hover:bg-cyber-card/50 transition-colors"
              >
                <div className={`p-2 rounded-lg ${
                  alert.severity === 'critical' ? 'bg-red-500/20' :
                  alert.severity === 'high' ? 'bg-orange-500/20' :
                  alert.severity === 'medium' ? 'bg-yellow-500/20' : 'bg-cyan-500/20'
                }`}>
                  {alert.severity === 'critical' ? <AlertTriangle className="w-4 h-4 text-red-400" /> :
                   alert.severity === 'high' ? <AlertTriangle className="w-4 h-4 text-orange-400" /> :
                   <CheckCircle2 className="w-4 h-4 text-cyan-400" />}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-200 truncate">{alert.title || alert.description}</p>
                  <p className="text-xs text-gray-500">{alert.employee_name || alert.employee_id} • {alert.department}</p>
                </div>
                <div className="text-right">
                  <span className={`text-xs font-medium ${
                    alert.severity === 'critical' ? 'text-red-400' :
                    alert.severity === 'high' ? 'text-orange-400' :
                    alert.severity === 'medium' ? 'text-yellow-400' : 'text-green-400'
                  }`}>
                    {alert.severity?.toUpperCase()}
                  </span>
                  <p className="text-xs text-gray-600">{alert.created_at ? new Date(alert.created_at).toLocaleDateString() : ''}</p>
                </div>
              </motion.div>
            ))}
            {alerts.length === 0 && !loading && (
              <div className="text-center py-8 text-gray-500 text-sm">No compliance alerts found</div>
            )}
          </div>
        </motion.div>

        {/* Compliance Overview */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="glass-card p-6"
        >
          <h3 className="text-sm font-medium text-gray-300 mb-6">Compliance Overview</h3>
          <div className="space-y-4">
            {[
              { label: 'Policy Compliance', value: '94%', color: '#00e676' },
              { label: 'Data Protection', value: '97%', color: '#42a5f5' },
              { label: 'Access Control', value: '89%', color: '#ffbb33' },
              { label: 'Audit Readiness', value: '92%', color: '#ff9100' },
            ].map((item, index) => (
              <div key={item.label} className="flex items-center gap-3">
                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: item.color }} />
                <div className="flex-1">
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-300">{item.label}</span>
                    <span className="text-gray-500">{item.value}</span>
                  </div>
                  <div className="h-1.5 bg-cyber-dark rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: item.value }}
                      transition={{ duration: 1, delay: index * 0.1 }}
                      className="h-full rounded-full"
                      style={{ backgroundColor: item.color }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 p-4 rounded-lg bg-cyber-card/50 border border-cyber-border/30">
            <div className="flex items-center gap-2 mb-2">
              <Lock className="w-4 h-4 text-emerald-400" />
              <span className="text-sm font-medium text-gray-200">Regulatory Standards</span>
            </div>
            <div className="flex flex-wrap gap-2 mt-3">
              {['GDPR', 'SOX', 'ISO 27001', 'HIPAA', 'PCI-DSS'].map((std) => (
                <span key={std} className="px-2.5 py-1 text-xs bg-emerald-500/10 text-emerald-400 rounded-full border border-emerald-500/20">
                  {std}
                </span>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
