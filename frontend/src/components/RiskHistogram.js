import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const RiskHistogram = ({ data = [] }) => {
  // Define risk score bins
  const bins = [
    { label: '0-50', min: 0, max: 50, color: '#4caf50' },
    { label: '50-70', min: 50, max: 70, color: '#ff9800' },
    { label: '70-85', min: 70, max: 85, color: '#ff5722' },
    { label: '85-100', min: 85, max: 100, color: '#f44336' },
  ];

  // Count items in each bin
  const binCounts = bins.map(bin => {
    const count = data.filter(item => 
      item.score >= bin.min && item.score < bin.max
    ).length;
    return count;
  });

  const chartData = {
    labels: bins.map(bin => bin.label),
    datasets: [
      {
        label: 'Number of Items',
        data: binCounts,
        backgroundColor: bins.map(bin => bin.color + '80'), // Add transparency
        borderColor: bins.map(bin => bin.color),
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: false,
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            const bin = bins[context.dataIndex];
            return `${bin.label}: ${context.parsed.y} items`;
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          stepSize: 1,
        },
        title: {
          display: true,
          text: 'Number of Items',
        },
      },
      x: {
        title: {
          display: true,
          text: 'Risk Score Range',
        },
      },
    },
  };

  if (data.length === 0) {
    return (
      <div style={{ 
        height: 300, 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        color: '#666',
        fontSize: '14px'
      }}>
        No data available for risk distribution
      </div>
    );
  }

  return (
    <div style={{ height: 300, width: '100%' }}>
      <Bar data={chartData} options={options} />
    </div>
  );
};

export default RiskHistogram;

