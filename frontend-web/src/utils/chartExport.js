import { saveAs } from 'file-saver';

/**
 * Export Chart.js chart as PNG image
 */
export const exportChartAsPNG = (chartRef, filename = 'chart.png') => {
    if (!chartRef || !chartRef.current) {
        console.error('Chart reference not found');
        return;
    }

    const canvas = chartRef.current.canvas;
    canvas.toBlob((blob) => {
        saveAs(blob, filename);
    });
};

/**
 * Export data as CSV
 */
export const exportAsCSV = (data, headers, filename = 'data.csv') => {
    const csvContent = [
        headers.join(','),
        ...data.map(row => row.join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    saveAs(blob, filename);
};

/**
 * Export equipment data as Excel-compatible CSV
 */
export const exportEquipmentAsExcel = (equipment, filename = 'equipment_data.csv') => {
    const headers = ['Equipment Name', 'Type', 'Flowrate (m³/h)', 'Pressure (bar)', 'Temperature (°C)', 'Pressure Outlier', 'Temperature Outlier'];

    const data = equipment.map(eq => [
        eq.equipment_name,
        eq.equipment_type,
        eq.flowrate.toFixed(2),
        eq.pressure.toFixed(2),
        eq.temperature.toFixed(2),
        eq.is_pressure_outlier ? 'Yes' : 'No',
        eq.is_temperature_outlier ? 'Yes' : 'No'
    ]);

    exportAsCSV(data, headers, filename);
};