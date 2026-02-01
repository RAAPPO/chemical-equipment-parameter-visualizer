import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { datasetAPI } from '../services/api';
import { useNavigate } from 'react-router-dom';
import UploadModal from '../components/UploadModal';

export default function Dashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [uploadModalOpen, setUploadModalOpen] = useState(false);

  useEffect(() => {
    loadDatasets();
  }, []);

  const loadDatasets = async () => {
    setLoading(true);
    setError(null);
    try {
      console.log('Fetching datasets...');
      const response = await datasetAPI.getAll();
      console.log('Datasets loaded:', response.data);
      setDatasets(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to load datasets:', error);
      setError(error.response?.data?.detail || error.message || 'Failed to load datasets');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-primary text-white shadow-lg">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold">Chemical Equipment Visualizer</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm">Welcome, <strong>{user?.username}</strong></span>
            <button
              onClick={handleLogout}
              className="bg-red-600 px-4 py-2 rounded hover:bg-red-700 transition"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-3xl font-bold text-gray-800">Datasets</h2>
          <button onClick={() => setUploadModalOpen(true)} className="bg-primary text-white px-6 py-2 rounded hover:bg-blue-800 transition">
            Upload CSV
          </button>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
            <p className="mt-4 text-gray-600">Loading datasets...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            <strong>Error:</strong> {error}
            <button onClick={loadDatasets} className="ml-4 underline">Retry</button>
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && datasets.length === 0 && (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 className="mt-2 text-lg font-medium text-gray-900">No datasets</h3>
            <p className="mt-1 text-gray-500">Get started by uploading a CSV file.</p>
            <button className="mt-6 bg-primary text-white px-6 py-2 rounded hover:bg-blue-800 transition">
              Upload First Dataset
            </button>
          </div>
        )}

        {/* Datasets Grid */}
        {!loading && !error && datasets.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {datasets.map((dataset) => (
              <div key={dataset.id} className="bg-white rounded-lg shadow hover:shadow-lg transition p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="font-bold text-lg text-gray-900 mb-2">
                      {dataset.filename}
                    </h3>
                    <div className="space-y-1 text-sm text-gray-600">
                      <p>
                        <span className="font-semibold">Equipment:</span> {dataset.total_equipment || dataset.equipment_count}
                      </p>
                      <p>
                        <span className="font-semibold">Uploaded:</span>{' '}
                        {new Date(dataset.uploaded_at).toLocaleDateString('en-GB', {
                          day: '2-digit',
                          month: 'short',
                          year: 'numeric',
                        })}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="mt-4 pt-4 border-t border-gray-200 flex gap-2">
                  <button onClick={() => navigate(`/dataset/${dataset.id}`)} className="flex-1 bg-blue-100 text-primary px-3 py-2 rounded text-sm font-medium hover:bg-blue-200 transition">
                    View Details
                  </button>
                  <button className="flex-1 bg-green-100 text-green-700 px-3 py-2 rounded text-sm font-medium hover:bg-green-200 transition">
                    Download PDF
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Debug Info (remove in production) */}
        <div className="mt-8 p-4 bg-gray-800 text-white rounded text-xs font-mono">
          <p><strong>Debug Info:</strong></p>
          <p>Loading: {loading.toString()}</p>
          <p>Error: {error || 'None'}</p>
          <p>Datasets count: {datasets.length}</p>
          <p>User: {user?.username}</p>
        </div>
      </main>
      
      {/* Upload Modal */}
      <UploadModal
        isOpen={uploadModalOpen}
        onClose={() => setUploadModalOpen(false)}
        onSuccess={(newDataset) => {
          loadDatasets();
          setUploadModalOpen(false);
        }}
      />
    </div>
  );
}