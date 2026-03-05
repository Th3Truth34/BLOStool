import { useState } from 'react';
import type { PipelineColumn, LeadStatus } from '../../types/lead';
import { STATUS_LABELS, STATUS_COLORS } from '../../types/lead';
import LeadCard from './LeadCard';

interface Props {
  pipeline: PipelineColumn[];
  onStatusChange: (leadId: string, newStatus: LeadStatus) => Promise<void>;
}

export default function LeadPipeline({ pipeline, onStatusChange }: Props) {
  const [draggedLeadId, setDraggedLeadId] = useState<string | null>(null);
  const [dragOverStatus, setDragOverStatus] = useState<LeadStatus | null>(null);

  const handleDragStart = (leadId: string) => {
    setDraggedLeadId(leadId);
  };

  const handleDragOver = (e: React.DragEvent, status: LeadStatus) => {
    e.preventDefault();
    setDragOverStatus(status);
  };

  const handleDrop = async (status: LeadStatus) => {
    if (draggedLeadId) {
      await onStatusChange(draggedLeadId, status);
    }
    setDraggedLeadId(null);
    setDragOverStatus(null);
  };

  const handleDragEnd = () => {
    setDraggedLeadId(null);
    setDragOverStatus(null);
  };

  return (
    <div className="flex gap-4 overflow-x-auto pb-4" style={{ minHeight: '70vh' }}>
      {pipeline.map((column) => (
        <div
          key={column.status}
          className={`flex-shrink-0 w-72 rounded-xl transition-colors ${
            dragOverStatus === column.status ? 'bg-blue-50 ring-2 ring-blue-300' : 'bg-gray-100'
          }`}
          onDragOver={(e) => handleDragOver(e, column.status)}
          onDrop={() => handleDrop(column.status)}
          onDragLeave={() => setDragOverStatus(null)}
        >
          <div className="p-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className={`px-2 py-1 rounded text-xs font-medium ${STATUS_COLORS[column.status]}`}>
                {STATUS_LABELS[column.status]}
              </span>
            </div>
            <span className="text-sm text-gray-500 font-medium">{column.count}</span>
          </div>
          <div className="p-2 space-y-2">
            {column.leads.map((lead) => (
              <div
                key={lead.id}
                draggable
                onDragStart={() => handleDragStart(lead.id)}
                onDragEnd={handleDragEnd}
                className={`${draggedLeadId === lead.id ? 'opacity-50' : ''}`}
              >
                <LeadCard lead={lead} />
              </div>
            ))}
            {column.leads.length === 0 && (
              <div className="text-center text-sm text-gray-400 py-8">
                Drop leads here
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
