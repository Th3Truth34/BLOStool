export interface Contact {
  id: string;
  lead_id: string;
  first_name: string;
  last_name: string;
  role: string;
  company: string | null;
  email: string | null;
  phone: string | null;
  is_primary: boolean;
  notes: string | null;
  created_at: string;
}

export const ROLE_LABELS: Record<string, string> = {
  developer: 'Developer',
  property_manager: 'Property Manager',
  owner: 'Owner',
  architect: 'Architect',
  general_contractor: 'General Contractor',
  leasing_agent: 'Leasing Agent',
  other: 'Other',
};
