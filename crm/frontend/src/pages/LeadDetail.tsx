import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Trash2, Edit2, Save, Plus, Phone, Mail, User, Building } from 'lucide-react';
import { getLead, updateLead, deleteLead } from '../api/leads';
import { getContacts, createContact, deleteContact } from '../api/contacts';
import type { Lead, LeadStatus } from '../types/lead';
import type { Contact } from '../types/contact';
import { STATUS_LABELS, STATUS_COLORS } from '../types/lead';
import { ROLE_LABELS } from '../types/contact';
import api from '../api/client';

interface ActivityItem {
  id: string;
  lead_id: string;
  activity_type: string;
  title: string;
  description: string | null;
  created_at: string;
}

export default function LeadDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [lead, setLead] = useState<Lead | null>(null);
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [activities, setActivities] = useState<ActivityItem[]>([]);
  const [editing, setEditing] = useState(false);
  const [editData, setEditData] = useState<Partial<Lead>>({});
  const [showAddContact, setShowAddContact] = useState(false);
  const [showAddActivity, setShowAddActivity] = useState(false);
  const [tab, setTab] = useState<'details' | 'contacts' | 'activities'>('details');

  const loadData = async () => {
    if (!id) return;
    const [leadData, contactsData, activitiesData] = await Promise.all([
      getLead(id),
      getContacts(id),
      api.get(`/leads/${id}/activities`).then(r => r.data),
    ]);
    setLead(leadData);
    setContacts(contactsData);
    setActivities(activitiesData);
  };

  useEffect(() => { loadData(); }, [id]);

  const handleSave = async () => {
    if (!id) return;
    await updateLead(id, editData);
    setEditing(false);
    loadData();
  };

  const handleDelete = async () => {
    if (!id || !confirm('Delete this lead? This cannot be undone.')) return;
    await deleteLead(id);
    navigate('/leads');
  };

  const handleStatusChange = async (newStatus: LeadStatus) => {
    if (!id) return;
    await updateLead(id, { status: newStatus });
    loadData();
  };

  const handleAddContact = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!id) return;
    const form = new FormData(e.currentTarget);
    await createContact(id, {
      first_name: form.get('first_name') as string,
      last_name: form.get('last_name') as string,
      role: form.get('role') as string,
      company: form.get('company') as string,
      email: form.get('email') as string,
      phone: form.get('phone') as string,
    });
    setShowAddContact(false);
    loadData();
  };

  const handleAddActivity = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!id) return;
    const form = new FormData(e.currentTarget);
    await api.post(`/leads/${id}/activities`, {
      activity_type: form.get('activity_type'),
      title: form.get('title'),
      description: form.get('description'),
    });
    setShowAddActivity(false);
    loadData();
  };

  if (!lead) return <div className="text-gray-500 py-12 text-center">Loading...</div>;

  const statuses: LeadStatus[] = ['new', 'researching', 'contacted', 'meeting_scheduled', 'proposal_sent', 'negotiating', 'won', 'lost'];

  return (
    <div>
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <button onClick={() => navigate('/leads')} className="p-2 hover:bg-gray-100 rounded-lg">
          <ArrowLeft size={20} />
        </button>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-gray-900">{lead.project_name}</h1>
          <p className="text-gray-500">
            {lead.city && lead.state ? `${lead.city}, ${lead.state}` : ''}
            {lead.unit_count ? ` \u2022 ${lead.unit_count} units` : ''}
          </p>
        </div>
        <button onClick={() => { setEditing(true); setEditData(lead); }} className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
          <Edit2 size={16} /> Edit
        </button>
        <button onClick={handleDelete} className="flex items-center gap-2 px-4 py-2 text-red-600 border border-red-200 rounded-lg hover:bg-red-50">
          <Trash2 size={16} /> Delete
        </button>
      </div>

      {/* Status Pipeline */}
      <div className="flex gap-1 mb-8 overflow-x-auto pb-2">
        {statuses.map((status) => (
          <button
            key={status}
            onClick={() => handleStatusChange(status)}
            className={`px-3 py-2 rounded-lg text-xs font-medium whitespace-nowrap transition-all ${
              lead.status === status
                ? `${STATUS_COLORS[status]} ring-2 ring-offset-2 ring-blue-500`
                : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
            }`}
          >
            {STATUS_LABELS[status]}
          </button>
        ))}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 border-b border-gray-200">
        {(['details', 'contacts', 'activities'] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              tab === t ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            {t.charAt(0).toUpperCase() + t.slice(1)}
            {t === 'contacts' && ` (${contacts.length})`}
            {t === 'activities' && ` (${activities.length})`}
          </button>
        ))}
      </div>

      {/* Details Tab */}
      {tab === 'details' && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          {editing ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Project Name</label>
                  <input
                    value={editData.project_name || ''}
                    onChange={(e) => setEditData({ ...editData, project_name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Unit Count</label>
                  <input
                    type="number"
                    value={editData.unit_count || ''}
                    onChange={(e) => setEditData({ ...editData, unit_count: parseInt(e.target.value) || null })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
                  <input
                    value={editData.city || ''}
                    onChange={(e) => setEditData({ ...editData, city: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">State</label>
                  <input
                    value={editData.state || ''}
                    onChange={(e) => setEditData({ ...editData, state: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    maxLength={2}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Priority (1-5)</label>
                  <input
                    type="number"
                    min={1}
                    max={5}
                    value={editData.priority || 3}
                    onChange={(e) => setEditData({ ...editData, priority: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Estimated Value</label>
                  <input
                    value={editData.estimated_value || ''}
                    onChange={(e) => setEditData({ ...editData, estimated_value: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    placeholder="$1,000,000"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Project Type</label>
                  <select
                    value={editData.project_type || ''}
                    onChange={(e) => setEditData({ ...editData, project_type: e.target.value })}
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
                    value={editData.construction_phase || ''}
                    onChange={(e) => setEditData({ ...editData, construction_phase: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  >
                    <option value="">Select...</option>
                    <option value="planning">Planning</option>
                    <option value="permitted">Permitted</option>
                    <option value="under_construction">Under Construction</option>
                    <option value="lease_up">Lease-Up</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
                <input
                  value={editData.address || ''}
                  onChange={(e) => setEditData({ ...editData, address: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Next Action</label>
                <input
                  value={editData.next_action || ''}
                  onChange={(e) => setEditData({ ...editData, next_action: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
                <textarea
                  value={editData.notes || ''}
                  onChange={(e) => setEditData({ ...editData, notes: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  rows={3}
                />
              </div>
              <div className="flex gap-2">
                <button onClick={handleSave} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                  <Save size={16} /> Save
                </button>
                <button onClick={() => setEditing(false)} className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">Cancel</button>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-6">
              <InfoRow label="Source" value={lead.source.replace('_', ' ')} />
              <InfoRow label="Priority" value={`${lead.priority}/5`} />
              <InfoRow label="Unit Count" value={lead.unit_count?.toLocaleString()} />
              <InfoRow label="Estimated Value" value={lead.estimated_value} />
              <InfoRow label="Project Type" value={lead.project_type?.replace('_', ' ')} />
              <InfoRow label="Construction Phase" value={lead.construction_phase?.replace('_', ' ')} />
              <InfoRow label="Address" value={lead.address} />
              <InfoRow label="Zip Code" value={lead.zip_code} />
              <InfoRow label="Next Action" value={lead.next_action} />
              <InfoRow label="Next Action Date" value={lead.next_action_date} />
              <InfoRow label="Estimated Completion" value={lead.estimated_completion} />
              <InfoRow label="Created" value={new Date(lead.created_at).toLocaleDateString()} />
              {lead.notes && (
                <div className="col-span-2">
                  <p className="text-sm text-gray-500">Notes</p>
                  <p className="text-sm text-gray-900 mt-1 whitespace-pre-wrap">{lead.notes}</p>
                </div>
              )}
              {lead.loss_reason && (
                <div className="col-span-2">
                  <p className="text-sm text-gray-500">Loss Reason</p>
                  <p className="text-sm text-red-600 mt-1">{lead.loss_reason}</p>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Contacts Tab */}
      {tab === 'contacts' && (
        <div>
          <div className="flex justify-end mb-4">
            <button onClick={() => setShowAddContact(true)} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
              <Plus size={16} /> Add Contact
            </button>
          </div>
          {contacts.length === 0 ? (
            <div className="bg-white rounded-xl border border-gray-200 p-12 text-center text-gray-500">
              No contacts yet. Add a contact to track project stakeholders.
            </div>
          ) : (
            <div className="grid gap-4">
              {contacts.map((contact) => (
                <div key={contact.id} className="bg-white rounded-xl border border-gray-200 p-6 flex items-start gap-4">
                  <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center">
                    <User size={20} className="text-gray-500" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h3 className="font-medium">{contact.first_name} {contact.last_name}</h3>
                      {contact.is_primary && <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">Primary</span>}
                    </div>
                    <p className="text-sm text-gray-500">{ROLE_LABELS[contact.role] || contact.role}</p>
                    {contact.company && <p className="text-sm text-gray-500 flex items-center gap-1 mt-1"><Building size={14} /> {contact.company}</p>}
                    <div className="flex gap-4 mt-2">
                      {contact.email && <span className="text-sm text-gray-600 flex items-center gap-1"><Mail size={14} /> {contact.email}</span>}
                      {contact.phone && <span className="text-sm text-gray-600 flex items-center gap-1"><Phone size={14} /> {contact.phone}</span>}
                    </div>
                  </div>
                  <button
                    onClick={async () => { await deleteContact(id!, contact.id); loadData(); }}
                    className="text-gray-400 hover:text-red-500"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              ))}
            </div>
          )}
          {showAddContact && (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
              <form onSubmit={handleAddContact} className="bg-white rounded-xl p-6 w-full max-w-lg">
                <h3 className="text-lg font-semibold mb-4">Add Contact</h3>
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <input name="first_name" placeholder="First name" required className="px-3 py-2 border border-gray-300 rounded-lg" />
                  <input name="last_name" placeholder="Last name" required className="px-3 py-2 border border-gray-300 rounded-lg" />
                  <select name="role" className="px-3 py-2 border border-gray-300 rounded-lg">
                    {Object.entries(ROLE_LABELS).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
                  </select>
                  <input name="company" placeholder="Company" className="px-3 py-2 border border-gray-300 rounded-lg" />
                  <input name="email" type="email" placeholder="Email" className="px-3 py-2 border border-gray-300 rounded-lg" />
                  <input name="phone" placeholder="Phone" className="px-3 py-2 border border-gray-300 rounded-lg" />
                </div>
                <div className="flex justify-end gap-2">
                  <button type="button" onClick={() => setShowAddContact(false)} className="px-4 py-2 border border-gray-300 rounded-lg">Cancel</button>
                  <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">Add</button>
                </div>
              </form>
            </div>
          )}
        </div>
      )}

      {/* Activities Tab */}
      {tab === 'activities' && (
        <div>
          <div className="flex justify-end mb-4">
            <button onClick={() => setShowAddActivity(true)} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
              <Plus size={16} /> Log Activity
            </button>
          </div>
          {activities.length === 0 ? (
            <div className="bg-white rounded-xl border border-gray-200 p-12 text-center text-gray-500">
              No activities yet. Log a call, email, or note.
            </div>
          ) : (
            <div className="space-y-3">
              {activities.map((activity) => (
                <div key={activity.id} className="bg-white rounded-xl border border-gray-200 p-4 flex items-start gap-3">
                  <div className="w-2 h-2 rounded-full bg-blue-500 mt-2 flex-shrink-0" />
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">{activity.activity_type}</span>
                      <span className="text-xs text-gray-400">{new Date(activity.created_at).toLocaleString()}</span>
                    </div>
                    <p className="font-medium text-sm mt-1">{activity.title}</p>
                    {activity.description && <p className="text-sm text-gray-500 mt-1">{activity.description}</p>}
                  </div>
                </div>
              ))}
            </div>
          )}
          {showAddActivity && (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
              <form onSubmit={handleAddActivity} className="bg-white rounded-xl p-6 w-full max-w-lg">
                <h3 className="text-lg font-semibold mb-4">Log Activity</h3>
                <div className="space-y-4 mb-4">
                  <select name="activity_type" className="w-full px-3 py-2 border border-gray-300 rounded-lg">
                    <option value="note">Note</option>
                    <option value="call">Call</option>
                    <option value="email">Email</option>
                    <option value="meeting">Meeting</option>
                    <option value="site_visit">Site Visit</option>
                  </select>
                  <input name="title" placeholder="Title" required className="w-full px-3 py-2 border border-gray-300 rounded-lg" />
                  <textarea name="description" placeholder="Description (optional)" className="w-full px-3 py-2 border border-gray-300 rounded-lg" rows={3} />
                </div>
                <div className="flex justify-end gap-2">
                  <button type="button" onClick={() => setShowAddActivity(false)} className="px-4 py-2 border border-gray-300 rounded-lg">Cancel</button>
                  <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">Log</button>
                </div>
              </form>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string | number | null | undefined }) {
  return (
    <div>
      <p className="text-sm text-gray-500">{label}</p>
      <p className="text-sm font-medium text-gray-900 mt-0.5">{value || '-'}</p>
    </div>
  );
}
