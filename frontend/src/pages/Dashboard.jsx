import React, { useState, useEffect } from 'react'
import MapView from '../components/MapView'
import InflationChart from '../components/InflationChart'
import { geospatialAPI, inflationAPI } from '../services/api'
import '../App.css'

function Dashboard() {
  const [heatmapData, setHeatmapData] = useState([])
  const [inflationData, setInflationData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [dataType, setDataType] = useState('rent')

  useEffect(() => {
    loadData()
  }, [dataType])

  const loadData = async () => {
    setLoading(true)
    setError(null)
    try {
      const [heatmapRes, inflationRes] = await Promise.all([
        geospatialAPI.getHeatmapData(dataType),
        inflationAPI.getData({ limit: 100 }),
      ])
      setHeatmapData(heatmapRes.data.points || [])
      setInflationData(inflationRes.data || [])
    } catch (err) {
      setError(err.message || 'Failed to load data')
      console.error('Error loading data:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleMarkerClick = (point) => {
    console.log('Marker clicked:', point)
  }

  if (loading) {
    return <div className="loading">Loading dashboard data...</div>
  }

  return (
    <div>
      <h1 style={{ marginBottom: '2rem' }}>Cost of Living Dashboard</h1>
      
      {error && <div className="error">{error}</div>}

      <div className="card">
        <div className="card-title">Heatmap Visualization</div>
        <div style={{ marginBottom: '1rem' }}>
          <label>
            Data Type:{' '}
            <select 
              value={dataType} 
              onChange={(e) => setDataType(e.target.value)}
              style={{ padding: '0.5rem', fontSize: '1rem' }}
            >
              <option value="rent">Rent</option>
              <option value="cost_burden">Cost Burden Index</option>
              <option value="grocery">Grocery</option>
              <option value="transport">Transport</option>
            </select>
          </label>
        </div>
        <MapView 
          data={heatmapData} 
          center={[23.2599, 77.4126]} 
          zoom={11}
          onMarkerClick={handleMarkerClick}
        />
      </div>

      <div className="card">
        <div className="card-title">Inflation Trends</div>
        <InflationChart data={inflationData} />
      </div>

      <div className="card">
        <div className="card-title">Quick Stats</div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          <div>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#667eea' }}>
              {heatmapData.length}
            </div>
            <div style={{ color: '#666' }}>Localities</div>
          </div>
          <div>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#667eea' }}>
              {inflationData.length}
            </div>
            <div style={{ color: '#666' }}>Inflation Records</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard

