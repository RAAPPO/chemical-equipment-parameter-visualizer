/**
 * Dataset Card Component
 * Memoized to prevent unnecessary re-renders
 */
import { memo } from 'react';
import PropTypes from 'prop-types';

const DatasetCard = memo(({ dataset, isDark, onViewDetails, onDownloadPDF }) => {
  return (
    <div className={`${isDark ? 'bg-gray-800 border-gray-700 text-white' : 'bg-white border-gray-200 text-gray-900'
      } border rounded-lg shadow hover:shadow-lg transition p-6`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h3 className={`font-bold text-lg mb-2 ${isDark ? 'text-white' : 'text-gray-900'}`}>
            {dataset.filename}
          </h3>
          <div className={`space-y-1 text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
            <p>
              <span className="font-semibold text-gray-500 dark:text-gray-300">Equipment:</span>{' '}
              {dataset.total_equipment || dataset.equipment_count}
            </p>
            <p>
              <span className="font-semibold text-gray-500 dark:text-gray-300">Uploaded:</span>{' '}
              {new Date(dataset.uploaded_at).toLocaleDateString('en-GB', {
                day: '2-digit',
                month: 'short',
                year: 'numeric',
              })}
            </p>
          </div>
        </div>
      </div>

      <div className={`mt-4 pt-4 border-t flex gap-2 ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
        <button
          onClick={() => onViewDetails(dataset.id)}
          className={`flex-1 px-3 py-2 rounded text-sm font-bold transition ${isDark
              ? 'bg-blue-900/40 text-blue-400 hover:bg-blue-900/60'
              : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
            }`}
          aria-label={`View details for ${dataset.filename}`}
        >
          View Details
        </button>
        <button
          onClick={() => onDownloadPDF(dataset.id, dataset.filename)}
          className={`flex-1 px-3 py-2 rounded text-sm font-bold transition ${isDark
              ? 'bg-green-900/40 text-green-400 hover:bg-green-900/60'
              : 'bg-green-100 text-green-700 hover:bg-green-200'
            }`}
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
  isDark: PropTypes.bool, // Added propType for theme support
  onViewDetails: PropTypes.func.isRequired,
  onDownloadPDF: PropTypes.func.isRequired,
};

export default DatasetCard;