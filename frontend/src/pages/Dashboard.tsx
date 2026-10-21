import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getAlerts, acknowledgeAlert } from '../api';
import { ShieldAlert, LogOut, Activity, AlertTriangle, Check } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

export default function Dashboard() {
  const [alerts, setAlerts] = useState<any[]>([]);
  const navigate = useNavigate();

  const fetchAlerts = () => getAlerts().then(setAlerts).catch(console.error);

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  const handleAcknowledge = async (alertId: string) => {
    await acknowledgeAlert(alertId);
    fetchAlerts(); // Refresh immediately
  };

  const attackTypes = alerts.reduce((acc: any, alert) => {
    acc[alert.alert_type] = (acc[alert.alert_type] || 0) + 1;
    return acc;
  }, {});

  const pieData = Object.keys(attackTypes).map(key => ({
    name: key, value: attackTypes[key]
  }));

  const COLORS = ['#ef4444', '#f97316', '#eab308', '#3b82f6'];

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <nav className="bg-slate-800 border-b border-slate-700 p-4 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <ShieldAlert className="w-8 h-8 text-blue-500" />
          <h1 className="text-xl font-bold">E-Gov IDS Dashboard</h1>
        </div>
        <button onClick={handleLogout} className="flex items-center gap-2 text-slate-300 hover:text-white transition-colors">
          <LogOut className="w-5 h-5" /> Logout
        </button>
      </nav>

      <main className="p-6 max-w-7xl mx-auto space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 flex items-center gap-4">
            <div className="p-3 bg-blue-500/20 rounded-lg text-blue-400"><Activity className="w-8 h-8" /></div>
            <div>
              <p className="text-slate-400 text-sm">Total Alerts</p>
              <p className="text-2xl font-bold">{alerts.length}</p>
            </div>
          </div>
          <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 flex items-center gap-4">
            <div className="p-3 bg-red-500/20 rounded-lg text-red-400"><AlertTriangle className="w-8 h-8" /></div>
            <div>
              <p className="text-slate-400 text-sm">Critical Alerts</p>
              <p className="text-2xl font-bold">{alerts.filter(a => a.severity === 'critical').length}</p>
            </div>
          </div>
          <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 flex items-center gap-4">
            <div className="p-3 bg-emerald-500/20 rounded-lg text-emerald-400"><Check className="w-8 h-8" /></div>
            <div>
              <p className="text-slate-400 text-sm">Acknowledged</p>
              <p className="text-2xl font-bold">{alerts.filter(a => a.status === 'acknowledged').length}</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
            <div className="p-4 border-b border-slate-700">
              <h2 className="font-semibold text-lg">Recent Alerts</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-slate-900/50 text-slate-400">
                  <tr>
                    <th className="px-4 py-3 font-medium">Severity</th>
                    <th className="px-4 py-3 font-medium">Type</th>
                    <th className="px-4 py-3 font-medium">Source IP</th>
                    <th className="px-4 py-3 font-medium">Time</th>
                    <th className="px-4 py-3 font-medium">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700">
                  {alerts.map((alert) => (
                    <tr key={alert.id} className="hover:bg-slate-700/50">
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 rounded text-xs font-bold ${
                          alert.severity === 'critical' ? 'bg-red-500/20 text-red-400' :
                          alert.severity === 'high' ? 'bg-orange-500/20 text-orange-400' :
                          'bg-blue-500/20 text-blue-400'
                        }`}>
                          {alert.severity.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-4 py-3 font-medium">{alert.alert_type}</td>
                      <td className="px-4 py-3 font-mono text-slate-300">{alert.source_ip}</td>
                      <td className="px-4 py-3 text-slate-400">{new Date(alert.created_at).toLocaleTimeString()}</td>
                      <td className="px-4 py-3">
                        {alert.status === 'acknowledged' ? (
                          <span className="text-emerald-400 text-xs flex items-center gap-1">
                            <Check className="w-4 h-4" /> Done
                          </span>
                        ) : (
                          <button
                            onClick={() => handleAcknowledge(alert.id)}
                            className="bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium px-3 py-1 rounded transition-colors"
                          >
                            Acknowledge
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                  {alerts.length === 0 && (
                    <tr>
                      <td colSpan={5} className="px-4 py-8 text-center text-slate-500">No alerts detected yet.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          <div className="bg-slate-800 rounded-xl border border-slate-700 p-4">
            <h2 className="font-semibold text-lg mb-4">Attack Types</h2>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px' }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}