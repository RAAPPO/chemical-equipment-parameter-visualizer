/**
 * Loading Skeleton Components
 * Professional loading states instead of basic spinners
 */

export const DatasetCardSkeleton = () => (
  <div className="bg-white rounded-lg shadow p-6 animate-pulse">
    <div className="h-6 bg-gray-200 rounded w-3/4 mb-3"></div>
    <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
    <div className="flex gap-2">
      <div className="h-10 bg-gray-200 rounded flex-1"></div>
      <div className="h-10 bg-gray-200 rounded flex-1"></div>
    </div>
  </div>
);

export const DatasetListSkeleton = () => (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    {[1, 2, 3].map((i) => (
      <DatasetCardSkeleton key={i} />
    ))}
  </div>
);

export const ChartSkeleton = () => (
  <div className="bg-white rounded-lg shadow p-6 animate-pulse">
    <div className="h-6 bg-gray-200 rounded w-1/2 mb-4"></div>
    <div className="h-64 bg-gray-200 rounded"></div>
  </div>
);

export const TableSkeleton = () => (
  <div className="bg-white rounded-lg shadow overflow-hidden animate-pulse">
    <div className="h-12 bg-gray-200"></div>
    {[1, 2, 3, 4, 5].map((i) => (
      <div key={i} className="h-16 bg-gray-100 border-t border-gray-200"></div>
    ))}
  </div>
);

export const Spinner = ({ size = 'md' }) => {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
  };

  return (
    <div className="flex justify-center items-center">
      <div
        className={`${sizeClasses[size]} animate-spin rounded-full border-b-2 border-primary`}
      ></div>
    </div>
  );
};
