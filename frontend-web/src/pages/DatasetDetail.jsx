import { useState, useEffect, useMemo, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { datasetAPI, equipmentAPI } from '../services/api';
import {
  Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale,
  LinearScale, BarElement, Title, PointElement, LineElement
} from 'chart.js';
import { Pie, Scatter, Bar, Bubble } from 'react-chartjs-2';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title, PointElement, LineElement);

export default function DatasetDetail() {
  const { id } = useParams();
  const navigate = useNavigate();

  // Data State
  const [dataset, setDataset] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [equipment, setEquipment] = useState([]);
  const [loading, setLoading] = useState(true);

  // UX State
  const [activeView, setActiveView] = useState('safety'); // safety | distribution | correlation | data
  const [typeFilter, setTypeFilter] = useState('All'); // Global Filter
  const [isDark, setIsDark] = useState(false);

  // Dark Mode Toggle
  useEffect(() => {
    document.documentElement.classList.toggle('dark', isDark);
  }, [isDark]);

  useEffect(() => { loadData(); }, [id]);

  const loadData = async () => {
    try {
      const [d, a, e] = await Promise.all([
        datasetAPI.getById(id),
        datasetAPI.getAnalytics(id),
        equipmentAPI.getAll(id),
      ]);
      setDataset(d.data);
      setAnalytics(a.data);
      setEquipment(e.data.results || e.data || []);
    } catch (err) { alert("Failed to load data"); } finally { setLoading(false); }
  };

  const handleDownloadPDF = useCallback(async () => {
    try {
      const response = await datasetAPI.downloadPDF(id);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'report.pdf');
      document.body.appendChild(link); link.click(); link.remove();
    } catch (e) { alert('Download failed'); }
  }, [id]);

  // --- FILTER LOGIC ---
  const filteredEquipment = useMemo(() => {
    if (typeFilter === 'All') return equipment;
    return equipment.filter(e => e.equipment_type === typeFilter);
  }, [equipment, typeFilter]);

  const filteredAnalytics = useMemo(() => {
    if (!analytics) return null;
    if (typeFilter === 'All') return analytics;

    // Filter Scatter Data locally
    const filteredScatter = analytics.scatter_data.filter(d => d.type === typeFilter);
    return { ...analytics, scatter_data: filteredScatter };
  }, [analytics, typeFilter]);

  const uniqueTypes = useMemo(() => {
    if (!equipment.length) return [];
    return ['All', ...new Set(equipment.map(e => e.equipment_type))];
  }, [equipment]);

  // --- CHART CONFIG ---
  const commonOptions = {
    responsive: true, maintainAspectRatio: false,
    scales: {
      x: { grid: { color: isDark ? '#334155' : '#E2E8F0' }, ticks: { color: isDark ? '#94A3B8' : '#64748B' } },
      y: { grid: { color: isDark ? '#334155' : '#E2E8F0' }, ticks: { color: isDark ? '#94A3B8' : '#64748B' } }
    },
    plugins: { legend: { labels: { color: isDark ? '#E2E8F0' : '#1E293B' } } }
  };

  // 1. SAFETY VIEW DATA
  const safetyData = useMemo(() => {
    if (!filteredAnalytics) return null;
    const outliers = new Set(filteredAnalytics.outlier_equipment.map(o => o.name));
    return {
      datasets: [
        {
          label: 'Safe Operation',
          data: filteredAnalytics.scatter_data.filter(d => !outliers.has(d.name)),
          backgroundColor: isDark ? '#34D399' : '#10B981',
        },
        {
          label: 'Critical Alerts',
          data: filteredAnalytics.scatter_data.filter(d => outliers.has(d.name)),
          backgroundColor: isDark ? '#F87171' : '#EF4444',
          pointRadius: 8, pointStyle: 'triangle',
        }
      ]
    };
  }, [filteredAnalytics, isDark]);

  // 2. DISTRIBUTION VIEW DATA (Floating Bar Range)
  const distributionData = useMemo(() => {
    if (!analytics) return null;
    // Note: We use global analytics for benchmarks to allow comparison even when filtered
    const labels = Object.keys(analytics.peer_benchmarks);
    return {
      labels,
      datasets: [{
        label: 'Flowrate Range (Min to Max)',
        data: labels.map(t => [analytics.peer_benchmarks[t].flowrate_min, analytics.peer_benchmarks[t].flowrate_max]),
        backgroundColor: isDark ? '#60A5FA' : '#3B82F6',
        barPercentage: 0.5,
      }]
    };
  }, [analytics, isDark]);

  // 3. CORRELATION VIEW DATA (Bubble)
  const correlationData = useMemo(() => {
    if (!filteredAnalytics) return null;
    return {
      datasets: [{
        label: 'P vs T (Size = Flowrate)',
        data: filteredAnalytics.scatter_data.map(d => ({ x: d.x, y: d.y, r: Math.max(3, d.r / 15) })),
        backgroundColor: isDark ? 'rgba(129, 140, 248, 0.6)' : 'rgba(79, 70, 229, 0.6)',
      }]
    };
  }, [filteredAnalytics, isDark]);


  if (loading) return <div className="min-h-screen bg-slate-50 dark:bg-darkbg flex items-center justify-center text-slate-500">Loading Intelligence...</div>;

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-darkbg text-slate-900 dark:text-slate-100 transition-colors duration-300 flex flex-col">

      {/* --- WORLD-CLASS TOOLBAR HEADER --- */}
      <header className="bg-white dark:bg-darkcard border-b border-slate-200 dark:border-slate-700 sticky top-0 z-20 px-6 py-3 shadow-sm flex items-center justify-between">

        {/* Left: Title & Filter */}
        <div className="flex items-center gap-6">
          <div>
            <h1 className="text-lg font-black tracking-tight">{dataset?.filename}</h1>
            <p className="text-xs text-slate-500 font-bold uppercase tracking-wider">Dashboard</p>
          </div>

          {/* GLOBAL FILTER */}
          <div className="flex items-center gap-2 px-4 py-1.5 bg-slate-100 dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
            <span className="text-xs font-bold text-slate-400 uppercase">Filter:</span>
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="bg-transparent text-sm font-bold text-slate-700 dark:text-slate-200 focus:outline-none cursor-pointer"
            >
              {uniqueTypes.map(t => <option key={t} value={t}>{t} Equipment</option>)}
            </select>
          </div>
        </div>

        {/* Center: View Switcher (Pills) */}
        <div className="bg-slate-100 dark:bg-slate-800 p-1 rounded-lg border border-slate-200 dark:border-slate-700 flex">
          {[
            { id: 'safety', icon: '🛡️', label: 'Safety' },
            { id: 'distribution', icon: '📊', label: 'Distribution' },
            { id: 'correlation', icon: '🔗', label: 'Correlation' },
            { id: 'data', icon: '📋', label: 'Equipment Data' },
          ].map((v) => (
            <button
              key={v.id}
              onClick={() => setActiveView(v.id)}
              className={`px-4 py-1.5 rounded-md text-sm font-bold transition-all ${activeView === v.id
                  ? 'bg-white dark:bg-slate-600 text-blue-600 dark:text-white shadow-sm'
                  : 'text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'
                }`}
            >
              <span className="mr-2">{v.icon}</span>{v.label}
            </button>
          ))}
        </div>

        {/* Right: Actions */}
        <div className="flex items-center gap-3">
          <button onClick={() => setIsDark(!isDark)} className="p-2 text-lg hover:bg-slate-100 dark:hover:bg-slate-700 rounded-full transition-colors">
            {isDark ? 'light mode ☀️' : 'dark mode 🌙'}
          </button>
          <button onClick={handleDownloadPDF} className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-bold shadow-sm transition-colors">
            Generat Report
          </button>
          <button onClick={() => navigate('/dashboard')} className="text-slate-400 hover:text-red-500 px-2 font-bold">close✕</button>
        </div>
      </header>

      {/* --- KPI BAR (Always Visible) --- */}
      <div className="bg-white dark:bg-darkcard border-b border-slate-200 dark:border-slate-700 px-6 py-4 grid grid-cols-4 gap-4">
        {[
          { l: 'Active Units', v: filteredEquipment.length, c: 'text-indigo-600 dark:text-indigo-400' },
          { l: 'Avg Flowrate', v: analytics?.avg_flowrate, u: 'm³/h', c: 'text-blue-600 dark:text-blue-400' },
          { l: 'Avg Pressure', v: analytics?.avg_pressure, u: 'bar', c: 'text-emerald-600 dark:text-emerald-400' },
          { l: 'Avg Temp', v: analytics?.avg_temperature, u: '°C', c: 'text-orange-600 dark:text-orange-400' },
        ].map((k, i) => (
          <div key={i} className="flex flex-col">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{k.l}</span>
            <span className={`text-2xl font-black ${k.c}`}>{k.v}<span className="text-sm text-slate-400 ml-1 font-medium">{k.u}</span></span>
          </div>
        ))}
      </div>

      {/* --- MAIN STAGE --- */}
      <main className="flex-1 p-6 overflow-hidden flex flex-col">
        {activeView === 'data' ? (
          /* VIEW 4: RAW DATA TABLE (Full Screen) */
          <div className="flex-1 bg-white dark:bg-darkcard rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden flex flex-col shadow-sm">
            <div className="overflow-auto flex-1">
              <table className="w-full text-left text-sm">
                <thead className="bg-slate-50 dark:bg-slate-800 text-xs uppercase font-bold text-slate-500 sticky top-0 z-10">
                  <tr>
                    {['Name', 'Type', 'Flow', 'Pressure', 'Temp', 'Status'].map(h => <th key={h} className="px-6 py-3">{h}</th>)}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
                  {filteredEquipment.map(eq => (
                    <tr key={eq.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                      <td className="px-6 py-3 font-medium">{eq.equipment_name}</td>
                      <td className="px-6 py-3 text-slate-500 dark:text-slate-400">{eq.equipment_type}</td>
                      <td className="px-6 py-3 font-mono">{eq.flowrate}</td>
                      <td className="px-6 py-3 font-mono">{eq.pressure}</td>
                      <td className="px-6 py-3 font-mono">{eq.temperature}</td>
                      <td className="px-6 py-3">
                        {eq.is_pressure_outlier || eq.is_temperature_outlier
                          ? <span className="text-red-500 font-bold text-xs bg-red-50 dark:bg-red-900/20 px-2 py-1 rounded">⚠️ ALERT</span>
                          : <span className="text-green-500 font-bold text-xs bg-green-50 dark:bg-green-900/20 px-2 py-1 rounded">OK</span>}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          /* VIEWS 1-3: SPLIT SCREEN (Chart + Insight) */
          <div className="grid grid-cols-3 gap-6 h-full min-h-[500px]">

            {/* LEFT: CHART AREA (2/3 Width) */}
            <div className="col-span-2 bg-white dark:bg-darkcard rounded-xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm flex flex-col">
              <h2 className="text-lg font-bold mb-4">
                {activeView === 'safety' && 'Process Envelope Analysis'}
                {activeView === 'distribution' && 'Equipment Flowrate Ranges'}
                {activeView === 'correlation' && 'Multi-Variable Correlation'}
              </h2>
              <div className="flex-1 relative">
                {activeView === 'safety' && safetyData && <Scatter data={safetyData} options={commonOptions} />}
                {activeView === 'distribution' && distributionData && <Bar data={distributionData} options={{ ...commonOptions, indexAxis: 'y' }} />}
                {activeView === 'correlation' && correlationData && <Bubble data={correlationData} options={commonOptions} />}
              </div>
            </div>

            {/* RIGHT: INSIGHT PANEL (1/3 Width) */}
            <div className="bg-white dark:bg-darkcard rounded-xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm overflow-y-auto">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">Live Insights</h3>

              {activeView === 'safety' && (
                <div className="space-y-3">
                  {analytics.outlier_equipment.length === 0 ? (
                    <div className="p-4 bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400 rounded-lg font-bold text-center">✅ All Systems Nominal</div>
                  ) : (
                    analytics.outlier_equipment.map((eq, i) => (
                      <div key={i} className="p-3 bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 rounded text-sm">
                        <div className="font-bold text-red-900 dark:text-red-200">{eq.name}</div>
                        <div className="text-red-600 dark:text-red-400 text-xs">Parameter Excursion Detected</div>
                      </div>
                    ))
                  )}
                </div>
              )}

              {activeView === 'distribution' && (
                <div className="space-y-4">
                  <div className="h-48"><Pie data={{
                    labels: Object.keys(analytics.equipment_type_distribution),
                    datasets: [{ data: Object.values(analytics.equipment_type_distribution), backgroundColor: ['#6366F1', '#3B82F6', '#10B981', '#F59E0B'] }]
                  }} options={{ maintainAspectRatio: false, plugins: { legend: { display: false } } }} /></div>
                  <div className="text-sm space-y-2">
                    {Object.entries(analytics.equipment_type_distribution).map(([k, v]) => (
                      <div key={k} className="flex justify-between border-b border-slate-100 dark:border-slate-700 pb-1">
                        <span className="font-bold">{k}</span><span className="text-slate-500">{v} Units</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeView === 'correlation' && analytics.correlation_matrix && (
                <div className="space-y-1">
                  {analytics.correlation_matrix.map(row => (
                    <div key={row.variable} className="text-xs">
                      <div className="font-bold uppercase mb-1">{row.variable} vs:</div>
                      <div className="grid grid-cols-3 gap-1 mb-3">
                        {['flowrate', 'pressure', 'temperature'].map(m => (
                          <div key={m} className={`p-2 rounded text-center font-mono ${Math.abs(row[m]) > 0.7 ? 'bg-indigo-100 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-300 font-bold' : 'bg-slate-50 dark:bg-slate-800'}`}>
                            {row[m]}
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}