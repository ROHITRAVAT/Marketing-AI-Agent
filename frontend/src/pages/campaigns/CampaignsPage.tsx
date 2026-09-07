import React from 'react';
import { Plus } from 'lucide-react';

export const CampaignsPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Campaign Management</h2>
          <p className="text-sm text-slate-400">
            Create, schedule, edit, and monitor your marketing campaigns.
          </p>
        </div>
        <button className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-lg transition-colors">
          <Plus className="w-4 h-4" />
          Create Campaign
        </button>
      </div>

      <div className="rounded-xl border border-dashed border-slate-800 bg-slate-900/50 p-12 text-center text-slate-400">
        Campaigns management table and status workflow (Ready for Task 5).
      </div>
    </div>
  );
};

export default CampaignsPage;
