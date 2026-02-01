import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { datasetAPI } from '../services/api';

export default function Dashboard() {
  const { user, logout } = useAuth();
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDatasets();
  }, []);

  const loadDatasets = async () => {
    try {
      const response = await datasetAPI.getAll();
      setDatasets(response.data);
    } catch (error) {
      console.error('Failed to load datasets:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-primary text-white shadow-lg">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold">Chemical Equipment Visualizer</h1>
          <div className="flex items-center gap-4">
            <span>Welcome, {user?.username}</span>
            <button
              onClick={logout}
              className="bg-red-600 px-4 py-2 rounded hover:bg-red-700"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <h2 className="text-2xl font-bold mb-6">Datasets</h2>

        {loading ? (
          <p>Loading...</p>
        ) : datasets.length === 0 ? (
          <p className="text-gray-600">No datasets found. Upload a CSV to get started.</p>
        ) : (
          <div className="grid gap-4">
            {datasets.map((dataset) => (
              <div key={dataset.id} className="bg-white p-6 rounded-lg shadow">
                <h3 className="font-bold text-lg">{dataset.filename}</h3>
                <p className="text-gray-600">
                  {dataset.total_equipment} equipment • 
                  Uploaded: {new Date(dataset.uploaded_at).toLocaleDateString()}
                </p>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
