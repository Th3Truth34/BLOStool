import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Building2, TrendingUp, Trophy, XCircle, Globe, Activity } from 'lucide-react';
import { getDashboard, type DashboardStats } from '../api/scraping';
import { STATUS_LABELS, STATUS_COLORS, type LeadStatus } from '../types/lead';

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDashboard().then(setStats).catch(console.error).finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="flex items-center justify-center h-64 text-gray-500">Loading dashboard...</div>;
  }

  if (!stats) {
    return <div className="text-red-500">Failed to load dashboard</div>;
  }

  const statCards = [
    { label: 'Active Leads', value: stats.active_leads, icon: Building2, color: 'blue' },
    { label: 'Total Units', value: stats.total_units.toLocaleString(), icon: TrendingUp, color: 'purple' },
    { label: 'Won Deals', value: stats.won_leads, icon: Trophy, color: 'green' },
    { label: 'Lost Deals', value: stats.lost_leads, icon: XCircle, color: 'red' },
    { label: 'Unreviewed Leads', value: stats.unmatched_scraped, icon: Globe, color: 'orange' },
    { label: 'Total Leads', value: stats.total_leads, icon: Activity, color: 'indigo' },
  ];

  const colorMap: Record<string, string> = {
    blue: 'bg-blue-50 text-blue-700 border-blue-200',
    purple: 'bg-purple-50 text-purple-700 border-purple-200',
    green: 'bg-green-50 text-green-700 border-green-200',
    red: 'bg-red-50 text-red-700 border-red-200',
    orange: 'bg-orange-50 text-orange-700 border-orange-200',
    indigo: 'bg-indigo-50 text-indigo-700 border-indigo-200',
  };

  const iconColorMap: Record<string, string> = {
    blue: 'text-blue-500',
    purple: 'text-purple-500',
    green: 'text-green-500',
    red: 'text-red-500',
    orange: 'text-orange-500',
    indigo: 'text-indigo-500',
  };

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500 mt-1">Multifamily housing leads overview</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {statCards.map((card) => (
          <div key={card.label} className={`p-6 rounded-xl border ${colorMap[card.color]}`}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium opacity-75">{card.label}</p>
                <p className="text-3xl font-bold mt-1">{card.value}</p>
              </div>
              <card.icon size={32} className={iconColorMap[card.color]} />
            </div>
          </div>
        ))}
      </div>

      {/* Pipeline Summary */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-8">
        <h2 className="text-lg font-semibold mb-4">Pipeline Summary</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Object.entries(stats.pipeline_counts).map(([status, count]) => (
            <Link
              key={status}
              to={`/leads?status=${status}`}
              className="p-4 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors"
            >
              <span className={`inline-block px-2 py-1 rounded text-xs font-medium ${STATUS_COLORS[status as LeadStatus] || 'bg-gray-100 text-gray-800'}`}>
                {STATUS_LABELS[status as LeadStatus] || status}
              </span>
              <p className="text-2xl font-bold mt-2">{count}</p>
            </Link>
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="text-lg font-semibold mb-4">Recent Activity</h2>
        {stats.recent_activities.length === 0 ? (
          <p className="text-gray-500 text-sm">No recent activity. Create a lead to get started.</p>
        ) : (
          <div className="space-y-3">
            {stats.recent_activities.map((activity) => (
              <Link
                key={activity.id}
                to={`/leads/${activity.lead_id}`}
                className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="w-2 h-2 rounded-full bg-blue-500 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">{activity.title}</p>
                  {activity.description && (
                    <p className="text-xs text-gray-500 truncate">{activity.description}</p>
                  )}
                </div>
                <span className="text-xs text-gray-400 flex-shrink-0">
                  {new Date(activity.created_at).toLocaleDateString()}
                </span>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
