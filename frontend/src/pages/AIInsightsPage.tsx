import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Brain, Shield, AlertTriangle, Activity, TrendingUp, Zap,
  CheckCircle2, XCircle, Cpu, RefreshCw, Radio
} from 'lucide-react';
import { aiAPI } from '../lib/api';
import { useWebSocket } from '../hooks/useWebSocket';
import { THREAT_COLORS, THREAT_TEXT_COLORS } from '../types';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, BarChart, Bar
} from 'recharts';

const COLORS = ['#00e676', '#42a5f5', '#ffbb33', '#ff9100', '#ff3366'];

export default function AIInsightsPage() {
  const [liveAlerts, setLiveAlerts] = useState<any[]>([]);
  const [modelInfo, setModelInfo] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [searchId, setSearchId] = useState('');
  const [prediction, setPrediction] = useState<any>(null);
  const [dashStats, setDashStats] = useState<any>(null);

  // WebSocket live updates
  const { connected, lastMessage } = useWebSocket((msg) => {
    if (msg.type === 'ai_alert') {
      setLiveAlerts((prev) => [msg.data, ...prev].slice(0, 20));
    }
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [alertsRes, modelRes] = await Promise.all([
          aiAPI.getLiveAlerts(20),
          aiAPI.getModelInfo(),
        ]);
        setLiveAlerts(alertsRes.data.alerts || []);
        setModelInfo(modelRes.data);
      } catch (err) {
        console.error('Failed to fetch AI data:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handlePredict = async () => {
    if (!searchId) return;
    try {
      const res = await aiAPI.predict(searchId);
      setPrediction(res.data);
    } catch (err) {
      console.error('Prediction failed:', err);
    }
  };

  const riskDist = {
    safe: 0, low: 0, medium: 0, high: 0, critical: 0
  };
  liveAlerts.forEach((a) => {
    if (a.risk_score <= 20) riskDist.safe++;
    else if (a.risk_score <= 40) riskDist.low++;
    else if (a.risk_score <= 60) riskDist.medium++;
    else if (a.risk_score <= 80) riskDist.high++;
    else riskDist.critical++;
  });

  const pieData = [
    { name: 'Safe', value: riskDist.safe || 1 },
    { name: 'Low', value: riskDist.low || 1 },
    { name: 'Medium', value: riskDist.medium || 1 },
    { name: 'High', value: riskDist.high || 1 },
    { name: 'Critical', value: riskDist.critical || 1 },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold gradient-text">AI Threat Intelligence</h1>
          <p className="text-gray-500 text-sm mt-1">Real-time AI-powered insider threat detection</p>
        </div>
        <div className="flex items-center gap-3">
          <div className={`flex items-center gap-2 px-4 py-2 bg-cyber-card/50 border border-cyber-border/30 rounded-lg`}>
            <div className={`w-2 h-2 rounded-full animate-pulse ${connected ? 'bg-green-400' : 'bg-red-400'}`} />
            <span className="text-xs text-gray-400">{connected ? 'Live' : 'Reconnecting'}</span>
          </div>
          <button
            onClick={() => window.location.reload()}
            className="flex items-center gap-2 px-4 py-2 bg-cyber-card border border-cyber-border rounded-lg text-sm text-gray-400 hover:text-gray-200 transition-colors"
          >
            <RefreshCw className="w-4 h-4" /> Refresh
          </button>
        </div>
      </div>

      {/* Model Status */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card p-6"
      >
        <div className="flex items-center gap-3 mb-4">
          <div className="p-3 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 opacity-20">
            <Brain className="w-6 h-6 text-white" />
          </div>
          <div className="flex-1">
            <h3 className="text-sm font-medium text-gray-300">AI Model Status</h3>
            <p className="text-xs text-gray-500">
              {modelInfo?.active_model?.model_version || 'Loading model...'}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Cpu className="w-4 h-4 text-cyan-400" />
            <span className="text-xs text-gray-400">Isolation Forest + XGBoost + SHAP</span>
          </div>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
          <div>
            <span className="text-gray-500">Trained:</span>
            <span className="text-gray-300 ml-1">
              {modelInfo?.active_model?.training_date ? new Date(modelInfo.active_model.training_date).toLocaleDateString() : 'N/A'}
            </span>
          </div>
          <div>
            <span className="text-gray-500">Versions:</span>
            <span className="text-gray-300 ml-1">{modelInfo?.versions?.length || 0}</span>
          </div>
          <div>
            <span className="text-gray-500">Features:</span>
            <span className="text-gray-300 ml-1">{modelInfo?.active_model?.features?.length || 0}</span>
          </div>
          <div>
            <span className="text-gray-500">Status:</span>
            <span className="text-green-400 ml-1">Active</span>
          </div>
        </div>
      </motion.div>

      {/* Prediction Search */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="glass-card p-6"
      >
        <h3 className="text-sm font-medium text-gray-300 mb-4 flex items-center gap-2">
          <Zap className="w-4 h-4 text-primary-400" /> AI Prediction Engine
        </h3>
        <div className="flex gap-3">
          <input
            value={searchId}
            onChange={(e) => setSearchId(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handlePredict()}
            placeholder="Enter employee ID (e.g. EMP00001)"
            className="flex-1 px-4 py-2 bg-cyber-dark border border-cyber-border rounded-lg text-sm text-gray-200 focus:outline-none focus:border-primary-500/50"
          />
          <button
            onClick={handlePredict}
            className="px-6 py-2 bg-gradient-to-r from-primary-500 to-blue-600 rounded-lg text-sm font-medium text-white hover:opacity-90 transition-opacity"
          >
            Predict Risk
          </button>
        </div>

        {prediction && (
          <div className="mt-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Risk Score */}
            <div className="p-6 rounded-xl bg-cyber-card/50 border border-cyber-border/30">
              <div className="flex items-center justify-between mb-4">
                <span className="text-sm text-gray-400">Risk Score</span>
                <span className={`text-xs font-medium ${THREAT_TEXT_COLORS[prediction.threat_level as keyof typeof THREAT_TEXT_COLORS] || 'text-gray-400'}`}>
                  {prediction.threat_level}
                </span>
              </div>
              <div className="text-5xl font-bold gradient-text mb-4">
                {prediction.risk_score?.toFixed(0)}
                <span className="text-lg text-gray-500">/100</span>
              </div>
              <div className="h-2 bg-cyber-dark rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full"
                  style={{
                    width: `${prediction.risk_score || 0}%`,
                    backgroundColor: THREAT_COLORS[prediction.threat_level as keyof typeof THREAT_COLORS] || '#42a5f5',
                  }}
                />
              </div>
              <div className="mt-4 flex items-center gap-2 text-xs text-gray-500">
                <Shield className="w-4 h-4 text-cyan-400" />
                Confidence: {(prediction.confidence * 100).toFixed(0)}%
              </div>
            </div>

            {/* Reasons */}
            <div className="p-6 rounded-xl bg-cyber-card/50 border border-cyber-border/30">
              <h4 className="text-sm font-medium text-gray-300 mb-3">Risk Indicators</h4>
              <ul className="space-y-2">
                {(prediction.reasons || []).slice(0, 5).map((reason: string, i: number) => (
                  <li key={i} className="flex items-start gap-2 text-xs text-gray-400">
                    <Activity className="w-3 h-3 text-red-400 mt-0.5 shrink-0" />
                    <span>{reason}</span>
                  </li>
                ))}
                {(!prediction.reasons || prediction.reasons.length === 0) && (
                  <li className="text-xs text-gray-500">No significant risk indicators detected</li>
                )}
              </ul>
            </div>

            {/* Recommended Actions */}
            <div className="p-6 rounded-xl bg-cyber-card/50 border border-cyber-border/30">
              <h4 className="text-sm font-medium text-gray-300 mb-3">Recommended Actions</h4>
              <ul className="space-y-2">
                {(prediction.recommended_actions || []).slice(0, 5).map((action: string, i: number) => (
                  <li key={i} className="flex items-start gap-2 text-xs text-gray-400">
                    {prediction.risk_score > 80 ? (
                      <AlertTriangle className="w-3 h-3 text-red-400 mt-0.5 shrink-0" />
                    ) : (
                      <CheckCircle2 className="w-3 h-3 text-green-400 mt-0.5 shrink-0" />
                    )}
                    <span>{action}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </motion.div>

      {/* Live Alerts + Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Live Alerts */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="lg:col-span-2 glass-card p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-sm font-medium text-gray-300 flex items-center gap-2">
              <Radio className="w-4 h-4 text-red-400" /> Live AI Alerts
            </h3>
            <span className="text-xs text-gray-500">{liveAlerts.length} alerts</span>
          </div>
          <div className="space-y-3">
            {liveAlerts.slice(0, 8).map((alert, index) => (
              <motion.div
                key={alert.id || index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className="flex items-center gap-4 p-3 rounded-lg bg-cyber-card/30 hover:bg-cyber-card/50 transition-colors"
              >
                <div className={`p-2 rounded-lg ${
                  alert.severity === 'critical' ? 'bg-red-500/20' :
                  alert.severity === 'high' ? 'bg-orange-500/20' : 'bg-yellow-500/20'
                }`}>
                  {alert.severity === 'critical' ? <AlertTriangle className="w-4 h-4 text-red-400" /> :
                   alert.severity === 'high' ? <Shield className="w-4 h-4 text-orange-400" /> :
                   <Activity className="w-4 h-4 text-yellow-400" />}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-200 truncate">{alert.title}</p>
                  <p className="text-xs text-gray-500 truncate">{alert.employee_id} • {alert.description}</p>
                </div>
                <div className="text-right">
                  <span className={`text-sm font-bold ${alert.risk_score > 80 ? 'text-red-400' : alert.risk_score > 60 ? 'text-orange-400' : 'text-yellow-400'}`}>
                    {alert.risk_score?.toFixed(0)}
                  </span>
                  <p className="text-xs text-gray-600">{alert.metadata?.model_version || ''}</p>
                </div>
              </motion.div>
            ))}
            {liveAlerts.length === 0 && (
              <div className="text-center py-8 text-gray-500 text-sm">
                <XCircle className="w-8 h-8 mx-auto mb-2 opacity-50" />
                No AI alerts generated yet
              </div>
            )}
          </div>
        </motion.div>

        {/* Risk Distribution */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="glass-card p-6"
        >
          <h3 className="text-sm font-medium text-gray-300 mb-6">Alert Risk Distribution</h3>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%" cy="50%" innerRadius={60} outerRadius={90}
                paddingAngle={3} dataKey="value"
              >
                {pieData.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ background: '#111328', border: '1px solid #1e2048', borderRadius: '8px' }} />
            </PieChart>
          </ResponsiveContainer>
          <div className="grid grid-cols-5 gap-2 mt-4">
            {pieData.map((item, i) => (
              <div key={item.name} className="text-center">
                <div className="w-2 h-2 rounded-full mx-auto mb-1" style={{ backgroundColor: COLORS[i] }} />
                <p className="text-xs text-gray-400">{item.name}</p>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
