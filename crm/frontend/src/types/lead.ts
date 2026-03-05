export type LeadStatus =
  | 'new'
  | 'researching'
  | 'contacted'
  | 'meeting_scheduled'
  | 'proposal_sent'
  | 'negotiating'
  | 'won'
  | 'lost';

export type LeadSource =
  | 'scraped_permit'
  | 'scraped_news'
  | 'scraped_planning'
  | 'manual'
  | 'referral';

export interface Lead {
  id: string;
  project_name: string;
  status: LeadStatus;
  source: LeadSource;
  priority: number;
  unit_count: number | null;
  estimated_value: string | null;
  project_type: string | null;
  construction_phase: string | null;
  estimated_completion: string | null;
  address: string | null;
  city: string | null;
  state: string | null;
  zip_code: string | null;
  next_action: string | null;
  next_action_date: string | null;
  loss_reason: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
  contact_count: number;
  activity_count: number;
}

export interface PipelineColumn {
  status: LeadStatus;
  count: number;
  leads: Lead[];
}

export const STATUS_LABELS: Record<LeadStatus, string> = {
  new: 'New Lead',
  researching: 'Researching',
  contacted: 'Contacted',
  meeting_scheduled: 'Meeting Scheduled',
  proposal_sent: 'Proposal Sent',
  negotiating: 'Negotiating',
  won: 'Won',
  lost: 'Lost',
};

export const STATUS_COLORS: Record<LeadStatus, string> = {
  new: 'bg-blue-100 text-blue-800',
  researching: 'bg-purple-100 text-purple-800',
  contacted: 'bg-yellow-100 text-yellow-800',
  meeting_scheduled: 'bg-orange-100 text-orange-800',
  proposal_sent: 'bg-indigo-100 text-indigo-800',
  negotiating: 'bg-pink-100 text-pink-800',
  won: 'bg-green-100 text-green-800',
  lost: 'bg-red-100 text-red-800',
};
