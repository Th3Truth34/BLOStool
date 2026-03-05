import api from './client';
import type { Lead, PipelineColumn } from '../types/lead';

export async function getLeads(params?: {
  status?: string;
  source?: string;
  city?: string;
  search?: string;
}): Promise<Lead[]> {
  const { data } = await api.get('/leads', { params });
  return data;
}

export async function getPipeline(): Promise<PipelineColumn[]> {
  const { data } = await api.get('/leads/pipeline');
  return data;
}

export async function getLead(id: string): Promise<Lead> {
  const { data } = await api.get(`/leads/${id}`);
  return data;
}

export async function createLead(lead: Partial<Lead>): Promise<Lead> {
  const { data } = await api.post('/leads', lead);
  return data;
}

export async function updateLead(id: string, updates: Partial<Lead>): Promise<Lead> {
  const { data } = await api.patch(`/leads/${id}`, updates);
  return data;
}

export async function deleteLead(id: string): Promise<void> {
  await api.delete(`/leads/${id}`);
}
