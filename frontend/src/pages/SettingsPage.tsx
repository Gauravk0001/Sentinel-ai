import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Shield, Bell, Eye, Lock, Globe, Sliders,
  Save, RefreshCw, User, Key, Webhook
} from 'lucide-react';

const settingsSections = [
  {
    id: 'general',
    title: 'General Settings',
    icon: Sliders,
    items: [
      { label: 'Organization Name', value: 'SentinelAI Security', type: 'text' },
      { label: 'Monitoring Status', value: 'Active', type: 'toggle' },
      { label: 'Data Retention (days)', value: '90', type: 'number' },
      { label: 'Alert Frequency', value: 'Real-time', type: 'select', options: ['Real-time', 'Hourly', 'Daily'] },
    ],
  },
  {
    id: 'monitoring',
    title: 'Monitoring Configuration',
    icon: Eye,
    items: [
      { label: 'File Activity Monitoring', value: 'Enabled', type: 'toggle' },
      { label: 'USB Device Detection', value: 'Enabled', type: 'toggle' },
      { label: 'Cloud Upload Tracking', value: 'Enabled', type: 'toggle' },
      { label: 'Email Metadata Analysis', value: 'Enabled', type: 'toggle' },
      { label: 'Network Traffic Analysis', value: 'Enabled', type: 'toggle' },
      { label: 'Application Usage Tracking', value: 'Enabled', type: 'toggle' },
    ],
  },
  {
    id: 'ai',
    title: 'AI Engine',
    icon: Shield,
    items: [
      { label: 'Anomaly Detection Sensitivity', value: 'Medium', type: 'select', options: ['Low', 'Medium', 'High', 'Very High'] },
      { label: 'False Positive Reduction', value: 'Enabled', type: 'toggle' },
      { label: 'Auto-incident Creation', value: 'Enabled', type: 'toggle' },
      { label: 'Risk Score Threshold', value: '60', type: 'number' },
      { label: 'Model Auto-retrain', value: 'Weekly', type: 'select', options: ['Daily', 'Weekly', 'Monthly'] },
    ],
  },
  {
    id: 'notifications',
    title: 'Notifications',
    icon: Bell,
    items: [
      { label: 'Email Alerts', value: 'Enabled', type: 'toggle' },
      { label: 'Browser Notifications', value: 'Enabled', type: 'toggle' },
      { label: 'Slack Integration', value: 'Not configured', type: 'button' },
      { label: 'Teams Integration', value: 'Not configured', type: 'button' },
    ],
  },
  {
    id: 'security',
    title: 'Security',
    icon: Lock,
    items: [
      { label: 'Two-Factor Authentication', value: 'Disabled', type: 'toggle' },
      { label: 'Session Timeout (minutes)', value: '30', type: 'number' },
      { label: 'Password Policy', value: 'Strong', type: 'select', options: ['Basic', 'Medium', 'Strong', 'Very Strong'] },
      { label: 'IP Whitelisting', value: 'Disabled', type: 'toggle' },
    ],
  },
];

export default function SettingsPage() {
  const [activeSection, setActiveSection] = useState('general');
  const [saving, setSaving] = useState(false);

  const handleSave = () => {
    setSaving(true);
    setTimeout(() => setSaving(false), 1500);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold gradient-text">Settings</h1>
          <p className="text-gray-500 text-sm mt-1">Configure your SentinelAI platform</p>
        </div>
        <button
          onClick={handleSave}
          disabled={saving}
          className="flex items-center gap-2 px-4 py-2 glass-button-primary text-sm"
        >
          {saving ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              Saving...
            </>
          ) : (
            <>
              <Save className="w-4 h-4" />
              Save Changes
            </>
          )}
        </button>
      </div>

      <div className="flex gap-6">
        {/* Sidebar */}
        <div className="w-56 flex-shrink-0 space-y-1">
          {settingsSections.map((section) => (
            <button
              key={section.id}
              onClick={() => setActiveSection(section.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm transition-all ${
                activeSection === section.id
                  ? 'bg-primary-600/20 text-primary-300 border border-primary-500/30'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-cyber-card/50'
              }`}
            >
              <section.icon className="w-4 h-4" />
              {section.title}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="flex-1 space-y-6">
          {settingsSections.map((section) => (
            <motion.div
              key={section.id}
              initial={false}
              animate={{
                opacity: activeSection === section.id ? 1 : 0,
                height: activeSection === section.id ? 'auto' : 0,
                overflow: 'hidden',
              }}
              transition={{ duration: 0.3 }}
            >
              {activeSection === section.id && (
                <div className="glass-card p-6 space-y-6">
                  <div className="flex items-center gap-3 pb-4 border-b border-cyber-border/30">
                    <section.icon className="w-5 h-5 text-primary-400" />
                    <h2 className="text-lg font-medium text-gray-200">{section.title}</h2>
                  </div>
                  <div className="space-y-4">
                    {section.items.map((item, idx) => (
                      <div key={idx} className="flex items-center justify-between py-2">
                        <div>
                          <p className="text-sm text-gray-300">{item.label}</p>
                        </div>
                        {item.type === 'toggle' && (
                          <label className="relative inline-flex items-center cursor-pointer">
                            <input type="checkbox" defaultChecked={item.value === 'Enabled'} className="sr-only peer" />
                            <div className="w-11 h-6 bg-cyber-dark rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600" />
                          </label>
                        )}
                        {item.type === 'text' && (
                          <input type="text" defaultValue={item.value} className="glass-input w-48 text-sm" />
                        )}
                        {item.type === 'number' && (
                          <input type="number" defaultValue={item.value} className="glass-input w-24 text-sm" />
                        )}
                        {item.type === 'select' && (
                          <select className="glass-input w-40 text-sm">
                            {item.options?.map((opt: string) => (
                              <option key={opt} value={opt}>{opt}</option>
                            ))}
                          </select>
                        )}
                        {item.type === 'button' && (
                          <button className="px-4 py-2 glass-button text-xs">
                            Configure
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
