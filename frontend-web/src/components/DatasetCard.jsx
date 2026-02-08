/**
 * Dataset Card Component
 * Memoized to prevent unnecessary re-renders
 */
import { memo } from 'react';
import PropTypes from 'prop-types';

const DatasetCard = memo(({ dataset, onViewDetails, onDownloadPDF }) => {
  return (
    <div className="bg-white rounded-lg shadow hover:shadow-lg transition p-6">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h3 className="font-bold text-lg text-gray-900 mb-2">
            {dataset.filename}
          </h3>
          <div className="space-y-1 text-sm text-gray-600">
            <p>
              <span className="font-semibold">Equipment:</span>{' '}
              {dataset.total_equipment || dataset.equipment_count}
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
        <button
          onClick={() => onViewDetails(dataset.id)}
          className="flex-1 bg-blue-100 text-primary px-3 py-2 rounded text-sm font-medium hover:bg-blue-200 transition"
          aria-label={`View details for ${dataset.filename}`}
        >
          View Details
        </button>
        <button
          onClick={() => onDownloadPDF(dataset.id, dataset.filename)}
          className="flex-1 bg-green-100 text-green-700 px-3 py-2 rounded text-sm font-medium hover:bg-green-200 transition"
          aria-label={`Download PDF report for ${dataset.filename}`}
        >
          Download PDF
        </button>
      </div>
    </div>
  );
});

DatasetCard.displayName = 'DatasetCard';

DatasetCard.propTypes = {
  dataset: PropTypes.shape({
    id: PropTypes.string.isRequired,
    filename: PropTypes.string.isRequired,
    uploaded_at: PropTypes.string.isRequired,
    total_equipment: PropTypes.number,
    equipment_count: PropTypes.number,
  }).isRequired,
  onViewDetails: PropTypes.func.isRequired,
  onDownloadPDF: PropTypes.func.isRequired,
};

export default DatasetCard;
