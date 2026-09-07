import React from 'react';

export const AnalyticsPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">Marketing Analytics</h2>
        <p className="text-sm text-slate-400">
          Visualize engagement metrics, KPIs, and campaign performance across channels.
        </p>
      </div>

      <div className="rounded-xl border border-dashed border-slate-800 bg-slate-900/50 p-12 text-center text-slate-400">
        Analytics charts and social media metrics dashboard (Ready for Task 6).
      </div>
    </div>
  );
};

export default AnalyticsPage;
