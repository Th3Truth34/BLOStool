import { useEffect, useState } from 'react';
import { Globe, RefreshCw, Check, X, Plus } from 'lucide-react';
import {
  getScrapedData,
  triggerScrape,
  dismissScraped,
  createLeadFromScraped,
  type ScrapedData,
} from '../api/scraping';

export default function Scraping() {
  const [data, setData] = useState<ScrapedData[]>([]);
  const [loading, setLoading] = useState(true);
  const [scraping, setScraping] = useState(false);
  const [filter, setFilter] = useState<'all' | 'unmatched' | 'matched' | 'dismissed'>('unmatched');
  const [lastResult, setLastResult] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const params: any = {};
      if (filter === 'unmatched') { params.is_matched = false; params.is_dismissed = false; }
      if (filter === 'matched') params.is_matched = true;
      if (filter === 'dismissed') params.is_dismissed = true;
      const results = await getScrapedData(params);
      setData(results);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  useEffect(() => { loadData(); }, [filter]);

  const handleScrape = async () => {
    setScraping(true);
    try {
      const result = await triggerScrape();
      setLastResult(`Found ${result.results_count} new results`);
      loadData();
    } catch (err: any) {
      setLastResult(`Error: ${err.response?.data?.detail || 'Scraping failed'}`);
    }
    setScraping(false);
  };

  const handleDismiss = async (id: string) => {
    await dismissScraped(id);
    loadData();
  };

  const handleCreateLead = async (id: string) => {
    await createLeadFromScraped(id);
    loadData();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Web Scraping</h1>
          <p className="text-gray-500 mt-1">Find multifamily construction leads from public data</p>
        </div>
        <button
          onClick={handleScrape}
          disabled={scraping}
          className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          <RefreshCw size={18} className={scraping ? 'animate-spin' : ''} />
          {scraping ? 'Scraping...' : 'Run Scrapers'}
        </button>
      </div>

      {lastResult && (
        <div className="bg-blue-50 text-blue-700 px-4 py-3 rounded-lg mb-6 text-sm flex items-center justify-between">
          {lastResult}
          <button onClick={() => setLastResult(null)} className="text-blue-500 hover:text-blue-700">
            <X size={16} />
          </button>
        </div>
      )}

      {/* Data Sources Info */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
        <h2 className="text-lg font-semibold mb-3">Data Sources</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
            <Globe size={20} className="text-blue-500 mt-0.5" />
            <div>
              <p className="font-medium text-sm">Building Permits</p>
              <p className="text-xs text-gray-500">City/county permit databases for new multifamily construction</p>
            </div>
          </div>
          <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
            <Globe size={20} className="text-green-500 mt-0.5" />
            <div>
              <p className="font-medium text-sm">Construction News</p>
              <p className="text-xs text-gray-500">RSS feeds from multifamily industry publications</p>
            </div>
          </div>
          <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
            <Globe size={20} className="text-purple-500 mt-0.5" />
            <div>
              <p className="font-medium text-sm">Planning Commissions</p>
              <p className="text-xs text-gray-500">Zoning changes and planning approvals (coming soon)</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filter */}
      <div className="flex gap-2 mb-6">
        {(['unmatched', 'matched', 'dismissed', 'all'] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === f ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      {/* Results */}
      {loading ? (
        <div className="text-gray-500 text-center py-12">Loading...</div>
      ) : data.length === 0 ? (
        <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
          <Globe size={48} className="mx-auto text-gray-300 mb-4" />
          <p className="text-gray-500">No scraped data found. Click "Run Scrapers" to find new leads.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {data.map((item) => (
            <div key={item.id} className="bg-white rounded-xl border border-gray-200 p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                      item.source_type === 'permit' ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'
                    }`}>
                      {item.source_type}
                    </span>
                    {item.confidence_score && (
                      <span className="text-xs text-gray-400">
                        {Math.round(item.confidence_score * 100)}% confidence
                      </span>
                    )}
                    <span className="text-xs text-gray-400">
                      {new Date(item.scraped_at).toLocaleDateString()}
                    </span>
                  </div>
                  <h3 className="font-medium text-gray-900">{item.title || 'Untitled'}</h3>
                  {item.description && (
                    <p className="text-sm text-gray-500 mt-1 line-clamp-2">{item.description}</p>
                  )}
                  <div className="flex gap-4 mt-2 text-xs text-gray-400">
                    {item.location && <span>Location: {item.location}</span>}
                    {item.unit_count && <span>Units: {item.unit_count}</span>}
                    <span>Source: {item.source_name}</span>
                  </div>
                </div>
                {!item.is_matched && !item.is_dismissed && (
                  <div className="flex gap-2 ml-4">
                    <button
                      onClick={() => handleCreateLead(item.id)}
                      className="flex items-center gap-1 px-3 py-1.5 bg-green-600 text-white rounded-lg text-sm hover:bg-green-700"
                      title="Create lead from this data"
                    >
                      <Plus size={14} /> Create Lead
                    </button>
                    <button
                      onClick={() => handleDismiss(item.id)}
                      className="p-1.5 text-gray-400 hover:text-red-500 rounded-lg hover:bg-gray-100"
                      title="Dismiss"
                    >
                      <X size={18} />
                    </button>
                  </div>
                )}
                {item.is_matched && (
                  <span className="flex items-center gap-1 text-xs text-green-600">
                    <Check size={14} /> Linked
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
