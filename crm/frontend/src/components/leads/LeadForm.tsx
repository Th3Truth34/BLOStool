import { useState } from 'react';
import { X } from 'lucide-react';
import type { Lead } from '../../types/lead';

interface Props {
  onSubmit: (data: Partial<Lead>) => Promise<void>;
  onClose: () => void;
  initial?: Partial<Lead>;
}

export default function LeadForm({ onSubmit, onClose, initial }: Props) {
  const [data, setData] = useState<Partial<Lead>>(initial || { priority: 3, source: 'manual' });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await onSubmit(data);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <form onSubmit={handleSubmit} className="bg-white rounded-xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold">{initial ? 'Edit Lead' : 'New Lead'}</h2>
          <button type="button" onClick={onClose} className="p-1 hover:bg-gray-100 rounded">
            <X size={20} />
          </button>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">Project Name *</label>
            <input
              value={data.project_name || ''}
              onChange={(e) => setData({ ...data, project_name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Source</label>
            <select
              value={data.source || 'manual'}
              onChange={(e) => setData({ ...data, source: e.target.value as any })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            >
              <option value="manual">Manual Entry</option>
              <option value="referral">Referral</option>
              <option value="scraped_permit">Scraped - Permit</option>
              <option value="scraped_news">Scraped - News</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
            <select
              value={data.priority || 3}
              onChange={(e) => setData({ ...data, priority: parseInt(e.target.value) })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            >
              {[1, 2, 3, 4, 5].map((n) => (
                <option key={n} value={n}>{n} - {['Lowest', 'Low', 'Medium', 'High', 'Highest'][n - 1]}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Unit Count</label>
            <input
              type="number"
              value={data.unit_count || ''}
              onChange={(e) => setData({ ...data, unit_count: parseInt(e.target.value) || undefined })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Estimated Value</label>
            <input
              value={data.estimated_value || ''}
              onChange={(e) => setData({ ...data, estimated_value: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              placeholder="$1,000,000"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Project Type</label>
            <select
              value={data.project_type || ''}
              onChange={(e) => setData({ ...data, project_type: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            >
              <option value="">Select...</option>
              <option value="new_construction">New Construction</option>
              <option value="renovation">Renovation</option>
              <option value="conversion">Conversion</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Construction Phase</label>
            <select
              value={data.construction_phase || ''}
              onChange={(e) => setData({ ...data, construction_phase: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            >
              <option value="">Select...</option>
              <option value="planning">Planning</option>
              <option value="permitted">Permitted</option>
              <option value="under_construction">Under Construction</option>
              <option value="lease_up">Lease-Up</option>
            </select>
          </div>
          <div className="col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
            <input
              value={data.address || ''}
              onChange={(e) => setData({ ...data, address: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
            <input
              value={data.city || ''}
              onChange={(e) => setData({ ...data, city: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">State</label>
            <input
              value={data.state || ''}
              onChange={(e) => setData({ ...data, state: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              maxLength={2}
              placeholder="TX"
            />
          </div>
          <div className="col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
            <textarea
              value={data.notes || ''}
              onChange={(e) => setData({ ...data, notes: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              rows={3}
            />
          </div>
        </div>

        <div className="flex justify-end gap-2 mt-6">
          <button type="button" onClick={onClose} className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
            Cancel
          </button>
          <button type="submit" disabled={loading} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">
            {loading ? 'Saving...' : initial ? 'Update Lead' : 'Create Lead'}
          </button>
        </div>
      </form>
    </div>
  );
}
