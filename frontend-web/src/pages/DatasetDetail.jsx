import { useState, useEffect, useMemo, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTheme } from '../context/ThemeContext';
import { datasetAPI, equipmentAPI } from '../services/api';
import EditEquipmentModal from '../components/EditEquipmentModal';
import AdvancedCharts from '../components/AdvancedCharts';
import { exportEquipmentAsExcel } from '../utils/chartExport';
import {
  Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale,
  LinearScale, BarElement, Title, PointElement, LineElement
} from 'chart.js';
import { Pie, Scatter, Bar, Bubble } from 'react-chartjs-2';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title, PointElement, LineElement);

export default function DatasetDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isDark, toggleTheme } = useTheme();

  // Data State
  const [dataset, setDataset] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [equipment, setEquipment] = useState([]);
  const [loading, setLoading] = useState(true);

  // UX State
  const [activeView, setActiveView] = useState('safety');
  const [typeFilter, setTypeFilter] = useState('All');

  // Modal State
  const [editingEquipment, setEditingEquipment] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);

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
    } catch (err) {
      console.error(err);
      alert("Failed to load data");
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
      link.setAttribute('download', `${dataset?.filename || 'report'}.pdf`);
      document.body.appendChild(link); link.click(); link.remove();
    } catch (e) { alert('Download failed'); }
  }, [id, dataset]);

  const handleEditEquipment = (item) => {
    setEditingEquipment(item);
    setShowEditModal(true);
  };

  const handleSaveEquipment = async (equipmentId, formData) => {
    try {
      await datasetAPI.updateEquipment(equipmentId, formData);
      await loadData();
      alert('Equipment updated successfully!');
    } catch (error) {
      console.error('Failed to update equipment:', error);
      throw error;
    }
  };

  const handleDeleteEquipment = async (equipmentId) => {
    if (!window.confirm('Are you sure you want to delete this equipment?')) return;
    try {
      await datasetAPI.deleteEquipment(equipmentId);
      await loadData();
      alert('Equipment deleted successfully!');
    } catch (error) {
      console.error('Failed to delete equipment:', error);
      alert('Failed to delete equipment');
    }
  };

  const filteredEquipment = useMemo(() => {
    if (typeFilter === 'All') return equipment;
    return equipment.filter(e => e.equipment_type === typeFilter);
  }, [equipment, typeFilter]);

  const dynamicStats = useMemo(() => {
    if (!filteredEquipment.length) return { flow: 0, press: 0, temp: 0 };
    const total = filteredEquipment.reduce((acc, curr) => ({
      flow: acc.flow + curr.flowrate,
      press: acc.press + curr.pressure,
      temp: acc.temp + curr.temperature
    }), { flow: 0, press: 0, temp: 0 });
    const count = filteredEquipment.length;
    return {
      flow: (total.flow / count).toFixed(2),
      press: (total.press / count).toFixed(2),
      temp: (total.temp / count).toFixed(2)
    };
  }, [filteredEquipment]);

  const filteredAnalytics = useMemo(() => {
    if (!analytics) return null;
    if (typeFilter === 'All') return analytics;
    const filteredScatter = analytics.scatter_data?.filter(d => d.type === typeFilter) || [];
    const filteredOutliers = analytics.outlier_equipment?.filter(o => o.type === typeFilter) || [];
    const filteredDist = { [typeFilter]: analytics.equipment_type_distribution?.[typeFilter] || 0 };
    return {
      ...analytics,
      scatter_data: filteredScatter,
      outlier_equipment: filteredOutliers,
      equipment_type_distribution: filteredDist
    };
  }, [analytics, typeFilter]);

  const uniqueTypes = useMemo(() => {
    if (!equipment.length) return [];
    return ['All', ...new Set(equipment.map(e => e.equipment_type))];
  }, [equipment]);

  const safetyData = useMemo(() => {
    if (!filteredAnalytics?.scatter_data) return null;
    const outliers = new Set(filteredAnalytics.outlier_equipment?.map(o => o.name) || []);
    return {
      datasets: [
        {
          label: 'Safe Operation',
          data: filteredAnalytics.scatter_data.filter(d => !outliers.has(d.name)),
          backgroundColor: '#10B981',
        },
        {
          label: 'Critical Alerts',
          data: filteredAnalytics.scatter_data.filter(d => outliers.has(d.name)),
          backgroundColor: '#EF4444',
          pointRadius: 8,
          pointStyle: 'triangle',
        }
      ]
    };
  }, [filteredAnalytics]);

  const distributionData = useMemo(() => {
    if (!analytics?.peer_benchmarks) return null;
    const keys = Object.keys(analytics.peer_benchmarks).filter(k => typeFilter === 'All' || k === typeFilter);
    return {
      labels: keys,
      datasets: [{
        label: 'Flowrate Range (Min to Max)',
        data: keys.map(t => [analytics.peer_benchmarks[t].flowrate_min, analytics.peer_benchmarks[t].flowrate_max]),
        backgroundColor: '#3B82F6',
        barPercentage: 0.5,
      }]
    };
  }, [analytics, typeFilter]);

  const correlationData = useMemo(() => {
    if (!filteredAnalytics?.scatter_data) return null;
    return {
      datasets: [{
        label: 'P vs T (Size = Flowrate)',
        data: filteredAnalytics.scatter_data.map(d => ({ x: d.x, y: d.y, r: Math.max(3, (d.r || 10) / 15) })),
        backgroundColor: 'rgba(79, 70, 229, 0.6)',
      }]
    };
  }, [filteredAnalytics]);

  const commonOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { position: 'bottom' } }
  };

  if (loading) {
    return (
      <div className={`min-h-screen flex items-center justify-center ${isDark ? 'bg-gray-900' : 'bg-gray-100'}`}>
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!dataset) return null;

  return (
    <div className={`min-h-screen ${isDark ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-900'} transition-colors duration-300`}>

      {/* COMPACT HEADER */}
      <div className="bg-primary text-white py-4 px-6 shadow-md">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-4 flex-wrap">
              <button
                onClick={() => navigate('/dashboard')}
                className="text-white/80 hover:text-white text-sm font-semibold whitespace-nowrap"
              >
                ← Back
              </button>
              <div className="h-6 w-px bg-white/30"></div>
              <h1 className="text-xl font-bold">{dataset.filename}</h1>
              <div className="h-6 w-px bg-white/30"></div>
              <span className="text-white/80 text-sm">
                {new Date(dataset.uploaded_at).toLocaleDateString('en-GB')}
              </span>
              <div className="h-6 w-px bg-white/30"></div>
              <span className="text-white/80 text-sm font-semibold">
                {dataset.total_equipment} Equipment
              </span>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={toggleTheme}
                className="px-3 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-white text-sm font-semibold transition"
              >
                {isDark ? 'Light ☀️' : 'Dark 🌙'}
              </button>
              <button
                onClick={handleDownloadPDF}
                className="bg-green-100 text-green-700 hover:bg-green-200 px-4 py-2 rounded-lg font-semibold text-sm transition whitespace-nowrap"
              >
                📄 Download PDF
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* COMPACT FILTER + TABS ROW */}
      <div className={`${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border-b px-6 py-3`}>
        <div className="max-w-7xl mx-auto flex items-center justify-between gap-6 flex-wrap">
          <div className="flex items-center gap-3">
            <label className="text-sm font-semibold whitespace-nowrap">Filter:</label>
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className={`border ${isDark ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900'} rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary`}
            >
              {uniqueTypes.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
            <span className="text-sm text-gray-500">
              {filteredEquipment.length} shown
            </span>
          </div>

          <div className="flex items-center gap-2 overflow-x-auto">
            {[
              { id: 'safety', label: 'Safety', icon: '🛡️' },
              { id: 'distribution', label: 'Distribution', icon: '📊' },
              { id: 'correlation', label: 'Correlation', icon: '🔗' },
              { id: 'data', label: 'Data', icon: '📋' },
              { id: 'charts', label: 'Charts', icon: '📈' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveView(tab.id)}
                className={`px-4 py-2 rounded-lg font-semibold text-sm transition whitespace-nowrap ${activeView === tab.id
                    ? 'bg-primary text-white'
                    : isDark ? 'text-gray-400 hover:text-white hover:bg-gray-700' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }`}
              >
                {tab.icon} {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* KPI CARDS */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          {[
            { label: 'Active Units', value: filteredEquipment.length, color: 'text-indigo-600' },
            { label: 'Avg Flowrate', value: dynamicStats.flow, unit: 'm³/h', color: 'text-blue-600' },
            { label: 'Avg Pressure', value: dynamicStats.press, unit: 'bar', color: 'text-green-600' },
            { label: 'Avg Temperature', value: dynamicStats.temp, unit: '°C', color: 'text-orange-600' }
          ].map((kpi, i) => (
            <div key={i} className={`${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg shadow p-6`}>
              <p className={`text-sm font-semibold mb-1 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>{kpi.label}</p>
              <p className={`text-3xl font-bold ${kpi.color}`}>
                {kpi.value}
                {kpi.unit && <span className="text-sm text-gray-500 ml-1">{kpi.unit}</span>}
              </p>
            </div>
          ))}
        </div>

        {/* CONTENT AREA */}
        <div className={`${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg shadow p-6`}>
          {activeView === 'charts' && (
            <div>
              <div className="mb-6 flex justify-end">
                <button
                  onClick={() => exportEquipmentAsExcel(equipment, `${dataset.filename}_data.csv`)}
                  className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-semibold transition flex items-center gap-2"
                >
                  📊 Export to Excel
                </button>
              </div>
              <AdvancedCharts
                equipment={equipment}
                analytics={{
                  avg_flowrate: dataset.avg_flowrate,
                  avg_pressure: dataset.avg_pressure,
                  avg_temperature: dataset.avg_temperature,
                  equipment_type_distribution: equipment.reduce((acc, eq) => {
                    acc[eq.equipment_type] = (acc[eq.equipment_type] || 0) + 1;
                    return acc;
                  }, {})
                }}
              />
            </div>
          )}

          {activeView === 'data' && (
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead className={`${isDark ? 'bg-gray-700' : 'bg-gray-50'}`}>
                  <tr>
                    {['Name', 'Type', 'Flow', 'Pressure', 'Temp', 'Status', 'Actions'].map(h => (
                      <th key={h} className={`px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className={`divide-y ${isDark ? 'divide-gray-700' : 'divide-gray-200'}`}>
                  {filteredEquipment.map(eq => (
                    <tr key={eq.id} className={`${isDark ? 'hover:bg-gray-700' : 'hover:bg-gray-50'} transition`}>
                      <td className="px-6 py-4 text-sm font-medium">{eq.equipment_name}</td>
                      <td className={`px-6 py-4 text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>{eq.equipment_type}</td>
                      <td className="px-6 py-4 text-sm font-mono">{eq.flowrate.toFixed(2)}</td>
                      <td className="px-6 py-4 text-sm font-mono">{eq.pressure.toFixed(2)}</td>
                      <td className="px-6 py-4 text-sm font-mono">{eq.temperature.toFixed(2)}</td>
                      <td className="px-6 py-4">
                        {eq.is_pressure_outlier || eq.is_temperature_outlier ? (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-red-100 text-red-800">
                            ⚠️ Alert
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-green-100 text-green-800">
                            OK
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        <button
                          onClick={() => handleEditEquipment(eq)}
                          className="text-blue-600 hover:text-blue-800 mr-3 text-sm font-medium"
                        >
                          ✏️ Edit
                        </button>
                        <button
                          onClick={() => handleDeleteEquipment(eq.id)}
                          className="text-red-600 hover:text-red-800 text-sm font-medium"
                        >
                          🗑️ Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {activeView !== 'data' && activeView !== 'charts' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <h3 className="text-lg font-bold mb-4">
                  {activeView === 'safety' && 'Safety Analysis'}
                  {activeView === 'distribution' && 'Equipment Distribution'}
                  {activeView === 'correlation' && 'Correlation Analysis'}
                </h3>
                <div style={{ height: '400px' }}>
                  {activeView === 'safety' && safetyData && <Scatter data={safetyData} options={commonOptions} />}
                  {activeView === 'distribution' && distributionData && <Bar data={distributionData} options={{ ...commonOptions, indexAxis: 'y' }} />}
                  {activeView === 'correlation' && correlationData && <Bubble data={correlationData} options={commonOptions} />}
                </div>
              </div>

              <div>
                <h3 className="text-lg font-bold mb-4">Live Insights</h3>
                {activeView === 'safety' && filteredAnalytics && (
                  <div className="space-y-3">
                    {filteredAnalytics.outlier_equipment?.length === 0 ? (
                      <div className="p-4 bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400 rounded-lg font-bold text-center">
                        ✅ All Systems Nominal
                      </div>
                    ) : (
                      filteredAnalytics.outlier_equipment?.map((eq, i) => (
                        <div key={i} className="p-3 bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 rounded text-sm">
                          <div className="font-bold text-red-900 dark:text-red-200">{eq.name}</div>
                          <div className="text-red-600 dark:text-red-400 text-xs">Parameter Excursion Detected</div>
                        </div>
                      ))
                    )}
                  </div>
                )}
                {activeView === 'distribution' && filteredAnalytics && (
                  <div>
                    <div style={{ height: '200px' }} className="mb-4">
                      <Pie
                        data={{
                          labels: Object.keys(filteredAnalytics.equipment_type_distribution || {}),
                          datasets: [{
                            data: Object.values(filteredAnalytics.equipment_type_distribution || {}),
                            backgroundColor: ['#6366F1', '#3B82F6', '#10B981', '#F59E0B']
                          }]
                        }}
                        options={{ maintainAspectRatio: false, plugins: { legend: { display: false } } }}
                      />
                    </div>
                    <div className="text-sm space-y-2">
                      {Object.entries(filteredAnalytics.equipment_type_distribution || {}).map(([k, v]) => (
                        <div key={k} className="flex justify-between border-b border-gray-200 dark:border-gray-700 pb-1">
                          <span className="font-bold">{k}</span>
                          <span className="text-gray-500">{v} Units</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                {activeView === 'correlation' && analytics?.correlation_matrix && (
                  <div className="space-y-2">
                    {analytics.correlation_matrix.map(row => (
                      <div key={row.variable} className="text-xs">
                        <div className="font-bold uppercase mb-1">{row.variable}</div>
                        <div className="grid grid-cols-3 gap-1">
                          {['flowrate', 'pressure', 'temperature'].map(m => (
                            <div
                              key={m}
                              className={`p-2 rounded text-center font-mono ${Math.abs(row[m]) > 0.7
                                ? 'bg-indigo-100 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-300 font-bold'
                                : 'bg-gray-100 dark:bg-gray-800'
                                }`}
                            >
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
        </div>
      </div>

      <EditEquipmentModal
        equipment={editingEquipment}
        isOpen={showEditModal}
        onClose={() => {
          setShowEditModal(false);
          setEditingEquipment(null);
        }}
        onSave={handleSaveEquipment}
      />
    </div>
  );
}