import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { UserPlus, Search, Shield, MoreVertical, CheckCircle2, XCircle, Edit3, Trash2 } from 'lucide-react';
import { authAPI } from '../lib/api';
import { ROLE_META, Role } from '../lib/roles';

interface ManagedUser {
  id: number;
  email: string;
  username: string;
  full_name: string;
  role: string;
  department: string;
  is_active: boolean;
  created_at: string;
}

export default function UserManagementPage() {
  const [users, setUsers] = useState<ManagedUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showAdd, setShowAdd] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Add user form
  const [form, setForm] = useState({
    email: '',
    username: '',
    password: '',
    full_name: '',
    role: 'analyst',
    department: 'Engineering',
  });

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const res = await authAPI.getUsers();
      setUsers(res.data || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const handleAddUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    try {
      await authAPI.register(form);
      setSuccess('User created successfully');
      setShowAdd(false);
      setForm({ email: '', username: '', password: '', full_name: '', role: 'analyst', department: 'Engineering' });
      fetchUsers();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create user');
    }
  };

  const filteredUsers = users.filter((u) =>
    u.full_name.toLowerCase().includes(search.toLowerCase()) ||
    u.username.toLowerCase().includes(search.toLowerCase()) ||
    u.role.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold gradient-text">User Management</h1>
          <p className="text-gray-500 text-sm mt-1">Manage platform users and their roles</p>
        </div>
        <button
          onClick={() => setShowAdd(!showAdd)}
          className="flex items-center gap-2 px-4 py-2 glass-button-primary text-sm"
        >
          <UserPlus className="w-4 h-4" />
          Add User
        </button>
      </div>

      {error && (
        <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">{error}</div>
      )}
      {success && (
        <div className="p-3 bg-green-500/10 border border-green-500/30 rounded-lg text-green-400 text-sm">{success}</div>
      )}

      {/* Add User Form */}
      {showAdd && (
        <motion.form
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          onSubmit={handleAddUser}
          className="glass-card p-6 grid grid-cols-1 md:grid-cols-3 gap-4"
        >
          <div>
            <label className="block text-xs text-gray-400 mb-1">Full Name</label>
            <input
              type="text" required value={form.full_name}
              onChange={(e) => setForm({ ...form, full_name: e.target.value })}
              className="glass-input w-full text-sm"
            />
          </div>
          <div>
            <label className="block text-xs text-gray-400 mb-1">Username</label>
            <input
              type="text" required value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              className="glass-input w-full text-sm"
            />
          </div>
          <div>
            <label className="block text-xs text-gray-400 mb-1">Email</label>
            <input
              type="email" required value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              className="glass-input w-full text-sm"
            />
          </div>
          <div>
            <label className="block text-xs text-gray-400 mb-1">Password</label>
            <input
              type="password" required value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              className="glass-input w-full text-sm"
            />
          </div>
          <div>
            <label className="block text-xs text-gray-400 mb-1">Role</label>
            <select
              value={form.role}
              onChange={(e) => setForm({ ...form, role: e.target.value })}
              className="glass-input w-full text-sm"
            >
              <option value="admin">Admin</option>
              <option value="analyst">Analyst</option>
              <option value="compliance">Compliance</option>
              <option value="viewer">Viewer</option>
            </select>
          </div>
          <div>
            <label className="block text-xs text-gray-400 mb-1">Department</label>
            <input
              type="text" value={form.department}
              onChange={(e) => setForm({ ...form, department: e.target.value })}
              className="glass-input w-full text-sm"
            />
          </div>
          <div className="md:col-span-3 flex gap-2">
            <button type="submit" className="px-4 py-2 glass-button-primary text-sm">Create User</button>
            <button type="button" onClick={() => setShowAdd(false)} className="px-4 py-2 glass-button text-sm">Cancel</button>
          </div>
        </motion.form>
      )}

      {/* Search */}
      <div className="glass-card p-4">
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          <input
            type="text" placeholder="Search users by name, username or role..."
            value={search} onChange={(e) => setSearch(e.target.value)}
            className="glass-input w-full pl-10"
          />
        </div>
      </div>

      {/* Users Table */}
      <div className="glass-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-cyber-border/50">
                <th className="text-left p-4 text-xs font-medium text-gray-400 uppercase tracking-wider">User</th>
                <th className="text-left p-4 text-xs font-medium text-gray-400 uppercase tracking-wider">Role</th>
                <th className="text-left p-4 text-xs font-medium text-gray-400 uppercase tracking-wider">Department</th>
                <th className="text-left p-4 text-xs font-medium text-gray-400 uppercase tracking-wider">Status</th>
                <th className="text-left p-4 text-xs font-medium text-gray-400 uppercase tracking-wider">Created</th>
                <th className="text-right p-4 text-xs font-medium text-gray-400 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-cyber-border/30">
              {filteredUsers.map((u, index) => {
                const roleMeta = ROLE_META[u.role as Role] || { label: u.role, color: 'from-gray-400 to-slate-500' };
                return (
                  <motion.tr
                    key={u.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.02 }}
                    className="hover:bg-cyber-card/30 transition-colors"
                  >
                    <td className="p-4">
                      <div className="flex items-center gap-3">
                        <div className={`w-10 h-10 rounded-full bg-gradient-to-br ${roleMeta.color} flex items-center justify-center text-white text-sm font-bold`}>
                          {u.full_name.charAt(0)}
                        </div>
                        <div>
                          <p className="text-sm font-medium text-gray-200">{u.full_name}</p>
                          <p className="text-xs text-gray-500">{u.email}</p>
                        </div>
                      </div>
                    </td>
                    <td className="p-4">
                      <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-primary-500/10 text-primary-300 border border-primary-500/20">
                        {roleMeta.label}
                      </span>
                    </td>
                    <td className="p-4"><span className="text-sm text-gray-300">{u.department}</span></td>
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        {u.is_active ? (
                          <CheckCircle2 className="w-4 h-4 text-green-400" />
                        ) : (
                          <XCircle className="w-4 h-4 text-red-400" />
                        )}
                        <span className={`text-xs ${u.is_active ? 'text-green-400' : 'text-red-400'}`}>
                          {u.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </div>
                    </td>
                    <td className="p-4">
                      <span className="text-sm text-gray-500">
                        {u.created_at ? new Date(u.created_at).toLocaleDateString() : '-'}
                      </span>
                    </td>
                    <td className="p-4 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <button className="p-1.5 hover:bg-cyber-card rounded transition-colors">
                          <Edit3 className="w-4 h-4 text-gray-500" />
                        </button>
                        <button className="p-1.5 hover:bg-cyber-card rounded transition-colors">
                          <Trash2 className="w-4 h-4 text-gray-500" />
                        </button>
                      </div>
                    </td>
                  </motion.tr>
                );
              })}
              {filteredUsers.length === 0 && !loading && (
                <tr>
                  <td colSpan={6} className="p-8 text-center text-gray-500 text-sm">No users found</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
