import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { AlertTriangle, Search, Filter, Plus, ChevronRight } from 'lucide-react';
import { incidentAPI } from '../lib/api';

const statusColors: Record<string, string> = {
  open: 'bg-red-500/20 text-red-400',
  investigating: 'bg-yellow-500/20 text-yellow-400',
  contained: 'bg-blue-500/20 text-blue-400',
  resolved: 'bg-green-500/20 text-green-400',
  false_positive: 'bg-gray-500/20 text-gray-400',
};

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await incidentAPI.getAll({ limit: 30 });
        setIncidents(res.data.incidents || []);
      } catch (err) {
        console.error('Failed to fetch incidents:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold gradient-text">Incidents</h1>
          <p className="text-gray-500 text-sm mt-1">Manage and investigate security incidents</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 glass-button-primary text-sm">
          <Plus className="w-4 h-4" />
          New Incident
        </button>
      </div>

      <div className="glass-card p-4">
        <div className="flex flex-wrap items-center gap-4">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <input type="text" placeholder="Search incidents..." className="glass-input w-full pl-10" />
          </div>
          <select className="glass-input w-40">
            <option>All Status</option>
            <option value="open">Open</option>
            <option value="investigating">Investigating</option>
            <option value="contained">Contained</option>
            <option value="resolved">Resolved</option>
          </select>
          <select className="glass-input w-40">
            <option>All Severity</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
          <button className="p-3 glass-input"><Filter className="w-4 h-4" /></button>
        </div>
      </div>

      <div className="space-y-3">
        {incidents.map((incident, index) => (
          <motion.div
            key={incident.incident_id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.03 }}
            onClick={() => navigate(`/incidents/${incident.incident_id}`)}
            className="glass-card p-5 hover:border-primary-500/30 transition-all duration-300 cursor-pointer"
          >
            <div className="flex items-start gap-4">
              <div className={`p-2.5 rounded-lg ${
                incident.severity === 'critical' ? 'bg-red-500/20' :
                incident.severity === 'high' ? 'bg-orange-500/20' : 'bg-yellow-500/20'
              }`}>
                <AlertTriangle className={`w-5 h-5 ${
                  incident.severity === 'critical' ? 'text-red-400' :
                  incident.severity === 'high' ? 'text-orange-400' : 'text-yellow-400'
                }`} />
              </div>
              <div className="flex-1">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="text-sm font-medium text-gray-200">{incident.title}</h3>
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                        statusColors[incident.status] || 'bg-gray-500/20 text-gray-400'
                      }`}>
                        {incident.status}
                      </span>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">{incident.description}</p>
                  </div>
                  <ChevronRight className="w-5 h-5 text-gray-600 ml-4" />
                </div>
                <div className="flex items-center gap-4 mt-3 text-xs text-gray-500">
                  <span className="font-medium text-gray-400">{incident.incident_id}</span>
                  <span>•</span>
                  <span>{incident.employee_name}</span>
                  <span>•</span>
                  <span>{incident.department}</span>
                  <span>•</span>
                  <span>Risk: {incident.risk_score?.toFixed(0)}</span>
                  <span>•</span>
                  <span>Confidence: {(incident.confidence * 100).toFixed(0)}%</span>
                  {incident.assigned_to && (
                    <>
                      <span>•</span>
                      <span>Assigned: {incident.assigned_to}</span>
                    </>
                  )}
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
