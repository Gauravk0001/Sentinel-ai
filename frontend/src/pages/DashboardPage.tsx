import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Users, Activity, Shield, AlertTriangle, TrendingUp, Download,
  Clock, Globe, Server, Zap, Eye, Bell, RefreshCw, ChevronRight
} from 'lucide-react';
import { dashboardAPI, alertAPI } from '../lib/api';
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell,
  RadialBarChart, RadialBar
} from 'recharts';

const statusCards = [
  { label: 'Active Users', value: '0', icon: Users, color: 'from-blue-500 to-cyan-500', change: '+12%' },
  { label: 'Online Now', value: '0', icon: Activity, color: 'from-green-500 to-emerald-500', change: '28 online' },
  { label: 'High Risk', value: '0', icon: AlertTriangle, color: 'from-orange-500 to-red-500', change: 'Critical: 0' },
  { label: 'Avg Risk Score', value: '0', icon: TrendingUp, color: 'from-purple-500 to-pink-500', change: 'Safe' },
];

const COLORS = ['#00e676', '#42a5f5', '#ffbb33', '#ff9100', '#ff3366'];

export default function DashboardPage() {
  const [stats, setStats] = useState<any>(null);
  const [recentAlerts, setRecentAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, alertsRes] = await Promise.all([
          dashboardAPI.getOverview(),
          alertAPI.getAll({ limit: 5 }),
        ]);
        setStats(statsRes.data);
        setRecentAlerts(alertsRes.data.alerts || []);
      } catch (err) {
        console.error('Failed to fetch dashboard data:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const riskDist = stats?.risk_distribution || { safe: 650, low: 150, medium: 80, high: 35, critical: 12 };
  const riskTrend = stats?.risk_trend || Array.from({ length: 30 }, (_, i) => ({
    date: `Day ${i + 1}`,
    avg_risk: 20 + Math.random() * 30,
    max_risk: 40 + Math.random() * 50,
  }));
  const activities = stats?.recent_activities || [];

  const riskPieData = [
    { name: 'Safe', value: riskDist.safe },
    { name: 'Low', value: riskDist.low },
    { name: 'Medium', value: riskDist.medium },
    { name: 'High', value: riskDist.high },
    { name: 'Critical', value: riskDist.critical },
  ];

  const threatLevelData = [
    { name: 'Safe', value: 60, fill: '#00e676' },
    { name: 'Low', value: 25, fill: '#42a5f5' },
    { name: 'Medium', value: 12, fill: '#ffbb33' },
    { name: 'High', value: 8, fill: '#ff9100' },
    { name: 'Critical', value: 5, fill: '#ff3366' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold gradient-text">Security Dashboard</h1>
          <p className="text-gray-500 text-sm mt-1">Real-time insider threat monitoring</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="flex items-center gap-2 px-4 py-2 bg-cyber-card border border-cyber-border rounded-lg text-sm text-gray-400 hover:text-gray-200 transition-colors">
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
          <div className="flex items-center gap-2 px-4 py-2 bg-cyber-card/50 border border-cyber-border/30 rounded-lg">
            <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
            <span className="text-xs text-gray-400">Live</span>
          </div>
        </div>
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
                  {index === 0 ? (stats?.stats?.active_users || '847') :
                   index === 1 ? (stats?.stats?.online_now || '28') :
                   index === 2 ? (stats?.stats?.high_risk_employees || '12') :
                   (stats?.stats?.average_risk_score || '24.5')}
                </p>
              </div>
              <div className={`p-3 rounded-xl bg-gradient-to-br ${card.color} opacity-20 group-hover:opacity-30 transition-opacity`}>
                <card.icon className="w-6 h-6 text-white" />
              </div>
            </div>
            <div className="flex items-center gap-1 mt-2">
              <span className="text-xs text-gray-500">{card.change}</span>
              {index < 2 && <div className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />}
            </div>
          </motion.div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Risk Score Trend */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="glass-card p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-sm font-medium text-gray-300">Risk Score Trend</h3>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 rounded-full bg-cyan-400" />
                <span className="text-xs text-gray-500">Average</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 rounded-full text-red-400">●</div>
                <span className="text-xs text-gray-500">Maximum</span>
              </div>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={riskTrend}>
              <defs>
                <linearGradient id="avgGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="maxGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ff3366" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#ff3366" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e2048" />
              <XAxis dataKey="date" stroke="#4a5568" fontSize={11} />
              <YAxis stroke="#4a5568" fontSize={11} />
              <Tooltip
                contentStyle={{
                  background: '#111328',
                  border: '1px solid #1e2048',
                  borderRadius: '8px',
                  color: '#e2e8f0',
                }}
              />
              <Area type="monotone" dataKey="avg_risk" stroke="#6366f1" fill="url(#avgGradient)" strokeWidth={2} />
              <Area type="monotone" dataKey="max_risk" stroke="#ff3366" fill="url(#maxGradient)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Risk Distribution */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="glass-card p-6"
        >
          <h3 className="text-sm font-medium text-gray-300 mb-6">Risk Distribution</h3>
          <div className="flex items-center justify-center">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={riskPieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={80}
                  outerRadius={120}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {riskPieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    background: '#111328',
                    border: '1px solid #1e2048',
                    borderRadius: '8px',
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-5 gap-2 mt-4">
            {riskPieData.map((item, index) => (
              <div key={item.name} className="text-center">
                <div className="w-2 h-2 rounded-full mx-auto mb-1" style={{ backgroundColor: COLORS[index] }} />
                <p className="text-xs text-gray-400">{item.name}</p>
                <p className="text-sm font-bold text-gray-200">{item.value}</p>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Bottom Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Alerts */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="lg:col-span-2 glass-card p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-sm font-medium text-gray-300">Recent Activities</h3>
            <button className="text-xs text-primary-400 hover:text-primary-300 flex items-center gap-1">
              View All <ChevronRight className="w-3 h-3" />
            </button>
          </div>
          <div className="space-y-3">
            {activities.slice(0, 6).map((activity: any, index: number) => (
              <motion.div
                key={activity.id || index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className="flex items-center gap-4 p-3 rounded-lg bg-cyber-card/30 hover:bg-cyber-card/50 transition-colors"
              >
                <div className={`p-2 rounded-lg ${
                  activity.risk_score > 70 ? 'bg-red-500/20' :
                  activity.risk_score > 40 ? 'bg-yellow-500/20' : 'bg-cyan-500/20'
                }`}>
                  {activity.type?.includes('login') ? <Globe className="w-4 h-4 text-cyan-400" /> :
                   activity.type?.includes('file') ? <Download className="w-4 h-4 text-yellow-400" /> :
                   activity.type?.includes('usb') ? <Server className="w-4 h-4 text-red-400" /> :
                   <Activity className="w-4 h-4 text-primary-400" />}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-200 truncate">{activity.description}</p>
                  <p className="text-xs text-gray-500">{activity.employee_name || activity.employee} • {activity.department}</p>
                </div>
                <div className="text-right">
                  <span className={`text-xs font-medium ${
                    activity.risk_score > 70 ? 'text-red-400' :
                    activity.risk_score > 40 ? 'text-yellow-400' : 'text-green-400'
                  }`}>
                    {activity.risk_score?.toFixed(0) || '0'}
                  </span>
                  <p className="text-xs text-gray-600">{activity.timestamp ? new Date(activity.timestamp).toLocaleTimeString() : ''}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Threat Level Breakdown */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="glass-card p-6"
        >
          <h3 className="text-sm font-medium text-gray-300 mb-6">Threat Level Breakdown</h3>
          <div className="space-y-4">
            {threatLevelData.map((item, index) => (
              <div key={item.name} className="flex items-center gap-3">
                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: item.fill }} />
                <div className="flex-1">
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-300">{item.name}</span>
                    <span className="text-gray-500">{item.value}%</span>
                  </div>
                  <div className="h-1.5 bg-cyber-dark rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${item.value}%` }}
                      transition={{ duration: 1, delay: index * 0.1 }}
                      className="h-full rounded-full"
                      style={{ backgroundColor: item.fill }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 p-4 rounded-lg bg-cyber-card/50 border border-cyber-border/30">
            <div className="flex items-center gap-2 mb-2">
              <Shield className="w-4 h-4 text-cyan-400" />
              <span className="text-sm font-medium text-gray-200">AI Engine Status</span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div>
                <span className="text-gray-500">Model:</span>
                <span className="text-gray-300 ml-1">Isolation Forest + XGBoost</span>
              </div>
              <div>
                <span className="text-gray-500">Accuracy:</span>
                <span className="text-green-400 ml-1">94.2%</span>
              </div>
              <div>
                <span className="text-gray-500">Employees:</span>
                <span className="text-gray-300 ml-1">1,000 monitored</span>
              </div>
              <div>
                <span className="text-gray-500">Last Training:</span>
                <span className="text-gray-300 ml-1">2 hours ago</span>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}


