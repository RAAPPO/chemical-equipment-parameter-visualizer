import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext'; // ADDED IMPORT
import { datasetAPI } from '../services/api';
import { useDatasets } from '../hooks/useDatasets';
import UploadModal from '../components/UploadModal';
import { DatasetListSkeleton } from '../components/LoadingSkeleton';
import DatasetCard from '../components/DatasetCard';

export default function Dashboard() {
  const { user, logout } = useAuth();
  const { isDark, toggleTheme } = useTheme(); // ADDED THEME HOOK
  const navigate = useNavigate();
  const [uploadModalOpen, setUploadModalOpen] = useState(false);

  // Use custom hook for data management
  const { datasets, loading, error, refetch } = useDatasets();

  // Memoized PDF download handler
  const handleDownloadPDF = useCallback(async (datasetId, filename) => {
    try {
      const response = await datasetAPI.downloadPDF(datasetId);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `report_${filename.replace('.csv', '')}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      alert('Failed to download PDF. Please try again.');
    }
  }, []);

  // Memoized logout handler
  const handleLogout = useCallback(() => {
    logout();
    navigate('/login');
  }, [logout, navigate]);

  return (
    <div className={`min-h-screen ${isDark ? 'bg-gray-900' : 'bg-gray-100'} transition-colors duration-300`}>
      {/* Updated Industry-Grade Slim Header */}
      <header className="bg-primary text-white py-4 px-6 shadow-md mb-8" role="banner">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <h1 className="text-xl font-bold">Chemical Equipment Parameter Visualizer</h1>

          {/* WELCOME TEXT + THEME TOGGLE + LOGOUT IN ONE LINE */}
          <div className="flex items-center gap-6">
            <span className="text-sm font-medium">
              Welcome, <strong>{user?.username || 'User'}</strong>
            </span>

            <div className="flex items-center gap-3">
              <button
                onClick={toggleTheme}
                className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-white text-sm font-semibold transition"
              >
                {isDark ? '☀️ Light' : '🌙 Dark'}
              </button>
              <button
                onClick={handleLogout}
                className="bg-red-600 px-4 py-2 rounded-lg hover:bg-red-700 transition font-semibold text-sm"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-4" role="main">
        <div className="flex justify-between items-center mb-8">
          <h2 className={`text-3xl font-bold ${isDark ? 'text-white' : 'text-gray-800'}`}>Datasets</h2>
          <button
            onClick={() => setUploadModalOpen(true)}
            className="bg-primary text-white px-6 py-2.5 rounded-lg hover:bg-blue-800 transition shadow-md font-semibold"
            aria-label="Upload new CSV dataset"
          >
            Upload CSV
          </button>
        </div>

        {/* Loading State */}
        {loading && <DatasetListSkeleton isDark={isDark} />}

        {/* Error State */}
        {error && (
          <div
            className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg mb-4 shadow-sm"
            role="alert"
          >
            <strong>Error:</strong> {error}
            <button onClick={refetch} className="ml-4 underline">Retry</button>
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && datasets.length === 0 && (
          <div
            className={`${isDark ? 'bg-gray-800 border-gray-700 text-white' : 'bg-white border-gray-200 text-gray-900'} border rounded-lg shadow p-12 text-center`}
            role="status"
            aria-live="polite"
          >
            <svg
              className={`mx-auto h-12 w-12 ${isDark ? 'text-gray-500' : 'text-gray-400'}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 className="mt-2 text-lg font-medium">No datasets</h3>
            <p className={isDark ? 'text-gray-400' : 'text-gray-500'}>Get started by uploading a CSV file.</p>
            <button
              onClick={() => setUploadModalOpen(true)}
              className="mt-6 bg-primary text-white px-6 py-2 rounded-lg hover:bg-blue-800 transition font-semibold"
              aria-label="Upload your first dataset"
            >
              Upload First Dataset
            </button>
          </div>
        )}

        {/* Datasets Grid - Removed extra wrapping div to remove the redundant box */}
        {!loading && !error && datasets.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {datasets.map((dataset) => (
              <DatasetCard
                key={dataset.id}
                dataset={dataset}
                isDark={isDark}
                onViewDetails={(id) => navigate(`/dataset/${id}`)}
                onDownloadPDF={handleDownloadPDF}
              />
            ))}
          </div>
        )}
      </main>

      {/* Upload Modal */}
      <UploadModal
        isOpen={uploadModalOpen}
        onClose={() => setUploadModalOpen(false)}
        isDark={isDark}
        onSuccess={() => {
          refetch();
          setUploadModalOpen(false);
        }}
      />
    </div>
  );
}