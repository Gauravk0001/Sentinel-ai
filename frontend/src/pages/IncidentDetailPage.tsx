import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  ArrowLeft, AlertTriangle, Clock, User, Shield,
  FileText, MessageSquare, Activity, ChevronRight
} from 'lucide-react';
import { incidentAPI } from '../lib/api';

const statusColors: Record<string, string> = {
  open: 'bg-red-500/20 text-red-400',
  investigating: 'bg-yellow-500/20 text-yellow-400',
  contained: 'bg-blue-500/20 text-blue-400',
  resolved: 'bg-green-500/20 text-green-400',
  false_positive: 'bg-gray-500/20 text-gray-400',
};

export default function IncidentDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [incident, setIncident] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await incidentAPI.getById(id!);
        setIncident(res.data);
      } catch (err) {
        console.error('Failed to fetch incident:', err);
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

  if (!incident) {
    return <div className="text-gray-400 text-center py-12">Incident not found</div>;
  }

  return (
    <div className="space-y-6 animate-in">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button onClick={() => navigate('/incidents')} className="p-2 hover:bg-cyber-card rounded-lg transition-colors">
          <ArrowLeft className="w-5 h-5 text-gray-400" />
        </button>
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold gradient-text">{incident.title}</h1>
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${statusColors[incident.status] || ''}`}>
              {incident.status}
            </span>
          </div>
          <p className="text-gray-500 text-sm">{incident.incident_id} • {incident.employee_name} • {incident.department}</p>
        </div>
      </div>

      {/* AI Explanation */}
      {incident.ai_explanation && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card p-6 border-red-500/30"
        >
          <div className="flex items-center gap-3 mb-4">
            <Shield className="w-5 h-5 text-red-400" />
            <h2 className="text-sm font-medium text-gray-200">AI Threat Analysis</h2>
          </div>
          <div className="flex items-center gap-4 mb-4">
            <div>
              <p className="text-3xl font-bold text-red-400">{incident.ai_explanation.risk_score}</p>
              <p className="text-xs text-gray-500">Risk Score</p>
            </div>
            <div className="text-center">
              <p className="text-lg font-bold text-red-400">{incident.ai_explanation.threat_level}</p>
              <p className="text-xs text-gray-500">Threat Level</p>
            </div>
            <div className="text-center">
              <p className="text-lg font-bold text-cyan-400">{(incident.ai_explanation.confidence * 100).toFixed(0)}%</p>
              <p className="text-xs text-gray-500">Confidence</p>
            </div>
          </div>
          <div className="space-y-2">
            {incident.ai_explanation.reasons.map((reason: string, idx: number) => (
              <div key={idx} className="flex items-start gap-2 text-sm">
                <span className="text-red-400 mt-1">•</span>
                <span className="text-gray-300">{reason}</span>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Timeline */}
      {incident.timeline && (
        <div className="glass-card p-6">
          <h3 className="text-sm font-medium text-gray-300 mb-6">Incident Timeline</h3>
          <div className="relative">
            <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-cyber-border" />
            <div className="space-y-6">
              {incident.timeline.map((event: any, index: number) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="relative pl-10"
                >
                  <div className={`absolute left-2.5 w-3 h-3 rounded-full border-2 ${
                    event.type === 'detection' || event.type === 'incident_created'
                      ? 'bg-red-500 border-red-500'
                      : event.type === 'usb' || event.type === 'cloud_upload'
                      ? 'bg-yellow-500 border-yellow-500'
                      : 'bg-cyan-500 border-cyan-500'
                  }`} />
                  <div className="glass-card p-3">
                    <div className="flex items-center justify-between">
                      <p className="text-sm text-gray-200">{event.event}</p>
                      <p className="text-xs text-gray-500">{new Date(event.time).toLocaleTimeString()}</p>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">{new Date(event.time).toLocaleDateString()}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Suggested Actions */}
      {incident.suggested_actions && (
        <div className="glass-card p-6 border-orange-500/30">
          <h3 className="text-sm font-medium text-gray-300 mb-4">Suggested Actions</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {incident.suggested_actions.map((action: string, idx: number) => (
              <div key={idx} className="flex items-center gap-2 p-3 rounded-lg bg-cyber-card/50 text-sm">
                <span className="text-orange-400">⚠️</span>
                <span className="text-gray-300">{action}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
