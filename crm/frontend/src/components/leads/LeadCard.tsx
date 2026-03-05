import { Link } from 'react-router-dom';
import { MapPin, Building2, Calendar } from 'lucide-react';
import type { Lead } from '../../types/lead';

export default function LeadCard({ lead }: { lead: Lead }) {
  return (
    <Link
      to={`/leads/${lead.id}`}
      className="block bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow cursor-pointer"
    >
      <h3 className="font-medium text-sm text-gray-900 mb-2 truncate">{lead.project_name}</h3>
      <div className="space-y-1">
        {(lead.city || lead.state) && (
          <div className="flex items-center gap-1 text-xs text-gray-500">
            <MapPin size={12} />
            <span>{lead.city}{lead.state ? `, ${lead.state}` : ''}</span>
          </div>
        )}
        {lead.unit_count && (
          <div className="flex items-center gap-1 text-xs text-gray-500">
            <Building2 size={12} />
            <span>{lead.unit_count} units</span>
          </div>
        )}
        {lead.next_action && (
          <div className="flex items-center gap-1 text-xs text-gray-500">
            <Calendar size={12} />
            <span className="truncate">{lead.next_action}</span>
          </div>
        )}
      </div>
      <div className="flex items-center justify-between mt-3 pt-2 border-t border-gray-100">
        <div className="flex gap-0.5">
          {[1, 2, 3, 4, 5].map((n) => (
            <div key={n} className={`w-1.5 h-1.5 rounded-full ${n <= lead.priority ? 'bg-blue-500' : 'bg-gray-200'}`} />
          ))}
        </div>
        <span className="text-xs text-gray-400">{lead.source.replace('_', ' ')}</span>
      </div>
    </Link>
  );
}
