/**
 * Custom hook for dataset operations
 * Encapsulates data fetching logic and state management
 */
import { useState, useEffect, useCallback } from 'react';
import { datasetAPI, equipmentAPI } from '../services/api';

export const useDatasets = () => {
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDatasets = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await datasetAPI.getAll();
      setDatasets(response.data.results || response.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to load datasets');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDatasets();
  }, [fetchDatasets]);

  return {
    datasets,
    loading,
    error,
    refetch: fetchDatasets,
  };
};

export const useDatasetDetail = (id) => {
  const [dataset, setDataset] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [equipment, setEquipment] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
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
      } catch (err) {
        setError(err.response?.data?.detail || err.message || 'Failed to load dataset');
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchData();
    }
  }, [id]);

  return { dataset, analytics, equipment, loading, error };
};
