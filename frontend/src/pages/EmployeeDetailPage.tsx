import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  ArrowLeft, Shield, AlertTriangle, Clock, Globe, Download,
  Mail, Server, Activity, TrendingUp, MapPin, Monitor,
  Calendar, ChevronRight
} from 'lucide-react';
import { employeeAPI } from '../lib/api';
import {
  LineChart, Line, AreaChart, Area, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';

export default function EmployeeDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [employee, setEmployee] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await employeeAPI.getById(id!);
        setEmployee(res.data);
      } catch (err) {
        console.error('Failed to fetch employee:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-primary-500/30 border-t-primary-500 rounded-full animate-spin" />
      </div>
    );
  }

  if (!employee) {
    return <div className="text-gray-400 text-center py-12">Employee not found</div>;
  }

  const riskHistory = employee.risk_history || [];

  return (
    <div className="space-y-6 animate-in">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate('/employees')}
          className="p-2 hover:bg-cyber-card rounded-lg transition-colors"
        >
          <ArrowLeft className="w-5 h-5 text-gray-400" />
        </button>
        <div>
          <h1 className="text-2xl font-bold gradient-text">{employee.name}</h1>
          <p className="text-gray-500 text-sm">{employee.position} • {employee.department}</p>
        </div>
      </div>

      {/* Employee Info Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Info */}
        <div className="lg:col-span-2 glass-card p-6">
          <div className="flex items-start gap-6">
            <div className="w-20 h-20 rounded-full bg-gradient-to-br from-primary-400 to-purple-500 flex items-center justify-center text-3xl font-bold text-white">
              {employee.name?.charAt(0) || '?'}
            </div>
            <div className="flex-1">
              <h2 className="text-xl font-bold text-gray-200">{employee.name}</h2>
              <p className="text-gray-400">{employee.email}</p>
              <div className="flex flex-wrap gap-4 mt-4 text-sm">
                <div className="flex items-center gap-1.5">
                  <MapPin className="w-4 h-4 text-gray-500" />
                  <span className="text-gray-400">{employee.location}</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <Monitor className="w-4 h-4 text-gray-500" />
                  <span className="text-gray-400">{employee.os}</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <Calendar className="w-4 h-4 text-gray-500" />
                  <span className="text-gray-400">{employee.tenure_days} days tenure</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <Globe className="w-4 h-4 text-gray-500" />
                  <span className="text-gray-400">{employee.is_remote ? 'Remote' : 'On-site'}</span>
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-6 border-t border-cyber-border/30">
            <div>
              <p className="text-xs text-gray-500">Manager</p>
              <p className="text-sm text-gray-300 font-medium">{employee.manager}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Clearance</p>
              <p className="text-sm text-gray-300 font-medium capitalize">{employee.clearance_level}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">VPN</p>
              <p className={`text-sm font-medium ${employee.has_vpn ? 'text-green-400' : 'text-gray-400'}`}>
                {employee.has_vpn ? 'Enabled' : 'Disabled'}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Work Hours</p>
              <p className="text-sm text-gray-300 font-medium">{employee.working_hours_start}:00 - {employee.working_hours_end}:00</p>
            </div>
          </div>
        </div>

        {/* Risk Score */}
        <div className="glass-card p-6 flex flex-col items-center justify-center">
          <div className="relative w-32 h-32 mb-4">
            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
              <circle cx="18" cy="18" r="16" fill="none" stroke="#1e2048" strokeWidth="3" />
              <circle
                cx="18" cy="18" r="16"
                fill="none"
                stroke={employee.current_risk_score > 80 ? '#ff3366' : employee.current_risk_score > 60 ? '#ff9100' : employee.current_risk_score > 40 ? '#ffbb33' : '#00e676'}
                strokeWidth="3"
                strokeDasharray={`${(employee.current_risk_score || 0) * 1.005} 100`}
                strokeLinecap="round"
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <p className={`text-4xl font-bold ${
                  employee.current_risk_score > 80 ? 'text-red-400' :
                  employee.current_risk_score > 60 ? 'text-orange-400' :
                  employee.current_risk_score > 40 ? 'text-yellow-400' : 'text-green-400'
                }`}>
                  {employee.current_risk_score?.toFixed(0) || '0'}
                </p>
                <p className="text-xs text-gray-500">Risk Score</p>
              </div>
            </div>
          </div>
          <div className={`px-4 py-2 rounded-full text-sm font-medium ${
            employee.current_threat_level === 'Critical' ? 'bg-red-500/20 text-red-400' :
            employee.current_threat_level === 'High' ? 'bg-orange-500/20 text-orange-400' :
            employee.current_threat_level === 'Medium' ? 'bg-yellow-500/20 text-yellow-400' :
            'bg-green-500/20 text-green-400'
          }`}>
            {employee.current_threat_level || 'Safe'}
          </div>
          <div className="flex items-center gap-1 mt-2 text-xs text-gray-500">
            <Activity className="w-3 h-3" />
            Last evaluated: {employee.last_evaluated ? new Date(employee.last_evaluated).toLocaleString() : 'Now'}
          </div>
        </div>
      </div>

      {/* Risk History Chart */}
      <div className="glass-card p-6">
        <h3 className="text-sm font-medium text-gray-300 mb-6">Risk Score History</h3>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={riskHistory}>
            <defs>
              <linearGradient id="riskHistGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e2048" />
            <XAxis dataKey="date" stroke="#4a5568" fontSize={11} />
            <YAxis stroke="#4a5568" fontSize={11} />
            <Tooltip contentStyle={{ background: '#111328', border: '1px solid #1e2048', borderRadius: '8px', color: '#e2e8f0' }} />
            <Area type="monotone" dataKey="risk_score" stroke="#6366f1" fill="url(#riskHistGrad)" strokeWidth={2} />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Recent Activities */}
      <div className="glass-card p-6">
        <h3 className="text-sm font-medium text-gray-300 mb-6">Recent Activities</h3>
        <div className="space-y-3">
          {(employee.recent_activities || []).slice(0, 10).map((activity: any, index: number) => (
            <motion.div
              key={activity.id || index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              className="flex items-center gap-4 p-3 rounded-lg bg-cyber-card/30 hover:bg-cyber-card/50 transition-colors"
            >
              <div className={`p-2 rounded-lg ${
                activity.type?.includes('file') ? 'bg-cyan-500/20' :
                activity.type?.includes('usb') ? 'bg-red-500/20' :
                activity.type?.includes('cloud') ? 'bg-yellow-500/20' :
                'bg-primary-500/20'
              }`}>
                {activity.type?.includes('file') ? <Download className="w-4 h-4 text-cyan-400" /> :
                 activity.type?.includes('usb') ? <Server className="w-4 h-4 text-red-400" /> :
                 activity.type?.includes('cloud') ? <Globe className="w-4 h-4 text-yellow-400" /> :
                 activity.type?.includes('email') ? <Mail className="w-4 h-4 text-blue-400" /> :
                 <Activity className="w-4 h-4 text-primary-400" />}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-gray-200">{activity.description}</p>
                <p className="text-xs text-gray-500">{new Date(activity.timestamp).toLocaleString()}</p>
              </div>
              <div className={`px-2.5 py-1 rounded-full text-xs font-medium ${
                activity.risk_score > 70 ? 'bg-red-500/20 text-red-400' :
                activity.risk_score > 40 ? 'bg-yellow-500/20 text-yellow-400' :
                'bg-green-500/20 text-green-400'
              }`}>
                {activity.risk_score?.toFixed(0) || '0'}
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
