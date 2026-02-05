import { useRef } from 'react';
import PropTypes from 'prop-types';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    BarElement,
    ArcElement,
    Title,
    Tooltip,
    Legend,
} from 'chart.js';
import { Bar, Pie, Line, Scatter } from 'react-chartjs-2';
import { exportChartAsPNG } from '../utils/chartExport';

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    BarElement,
    ArcElement,
    Title,
    Tooltip,
    Legend
);

export default function AdvancedCharts({ equipment, analytics }) {
    const barChartRef = useRef();
    const pieChartRef = useRef();
    const scatterChartRef = useRef();
    const lineChartRef = useRef();

    // Prepare data for Equipment Type Distribution (Pie Chart)
    const pieData = {
        labels: Object.keys(analytics.equipment_type_distribution || {}),
        datasets: [{
            label: 'Equipment Count',
            data: Object.values(analytics.equipment_type_distribution || {}),
            backgroundColor: [
                '#3B82F6', // Blue
                '#10B981', // Green
                '#F59E0B', // Yellow
                '#EF4444', // Red
                '#8B5CF6', // Purple
                '#EC4899', // Pink
            ],
            borderWidth: 2,
            borderColor: '#fff'
        }]
    };

    // Prepare data for Parameter Comparison (Bar Chart)
    const barData = {
        labels: ['Flowrate', 'Pressure', 'Temperature'],
        datasets: [{
            label: 'Average Values',
            data: [
                analytics.avg_flowrate || 0,
                analytics.avg_pressure || 0,
                analytics.avg_temperature || 0
            ],
            backgroundColor: ['#3B82F6', '#10B981', '#F59E0B'],
            borderWidth: 1,
            borderColor: ['#2563EB', '#059669', '#D97706']
        }]
    };

    // Prepare data for Pressure vs Temperature (Scatter Plot)
    const scatterData = {
        datasets: [
            {
                label: 'Normal Equipment',
                data: equipment
                    .filter(eq => !eq.is_pressure_outlier && !eq.is_temperature_outlier)
                    .map(eq => ({ x: eq.pressure, y: eq.temperature })),
                backgroundColor: '#3B82F6',
                pointRadius: 5,
                pointHoverRadius: 7
            },
            {
                label: 'Outliers',
                data: equipment
                    .filter(eq => eq.is_pressure_outlier || eq.is_temperature_outlier)
                    .map(eq => ({ x: eq.pressure, y: eq.temperature })),
                backgroundColor: '#EF4444',
                pointRadius: 6,
                pointHoverRadius: 8,
                pointStyle: 'triangle'
            }
        ]
    };

    // Prepare data for Flowrate Trend (Line Chart)
    const lineData = {
        labels: equipment.map((eq, idx) => `#${idx + 1}`),
        datasets: [{
            label: 'Flowrate Trend',
            data: equipment.map(eq => eq.flowrate),
            borderColor: '#3B82F6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            tension: 0.4,
            fill: true,
            pointRadius: 3,
            pointHoverRadius: 5
        }]
    };

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top',
            },
        },
    };

    const scatterOptions = {
        ...options,
        scales: {
            x: {
                title: {
                    display: true,
                    text: 'Pressure (bar)'
                }
            },
            y: {
                title: {
                    display: true,
                    text: 'Temperature (°C)'
                }
            }
        }
    };

    return (
        <div className="space-y-6">
            {/* Equipment Type Distribution */}
            <div className="bg-white rounded-lg shadow p-6">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-bold text-gray-800">Equipment Type Distribution</h3>
                    <button
                        onClick={() => exportChartAsPNG(pieChartRef, 'equipment_distribution.png')}
                        className="px-4 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition"
                    >
                        📥 Download PNG
                    </button>
                </div>
                <div className="h-64">
                    <Pie ref={pieChartRef} data={pieData} options={options} />
                </div>
            </div>

            {/* Parameter Comparison */}
            <div className="bg-white rounded-lg shadow p-6">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-bold text-gray-800">Average Parameters Comparison</h3>
                    <button
                        onClick={() => exportChartAsPNG(barChartRef, 'parameters_comparison.png')}
                        className="px-4 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition"
                    >
                        📥 Download PNG
                    </button>
                </div>
                <div className="h-64">
                    <Bar ref={barChartRef} data={barData} options={options} />
                </div>
            </div>

            {/* Pressure vs Temperature Scatter */}
            <div className="bg-white rounded-lg shadow p-6">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-bold text-gray-800">Pressure-Temperature Correlation</h3>
                    <button
                        onClick={() => exportChartAsPNG(scatterChartRef, 'pressure_temperature_correlation.png')}
                        className="px-4 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition"
                    >
                        📥 Download PNG
                    </button>
                </div>
                <div className="h-80">
                    <Scatter ref={scatterChartRef} data={scatterData} options={scatterOptions} />
                </div>
            </div>

            {/* Flowrate Trend */}
            <div className="bg-white rounded-lg shadow p-6">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-bold text-gray-800">Flowrate Trend Analysis</h3>
                    <button
                        onClick={() => exportChartAsPNG(lineChartRef, 'flowrate_trend.png')}
                        className="px-4 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition"
                    >
                        📥 Download PNG
                    </button>
                </div>
                <div className="h-64">
                    <Line ref={lineChartRef} data={lineData} options={options} />
                </div>
            </div>
        </div>
    );
}

AdvancedCharts.propTypes = {
    equipment: PropTypes.array.isRequired,
    analytics: PropTypes.object.isRequired
};