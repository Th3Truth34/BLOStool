import api from './client';
import type { Contact } from '../types/contact';

export async function getContacts(leadId: string): Promise<Contact[]> {
  const { data } = await api.get(`/leads/${leadId}/contacts`);
  return data;
}

export async function createContact(leadId: string, contact: Partial<Contact>): Promise<Contact> {
  const { data } = await api.post(`/leads/${leadId}/contacts`, contact);
  return data;
}

export async function updateContact(leadId: string, contactId: string, updates: Partial<Contact>): Promise<Contact> {
  const { data } = await api.patch(`/leads/${leadId}/contacts/${contactId}`, updates);
  return data;
}

export async function deleteContact(leadId: string, contactId: string): Promise<void> {
  await api.delete(`/leads/${leadId}/contacts/${contactId}`);
}
