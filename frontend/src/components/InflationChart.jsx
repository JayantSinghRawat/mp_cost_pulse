import React from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { Line } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

function InflationChart({ data }) {
  if (!data || data.length === 0) {
    return <div className="loading">No inflation data available</div>
  }

  // Group data by category
  const categories = [...new Set(data.map(d => d.category || 'Overall'))]
  const labels = [...new Set(data.map(d => d.period))].sort()
  
  const chartData = {
    labels: labels,
    datasets: categories.map((category, index) => {
      const categoryData = data.filter(d => (d.category || 'Overall') === category)
      const colors = [
        'rgb(75, 192, 192)',
        'rgb(255, 99, 132)',
        'rgb(54, 162, 235)',
        'rgb(255, 206, 86)',
        'rgb(153, 102, 255)',
      ]
      return {
        label: category,
        data: labels.map(label => {
          const item = categoryData.find(d => d.period === label)
          return item ? item.value : null
        }),
        borderColor: colors[index % colors.length],
        backgroundColor: colors[index % colors.length] + '40',
        tension: 0.1,
      }
    }),
  }

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Inflation Trends Over Time',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Inflation (%)',
        },
      },
    },
  }

  return (
    <div style={{ height: '400px' }}>
      <Line data={chartData} options={options} />
    </div>
  )
}

export default InflationChart

