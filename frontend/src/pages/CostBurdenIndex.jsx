import React, { useState, useEffect } from 'react'
import MapView from '../components/MapView'
import { geospatialAPI } from '../services/api'
import '../App.css'

function CostBurdenIndex() {
  const [heatmapData, setHeatmapData] = useState([])
  const [selectedLocality, setSelectedLocality] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadCostBurdenData()
  }, [])

  const loadCostBurdenData = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await geospatialAPI.getHeatmapData('cost_burden')
      setHeatmapData(response.data.points || [])
    } catch (err) {
      setError('Failed to load cost burden data')
      console.error('Error loading cost burden data:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleMarkerClick = async (point) => {
    try {
      const statsRes = await geospatialAPI.getLocalityStats(point.id)
      setSelectedLocality({
        ...point,
        stats: statsRes.data,
      })
    } catch (err) {
      console.error('Error loading locality stats:', err)
    }
  }

  const getBurdenCategory = (index) => {
    if (!index) return 'N/A'
    if (index < 30) return 'Low'
    if (index < 50) return 'Moderate'
    if (index < 70) return 'High'
    return 'Very High'
  }

  const getBurdenColor = (index) => {
    if (!index) return '#808080'
    if (index < 30) return '#4caf50'
    if (index < 50) return '#ffc107'
    if (index < 70) return '#ff9800'
    return '#f44336'
  }

  if (loading) {
    return <div className="loading">Loading cost burden data...</div>
  }

  return (
    <div>
      <h1 style={{ marginBottom: '2rem' }}>Cost Burden Index</h1>

      {error && <div className="error">{error}</div>}

      <div className="card">
        <div className="card-title">Cost Burden Heatmap</div>
        <p style={{ marginBottom: '1rem', color: '#666' }}>
          The Cost Burden Index represents the percentage of average income spent on housing, groceries, and transport.
          Lower values indicate more affordable areas.
        </p>
        <MapView 
          data={heatmapData.map(d => ({
            ...d,
            value: d.value || d.metadata?.cost_burden_index,
          }))} 
          center={[23.2599, 77.4126]} 
          zoom={11}
          onMarkerClick={handleMarkerClick}
        />
      </div>

      {selectedLocality && (
        <div className="card">
          <div className="card-title">Locality Details: {selectedLocality.name}</div>
          {selectedLocality.stats ? (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem' }}>
              <div>
                <div style={{ fontSize: '0.9rem', color: '#666', marginBottom: '0.5rem' }}>Cost Burden Index</div>
                <div style={{ 
                  fontSize: '2rem', 
                  fontWeight: 'bold',
                  color: getBurdenColor(selectedLocality.stats.cost_burden_index)
                }}>
                  {selectedLocality.stats.cost_burden_index?.toFixed(2)}%
                </div>
                <div style={{ color: '#666', marginTop: '0.5rem' }}>
                  Category: {getBurdenCategory(selectedLocality.stats.cost_burden_index)}
                </div>
              </div>
              <div>
                <div style={{ fontSize: '0.9rem', color: '#666', marginBottom: '0.5rem' }}>Average Rent (2BHK)</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
                  ₹{selectedLocality.stats.avg_rent_2bhk?.toLocaleString() || 'N/A'}
                </div>
              </div>
              <div>
                <div style={{ fontSize: '0.9rem', color: '#666', marginBottom: '0.5rem' }}>Monthly Grocery Cost</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
                  ₹{selectedLocality.stats.avg_grocery_cost_monthly?.toLocaleString() || 'N/A'}
                </div>
              </div>
              <div>
                <div style={{ fontSize: '0.9rem', color: '#666', marginBottom: '0.5rem' }}>Monthly Transport Cost</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
                  ₹{selectedLocality.stats.avg_transport_cost_monthly?.toLocaleString() || 'N/A'}
                </div>
              </div>
            </div>
          ) : (
            <div className="loading">Loading locality statistics...</div>
          )}
        </div>
      )}

      <div className="card">
        <div className="card-title">Legend</div>
        <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <div style={{ width: '20px', height: '20px', backgroundColor: '#4caf50', borderRadius: '50%' }}></div>
            <span>Low (&lt;30%)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <div style={{ width: '20px', height: '20px', backgroundColor: '#ffc107', borderRadius: '50%' }}></div>
            <span>Moderate (30-50%)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <div style={{ width: '20px', height: '20px', backgroundColor: '#ff9800', borderRadius: '50%' }}></div>
            <span>High (50-70%)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <div style={{ width: '20px', height: '20px', backgroundColor: '#f44336', borderRadius: '50%' }}></div>
            <span>Very High (&gt;70%)</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CostBurdenIndex

