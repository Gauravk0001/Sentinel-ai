import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FileText, Download, Clock, TrendingUp, BarChart3, Plus, Calendar } from 'lucide-react';
import { reportAPI, dashboardAPI } from '../lib/api';

const reportTemplates = [
  { id: 'daily', title: 'Daily Security Summary', desc: 'Daily overview of alerts, threats and incidents', icon: FileText, color: 'from-blue-500 to-cyan-500' },
  { id: 'weekly', title: 'Weekly Risk Report', desc: 'Weekly risk trends and department breakdowns', icon: TrendingUp, color: 'from-purple-500 to-pink-500' },
  { id: 'monthly', title: 'Monthly Compliance Report', desc: 'Monthly compliance posture and policy adherence', icon: BarChart3, color: 'from-emerald-500 to-teal-500' },
  { id: 'incident', title: 'Incident Analysis Report', desc: 'Detailed incident timelines and findings', icon: FileText, color: 'from-orange-500 to-red-500' },
];

export default function ReportsPage() {
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await reportAPI.getDailySummary();
        setSummary(res.data);
      } catch (err) {
        console.error('Failed to load reports:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleGenerate = (id: string) => {
    setGenerating(id);
    setTimeout(() => setGenerating(''), 2000);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold gradient-text">Reports</h1>
          <p className="text-gray-500 text-sm mt-1">Generate and export security, risk and compliance reports</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 glass-button-primary text-sm">
          <Calendar className="w-4 h-4" />
          Schedule Report
        </button>
      </div>

      {/* Report Templates */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {reportTemplates.map((template, index) => (
          <motion.div
            key={template.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="glass-card p-6 group hover:border-primary-500/30 transition-all duration-300"
          >
            <div className={`inline-flex p-3 rounded-xl bg-gradient-to-br ${template.color} opacity-20 group-hover:opacity-30 transition-opacity mb-4`}>
              <template.icon className="w-6 h-6 text-white" />
            </div>
            <h3 className="text-sm font-medium text-gray-200 mb-1">{template.title}</h3>
            <p className="text-xs text-gray-500 mb-4">{template.desc}</p>
            <button
              onClick={() => handleGenerate(template.id)}
              disabled={generating === template.id}
              className="w-full flex items-center justify-center gap-2 px-3 py-2 glass-button text-xs disabled:opacity-50"
            >
              {generating === template.id ? (
                <>
                  <Clock className="w-4 h-4 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Plus className="w-4 h-4" />
                  Generate Report
                </>
              )}
            </button>
          </motion.div>
        ))}
      </div>

      {/* Latest Summary */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="glass-card p-6"
      >
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-sm font-medium text-gray-300">Latest Daily Summary</h3>
            <p className="text-xs text-gray-500 mt-1">
              Generated at {summary?.generated_at ? new Date(summary.generated_at).toLocaleString() : '—'}
            </p>
          </div>
          <button className="flex items-center gap-2 px-3 py-2 glass-button-primary text-xs">
            <Download className="w-4 h-4" />
            Download PDF
          </button>
        </div>

        {summary?.summary ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: 'Total Alerts', value: summary.summary.total_alerts },
              { label: 'Critical Alerts', value: summary.summary.critical_alerts },
              { label: 'Open Incidents', value: summary.summary.open_incidents },
              { label: 'High Risk Employees', value: summary.summary.high_risk_employees },
              { label: 'Avg Risk Score', value: summary.summary.average_risk_score },
              { label: 'Threats Blocked', value: summary.summary.threats_blocked },
              { label: 'Employees Monitored', value: summary.summary.employees_monitored },
              { label: 'Suspicious Activities', value: summary.summary.suspicious_activities },
            ].map((item, i) => (
              <div key={i} className="p-4 bg-cyber-card/30 rounded-lg">
                <p className="text-xs text-gray-500">{item.label}</p>
                <p className="text-2xl font-bold gradient-text mt-1">{item.value}</p>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500 text-sm">
            {loading ? 'Loading report data...' : 'No report data available. Generate a report to begin.'}
          </div>
        )}
      </motion.div>

      {/* Department Risk */}
      {summary?.department_risk && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="glass-card p-6"
        >
          <h3 className="text-sm font-medium text-gray-300 mb-6">Department Risk Summary</h3>
          <div className="space-y-4">
            {summary.department_risk.map((dept: any, index: number) => (
              <div key={dept.department} className="flex items-center gap-4">
                <div className="w-32 text-sm text-gray-300 flex-shrink-0">{dept.department}</div>
                <div className="flex-1">
                  <div className="h-2 bg-cyber-dark rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${Math.min(dept.avg_risk, 100)}%` }}
                      transition={{ duration: 1, delay: index * 0.1 }}
                      className="h-full rounded-full"
                      style={{
                        backgroundColor: dept.avg_risk > 60 ? '#ff3366' : dept.avg_risk > 40 ? '#ff9100' : dept.avg_risk > 20 ? '#42a5f5' : '#00e676',
                      }}
                    />
                  </div>
                </div>
                <div className="w-24 text-sm text-gray-400 text-right">{dept.avg_risk}</div>
                <div className="w-24 text-xs text-gray-500 text-right">{dept.employees_at_risk} at risk</div>
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
}
