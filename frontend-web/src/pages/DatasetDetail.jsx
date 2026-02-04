import { useState, useEffect, useMemo, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { datasetAPI, equipmentAPI } from '../services/api';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  PointElement,
  LineElement
} from 'chart.js';
import { Pie, Scatter, Bar, Bubble } from 'react-chartjs-2';

// Register all necessary components for the new charts
ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  PointElement,
  LineElement
);

export default function DatasetDetail() {
  const { id } = useParams();
  const navigate = useNavigate();

  // Data State
  const [dataset, setDataset] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [equipment, setEquipment] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // View State (The Core of the Dynamic Dashboard)
  const [activeView, setActiveView] = useState('safety'); // 'safety' | 'distribution' | 'correlation'

  useEffect(() => {
    loadDatasetDetails();
  }, [id]);

  const loadDatasetDetails = async () => {
    setLoading(true);
    setError(null);
    try {
      const [datasetRes, analyticsRes, equipmentRes] = await Promise.all([
        datasetAPI.getById(id),
        datasetAPI.getAnalytics(id),
        equipmentAPI.getAll(id),
      ]);

      setDataset(datasetRes.data);
      setAnalytics(analyticsRes.data);
      setEquipment(equipmentRes.data.results || equipmentRes.data || []);
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to load dataset');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPDF = useCallback(async () => {
    try {
      const response = await datasetAPI.downloadPDF(id);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `report_${dataset.filename.replace('.csv', '')}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      alert('Failed to download PDF');
    }
  }, [id, dataset]);

  // --- CHART DATA GENERATORS ---

  // 1. SAFETY VIEW: Scatter Plot highlighting Outliers
  const safetyChartData = useMemo(() => {
    if (!analytics) return null;
    return {
      datasets: [
        {
          label: 'Safe Operation',
          data: analytics.scatter_data.filter(d => !analytics.outlier_equipment.some(o => o.name === d.name)),
          backgroundColor: '#10B981', // Emerald 500
          pointRadius: 6,
        },
        {
          label: 'Critical Outliers',
          data: analytics.scatter_data.filter(d => analytics.outlier_equipment.some(o => o.name === d.name)),
          backgroundColor: '#EF4444', // Red 500
          pointRadius: 8,
          pointStyle: 'triangle',
        }
      ]
    };
  }, [analytics]);

  // 2. DISTRIBUTION VIEW: Floating Bars (Range) + Average Line
  const distributionChartData = useMemo(() => {
    if (!equipment.length) return null;

    // Calculate Min, Max, and Avg Flowrate per Type
    const statsByType = equipment.reduce((acc, eq) => {
      if (!acc[eq.equipment_type]) {
        acc[eq.equipment_type] = { min: eq.flowrate, max: eq.flowrate, sum: eq.flowrate, count: 1 };
      } else {
        acc[eq.equipment_type].min = Math.min(acc[eq.equipment_type].min, eq.flowrate);
        acc[eq.equipment_type].max = Math.max(acc[eq.equipment_type].max, eq.flowrate);
        acc[eq.equipment_type].sum += eq.flowrate;
        acc[eq.equipment_type].count += 1;
      }
      return acc;
    }, {});

    const labels = Object.keys(statsByType);

    return {
      labels,
      datasets: [
        {
          label: 'Operating Range (Min-Max Flow)',
          data: labels.map(l => [statsByType[l].min, statsByType[l].max]),
          backgroundColor: 'rgba(59, 130, 246, 0.5)', // Blue with opacity
          borderColor: '#2563EB',
          borderWidth: 1,
          borderSkipped: false, // Make it a floating bar
        }
      ]
    };
  }, [equipment]);

  // 3. CORRELATION VIEW: Bubble Chart
  const correlationChartData = useMemo(() => {
    if (!analytics) return null;
    return {
      datasets: [{
        label: 'Multi-Variable Analysis (Size = Flow)',
        data: analytics.scatter_data, // Backend now provides {x, y, r}
        backgroundColor: 'rgba(99, 102, 241, 0.6)', // Indigo
        borderColor: '#4F46E5',
        borderWidth: 1,
      }]
    };
  }, [analytics]);

  if (loading) return <div className="min-h-screen flex items-center justify-center"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div></div>;
  if (error) return <div className="p-8 text-center text-red-600 font-bold">{error}</div>;

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-900">

      {/* --- HEADER --- */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <button onClick={() => navigate('/dashboard')} className="text-slate-500 hover:text-blue-600 transition-colors">← Back</button>
            <div>
              <h1 className="text-xl font-bold text-slate-800">{dataset?.filename}</h1>
              <p className="text-sm text-slate-500">Uploaded {new Date(dataset?.uploaded_at).toLocaleDateString()}</p>
            </div>
          </div>
          <button onClick={handleDownloadPDF} className="bg-slate-900 hover:bg-slate-800 text-white px-5 py-2.5 rounded-lg text-sm font-medium transition-colors shadow-sm flex items-center gap-2">
            <span>📄</span> Generate PDF Report
          </button>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8">

        {/* --- KPI CARDS (Always Visible) --- */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          {[
            { label: 'Total Units', val: analytics?.total_equipment, unit: '', color: 'text-indigo-600' },
            { label: 'Avg Flowrate', val: analytics?.avg_flowrate, unit: 'm³/h', color: 'text-blue-600' },
            { label: 'Avg Pressure', val: analytics?.avg_pressure, unit: 'bar', color: 'text-emerald-600' },
            { label: 'Avg Temp', val: analytics?.avg_temperature, unit: '°C', color: 'text-orange-600' },
          ].map((kpi, i) => (
            <div key={i} className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
              <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">{kpi.label}</p>
              <p className={`text-3xl font-black ${kpi.color}`}>{kpi.val} <span className="text-base text-slate-400 font-normal">{kpi.unit}</span></p>
            </div>
          ))}
        </div>

        {/* --- DYNAMIC DASHBOARD CONTROLS --- */}
        <div className="mb-6 flex justify-center">
          <div className="bg-white p-1.5 rounded-full border border-slate-200 shadow-sm inline-flex">
            {[
              { id: 'safety', icon: '🛡️', label: 'Process Safety' },
              { id: 'distribution', icon: '📊', label: 'Distributions' },
              { id: 'correlation', icon: '🔗', label: 'Correlations' },
            ].map((view) => (
              <button
                key={view.id}
                onClick={() => setActiveView(view.id)}
                className={`px-6 py-2 rounded-full text-sm font-bold transition-all ${activeView === view.id
                    ? 'bg-slate-900 text-white shadow-md'
                    : 'text-slate-500 hover:bg-slate-50'
                  }`}
              >
                <span className="mr-2">{view.icon}</span>{view.label}
              </button>
            ))}
          </div>
        </div>

        {/* --- DYNAMIC CONTENT STAGE --- */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-10">

          {/* Main Visualization (Takes up 2/3 space) */}
          <div className="lg:col-span-2 bg-white p-8 rounded-2xl border border-slate-200 shadow-sm h-[500px] flex flex-col">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-lg font-bold text-slate-800">
                {activeView === 'safety' && 'Process Envelope (Pressure vs Temperature)'}
                {activeView === 'distribution' && 'Flowrate Variability by Equipment Type'}
                {activeView === 'correlation' && 'Multi-Variable Interaction (P-T-Flow)'}
              </h2>
            </div>

            <div className="flex-1 relative w-full h-full">
              {activeView === 'safety' && safetyChartData && (
                <Scatter
                  data={safetyChartData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                      x: { title: { display: true, text: 'Pressure (bar)' } },
                      y: { title: { display: true, text: 'Temperature (°C)' } }
                    }
                  }}
                />
              )}
              {activeView === 'distribution' && distributionChartData && (
                <Bar
                  data={distributionChartData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: { y: { title: { display: true, text: 'Flowrate (m³/h)' }, beginAtZero: false } }
                  }}
                />
              )}
              {activeView === 'correlation' && correlationChartData && (
                <Bubble
                  data={correlationChartData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                      x: { title: { display: true, text: 'Pressure (bar)' } },
                      y: { title: { display: true, text: 'Temperature (°C)' } }
                    }
                  }}
                />
              )}
            </div>
          </div>

          {/* Side Panel (Contextual Insights) */}
          <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm flex flex-col h-[500px] overflow-y-auto">

            {/* SAFETY SIDEBAR */}
            {activeView === 'safety' && (
              <>
                <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-6">Safety Alerts</h3>
                {analytics.outliers_count > 0 ? (
                  <div className="space-y-3">
                    {analytics.outlier_equipment.map((eq, i) => (
                      <div key={i} className="p-4 bg-red-50 border border-red-100 rounded-lg">
                        <div className="flex justify-between items-center mb-1">
                          <span className="font-bold text-red-900">{eq.name}</span>
                          <span className="text-xs font-bold bg-red-200 text-red-800 px-2 py-1 rounded">{eq.type}</span>
                        </div>
                        <p className="text-xs text-red-700">
                          {eq.pressure_outlier && 'High Pressure Risk. '}
                          {eq.temperature_outlier && 'Temperature Excursion.'}
                        </p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-10 text-emerald-600 bg-emerald-50 rounded-lg border border-emerald-100">
                    <div className="text-4xl mb-2">✅</div>
                    <p className="font-bold">No Critical Alerts</p>
                    <p className="text-sm">All units operating within normal bounds.</p>
                  </div>
                )}
              </>
            )}

            {/* DISTRIBUTION SIDEBAR */}
            {activeView === 'distribution' && (
              <>
                <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-6">Equipment Breakdown</h3>
                <div className="relative h-64 mb-6">
                  <Pie
                    data={{
                      labels: Object.keys(analytics.equipment_type_distribution),
                      datasets: [{
                        data: Object.values(analytics.equipment_type_distribution),
                        backgroundColor: ['#6366F1', '#3B82F6', '#10B981', '#F59E0B', '#EF4444']
                      }]
                    }}
                    options={{ responsive: true, maintainAspectRatio: false }}
                  />
                </div>
                <div className="text-sm text-slate-600 space-y-2">
                  <p><strong>Dominant Type:</strong> {Object.keys(analytics.equipment_type_distribution)[0]}</p>
                  <p><strong>Variety:</strong> {Object.keys(analytics.equipment_type_distribution).length} Categories</p>
                </div>
              </>
            )}

            {/* CORRELATION SIDEBAR (Matrix) */}
            {activeView === 'correlation' && analytics.correlation_matrix && (
              <>
                <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-6">Correlation Matrix</h3>
                <div className="flex flex-col gap-1">
                  {/* Header Row */}
                  <div className="grid grid-cols-4 gap-1 text-xs font-bold text-slate-500 mb-2">
                    <div></div><div>Flow</div><div>Pres</div><div>Temp</div>
                  </div>
                  {/* Rows */}
                  {analytics.correlation_matrix.map((row) => (
                    <div key={row.variable} className="grid grid-cols-4 gap-1 text-xs">
                      <div className="font-bold capitalize self-center">{row.variable}</div>
                      {[row.flowrate, row.pressure, row.temperature].map((val, idx) => {
                        const intensity = Math.abs(val);
                        const bg = val > 0 ? `rgba(16, 185, 129, ${intensity})` : `rgba(239, 68, 68, ${intensity})`;
                        return (
                          <div key={idx} className="h-8 rounded flex items-center justify-center font-medium" style={{ backgroundColor: bg }}>
                            {val}
                          </div>
                        )
                      })}
                    </div>
                  ))}
                </div>
                <p className="text-xs text-slate-400 mt-4 italic">
                  *Values close to 1.0 indicate strong positive correlation.
                </p>
              </>
            )}
          </div>
        </div>

        {/* --- DATA TABLE --- */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="px-8 py-6 border-b border-slate-100">
            <h3 className="text-lg font-bold text-slate-800">Raw Equipment Data</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead className="bg-slate-50">
                <tr>
                  {['Name', 'Type', 'Flowrate', 'Pressure', 'Temperature', 'Status'].map(h => (
                    <th key={h} className="px-8 py-4 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {equipment.map((eq) => (
                  <tr key={eq.id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-8 py-4 font-medium text-slate-900">{eq.equipment_name}</td>
                    <td className="px-8 py-4 text-slate-500">{eq.equipment_type}</td>
                    <td className="px-8 py-4 text-slate-500">{eq.flowrate.toFixed(1)}</td>
                    <td className="px-8 py-4 text-slate-500">{eq.pressure.toFixed(1)}</td>
                    <td className="px-8 py-4 text-slate-500">{eq.temperature.toFixed(1)}</td>
                    <td className="px-8 py-4">
                      {eq.is_pressure_outlier || eq.is_temperature_outlier ? (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                          ⚠️ Check
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">
                          Normal
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
}