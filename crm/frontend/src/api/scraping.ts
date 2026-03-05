import api from './client';

export interface ScrapedData {
  id: string;
  lead_id: string | null;
  source_type: string;
  source_url: string;
  source_name: string;
  title: string | null;
  description: string | null;
  location: string | null;
  unit_count: number | null;
  scraped_at: string;
  is_matched: boolean;
  is_dismissed: boolean;
  confidence_score: number | null;
}

export interface DashboardStats {
  total_leads: number;
  active_leads: number;
  won_leads: number;
  lost_leads: number;
  total_units: number;
  pipeline_counts: Record<string, number>;
  recent_activities: Array<{
    id: string;
    lead_id: string;
    activity_type: string;
    title: string;
    description: string | null;
    created_at: string;
  }>;
  unmatched_scraped: number;
}

export async function getDashboard(): Promise<DashboardStats> {
  const { data } = await api.get('/dashboard');
  return data;
}

export async function getScrapedData(params?: {
  is_matched?: boolean;
  is_dismissed?: boolean;
  source_type?: string;
}): Promise<ScrapedData[]> {
  const { data } = await api.get('/scraping', { params });
  return data;
}

export async function triggerScrape(): Promise<{ message: string; results_count: number }> {
  const { data } = await api.post('/scraping/trigger');
  return data;
}

export async function linkToLead(scrapedId: string, leadId: string): Promise<ScrapedData> {
  const { data } = await api.post(`/scraping/${scrapedId}/link`, { lead_id: leadId });
  return data;
}

export async function dismissScraped(scrapedId: string): Promise<ScrapedData> {
  const { data } = await api.post(`/scraping/${scrapedId}/dismiss`);
  return data;
}

export async function createLeadFromScraped(scrapedId: string): Promise<{ lead_id: string }> {
  const { data } = await api.post(`/scraping/${scrapedId}/create-lead`);
  return data;
}
