import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { datasetAPI, equipmentAPI } from '../services/api';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title } from 'chart.js';
import { Pie, Bar } from 'react-chartjs-2';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title);

export default function DatasetDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [dataset, setDataset] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [equipment, setEquipment] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDatasetDetails();
  }, [id]);

  const loadDatasetDetails = async () => {
    try {
      const [datasetRes, analyticsRes, equipmentRes] = await Promise.all([
        datasetAPI.getById(id),
        datasetAPI.getAnalytics(id),
        equipmentAPI.getAll(id),
      ]);

      setDataset(datasetRes.data);
      setAnalytics(analyticsRes.data);
      setEquipment(equipmentRes.data);
    } catch (error) {
      console.error('Failed to load dataset details:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPDF = async () => {
    try {
      const response = await datasetAPI.downloadPDF(id);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `report_${dataset.filename.replace('.csv', '')}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Failed to download PDF:', error);
      alert('Failed to download PDF');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  // Prepare chart data
  const pieData = {
    labels: Object.keys(analytics?.equipment_type_distribution || {}),
    datasets: [
      {
        data: Object.values(analytics?.equipment_type_distribution || {}),
        backgroundColor: [
          '#1E3A8A', '#3B82F6', '#60A5FA', '#93C5FD', '#DBEAFE',
          '#F97316', '#FB923C', '#FDBA74'
        ],
      },
    ],
  };

  const barData = {
    labels: ['Flowrate', 'Pressure', 'Temperature'],
    datasets: [
      {
        label: 'Average Values',
        data: [
          analytics?.avg_flowrate || 0,
          analytics?.avg_pressure || 0,
          analytics?.avg_temperature || 0,
        ],
        backgroundColor: ['#1E3A8A', '#3B82F6', '#60A5FA'],
      },
    ],
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-primary text-white shadow-lg">
        <div className="container mx-auto px-4 py-4 flex items-center gap-4">
          <button
            onClick={() => navigate('/dashboard')}
            className="hover:bg-blue-800 p-2 rounded"
          >
            ← Back
          </button>
          <h1 className="text-2xl font-bold">Dataset Analysis</h1>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* Dataset Info Card */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex justify-between items-start">
            <div>
              <h2 className="text-2xl font-bold text-gray-800">{dataset?.filename}</h2>
              <p className="text-gray-600 mt-1">
                Uploaded: {new Date(dataset?.uploaded_at).toLocaleString('en-GB')}
              </p>
            </div>
            <button
              onClick={handleDownloadPDF}
              className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M13 8V2H7v6H2l8 8 8-8h-5zM0 18h20v2H0v-2z"/>
              </svg>
              Download PDF
            </button>
          </div>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm text-gray-600">Total Equipment</p>
            <p className="text-3xl font-bold text-primary">{analytics?.total_equipment}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm text-gray-600">Avg Flowrate</p>
            <p className="text-3xl font-bold text-blue-600">{analytics?.avg_flowrate?.toFixed(2)}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm text-gray-600">Avg Pressure</p>
            <p className="text-3xl font-bold text-blue-600">{analytics?.avg_pressure?.toFixed(2)}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm text-gray-600">Avg Temperature</p>
            <p className="text-3xl font-bold text-blue-600">{analytics?.avg_temperature?.toFixed(2)}</p>
          </div>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-bold mb-4">Equipment Type Distribution</h3>
            <Pie data={pieData} />
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-bold mb-4">Average Parameters</h3>
            <Bar data={barData} options={{ responsive: true }} />
          </div>
        </div>

        {/* Outliers */}
        {analytics?.outliers_count > 0 && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-6">
            <h3 className="text-lg font-bold text-red-800 mb-4">
              ⚠️ Outliers Detected ({analytics.outliers_count})
            </h3>
            <div className="space-y-2">
              {analytics.outlier_equipment.map((eq, idx) => (
                <div key={idx} className="bg-white p-3 rounded border border-red-300">
                  <p className="font-semibold">{eq.name} ({eq.type})</p>
                  <p className="text-sm text-gray-600">
                    {eq.pressure_outlier && '🔴 Pressure Outlier '}
                    {eq.temperature_outlier && '🔴 Temperature Outlier'}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Equipment Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <h3 className="text-lg font-bold p-6 border-b">Equipment List</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Flowrate</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Pressure</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Temperature</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {equipment.map((eq) => (
                  <tr key={eq.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{eq.equipment_name}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{eq.equipment_type}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{eq.flowrate.toFixed(1)}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{eq.pressure.toFixed(1)}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{eq.temperature.toFixed(1)}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {eq.is_pressure_outlier || eq.is_temperature_outlier ? (
                        <span className="px-2 py-1 bg-red-100 text-red-800 rounded-full text-xs">Outlier</span>
                      ) : (
                        <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">Normal</span>
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
