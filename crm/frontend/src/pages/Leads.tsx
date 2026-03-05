import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { Plus, Search, Filter } from 'lucide-react';
import { getLeads, getPipeline, createLead, updateLead } from '../api/leads';
import type { Lead, PipelineColumn, LeadStatus } from '../types/lead';
import { STATUS_LABELS, STATUS_COLORS } from '../types/lead';
import LeadForm from '../components/leads/LeadForm';
import LeadPipeline from '../components/leads/LeadPipeline';

export default function Leads({ view }: { view?: string }) {
  const [searchParams] = useSearchParams();
  const [leads, setLeads] = useState<Lead[]>([]);
  const [pipeline, setPipeline] = useState<PipelineColumn[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState(searchParams.get('status') || '');

  const isPipeline = view === 'pipeline';

  const loadData = async () => {
    setLoading(true);
    try {
      if (isPipeline) {
        const data = await getPipeline();
        setPipeline(data);
      } else {
        const params: any = {};
        if (search) params.search = search;
        if (statusFilter) params.status = statusFilter;
        const data = await getLeads(params);
        setLeads(data);
      }
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  useEffect(() => { loadData(); }, [isPipeline, statusFilter]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadData();
  };

  const handleCreate = async (data: Partial<Lead>) => {
    await createLead(data);
    setShowForm(false);
    loadData();
  };

  const handleStatusChange = async (leadId: string, newStatus: LeadStatus) => {
    await updateLead(leadId, { status: newStatus });
    loadData();
  };

  if (isPipeline) {
    return (
      <div>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Pipeline</h1>
            <p className="text-gray-500 mt-1">Drag leads between stages</p>
          </div>
          <button
            onClick={() => setShowForm(true)}
            className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            <Plus size={18} /> New Lead
          </button>
        </div>
        {loading ? (
          <div className="text-gray-500 text-center py-12">Loading pipeline...</div>
        ) : (
          <LeadPipeline pipeline={pipeline} onStatusChange={handleStatusChange} />
        )}
        {showForm && <LeadForm onSubmit={handleCreate} onClose={() => setShowForm(false)} />}
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Leads</h1>
          <p className="text-gray-500 mt-1">{leads.length} total leads</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          <Plus size={18} /> New Lead
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-4 mb-6">
        <form onSubmit={handleSearch} className="flex-1 relative">
          <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search leads..."
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </form>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Statuses</option>
          {Object.entries(STATUS_LABELS).map(([value, label]) => (
            <option key={value} value={value}>{label}</option>
          ))}
        </select>
      </div>

      {/* Leads Table */}
      {loading ? (
        <div className="text-gray-500 text-center py-12">Loading...</div>
      ) : leads.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
          <p className="text-gray-500">No leads found. Create your first lead to get started.</p>
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 bg-gray-50">
                <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Project</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Location</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Units</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Source</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Priority</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Updated</th>
              </tr>
            </thead>
            <tbody>
              {leads.map((lead) => (
                <tr key={lead.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <Link to={`/leads/${lead.id}`} className="text-blue-600 hover:underline font-medium">
                      {lead.project_name}
                    </Link>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${STATUS_COLORS[lead.status]}`}>
                      {STATUS_LABELS[lead.status]}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    {lead.city && lead.state ? `${lead.city}, ${lead.state}` : lead.city || '-'}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">{lead.unit_count || '-'}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{lead.source.replace('_', ' ')}</td>
                  <td className="px-6 py-4">
                    <div className="flex gap-0.5">
                      {[1, 2, 3, 4, 5].map((n) => (
                        <div
                          key={n}
                          className={`w-2 h-2 rounded-full ${n <= lead.priority ? 'bg-blue-500' : 'bg-gray-200'}`}
                        />
                      ))}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {new Date(lead.updated_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showForm && <LeadForm onSubmit={handleCreate} onClose={() => setShowForm(false)} />}
    </div>
  );
}
