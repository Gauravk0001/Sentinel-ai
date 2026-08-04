import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Search, Filter, MoreVertical, Shield, ChevronDown, Download, SlidersHorizontal } from 'lucide-react';
import { employeeAPI } from '../lib/api';
import { THREAT_COLORS, THREAT_TEXT_COLORS, THREAT_BG_COLORS } from '../types';

export default function EmployeesPage() {
  const [employees, setEmployees] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [deptFilter, setDeptFilter] = useState('');
  const [riskFilter, setRiskFilter] = useState('');
  const [page, setPage] = useState(1);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await employeeAPI.getAll({ page, limit: 20, search, department: deptFilter, risk_level: riskFilter });
        setEmployees(res.data.employees || []);
      } catch (err) {
        console.error('Failed to fetch employees:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [page, search, deptFilter, riskFilter]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold gradient-text">Employees</h1>
          <p className="text-gray-500 text-sm mt-1">Monitor and manage employee security risk</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 glass-button-primary text-sm">
          <Download className="w-4 h-4" />
          Export Report
        </button>
      </div>

      <div className="glass-card p-4">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex-1 min-w-[200px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input
                type="text"
                placeholder="Search employees..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="glass-input w-full pl-10"
              />
            </div>
          </div>
          <select
            value={deptFilter}
            onChange={(e) => setDeptFilter(e.target.value)}
            className="glass-input w-40"
          >
            <option value="">All Departments</option>
            <option value="Engineering">Engineering</option>
            <option value="Sales">Sales</option>
            <option value="Marketing">Marketing</option>
            <option value="Finance">Finance</option>
            <option value="HR">HR</option>
            <option value="IT">IT</option>
          </select>
          <select
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
            className="glass-input w-40"
          >
            <option value="">All Risk Levels</option>
            <option value="Safe">Safe</option>
            <option value="Low">Low</option>
            <option value="Medium">Medium</option>
            <option value="High">High</option>
            <option value="Critical">Critical</option>
          </select>
          <button className="p-3 glass-input">
            <SlidersHorizontal className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="glass-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-cyber-border/50">
                <th className="text-left p-4 text-xs font-medium text-gray-400 uppercase tracking-wider">Employee</th>
                <th className="text-left p-4 text-xs font-medium text-gray-400 uppercase tracking-wider">Department</th>
                <th className="text-left p-4 text-xs font-medium text-gray-400 uppercase tracking-wider">Position</th>
                <th className="text-left p-4 text-xs font-medium text-gray-400 uppercase tracking-wider">Risk Score</th>
                <th className="text-left p-4 text-xs font-medium text-gray-400 uppercase tracking-wider">Threat Level</th>
                <th className="text-left p-4 text-xs font-medium text-gray-400 uppercase tracking-wider">Status</th>
                <th className="text-right p-4 text-xs font-medium text-gray-400 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-cyber-border/30">
              {employees.map((emp: any, index: number) => (
                <motion.tr
                  key={emp.employee_id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.02 }}
                  className="hover:bg-cyber-card/30 cursor-pointer transition-colors"
                  onClick={() => navigate(`/employees/${emp.employee_id}`)}
                >
                  <td className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-400 to-purple-500 flex items-center justify-center text-white text-sm font-bold">
                        {emp.name?.charAt(0) || '?'}
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-200">{emp.name}</p>
                        <p className="text-xs text-gray-500">{emp.email}</p>
                      </div>
                    </div>
                  </td>
                  <td className="p-4">
                    <span className="text-sm text-gray-300">{emp.department}</span>
                  </td>
                  <td className="p-4">
                    <span className="text-sm text-gray-400">{emp.position}</span>
                  </td>
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      <div className="w-20 h-1.5 bg-cyber-dark rounded-full overflow-hidden">
                        <div
                          className="h-full rounded-full transition-all duration-500"
                          style={{
                            width: `${emp.current_risk_score || 0}%`,
                            backgroundColor: emp.current_risk_score > 80 ? '#ff3366' : emp.current_risk_score > 60 ? '#ff9100' : emp.current_risk_score > 40 ? '#ffbb33' : emp.current_risk_score > 20 ? '#42a5f5' : '#00e676'
                          }}
                        />
                      </div>
                      <span className="text-sm font-mono text-gray-300">{emp.current_risk_score?.toFixed(0) || '0'}</span>
                    </div>
                  </td>
                  <td className="p-4">
                    <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${
                      THREAT_BG_COLORS[emp.current_threat_level as keyof typeof THREAT_BG_COLORS] || 'bg-gray-500/10'
                    } ${
                      THREAT_TEXT_COLORS[emp.current_threat_level as keyof typeof THREAT_TEXT_COLORS] || 'text-gray-400'
                    }`}>
                      {emp.current_threat_level || 'Safe'}
                    </span>
                  </td>
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      <div className={`w-2 h-2 rounded-full ${emp.is_remote ? 'bg-yellow-400' : 'bg-green-400'} animate-pulse`} />
                      <span className="text-xs text-gray-500">{emp.is_remote ? 'Remote' : 'On-site'}</span>
                    </div>
                  </td>
                  <td className="p-4 text-right">
                    <button className="p-1 hover:bg-cyber-card rounded transition-colors">
                      <MoreVertical className="w-4 h-4 text-gray-500" />
                    </button>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="flex items-center justify-between text-sm">
        <p className="text-gray-500">Showing {employees.length} of 1,000 employees</p>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-3 py-1.5 glass-input text-xs disabled:opacity-50"
          >
            Previous
          </button>
          <span className="px-3 py-1.5 text-gray-400">Page {page}</span>
          <button
            onClick={() => setPage(p => p + 1)}
            className="px-3 py-1.5 glass-input text-xs"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}


