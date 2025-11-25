import React, { useState, useEffect } from 'react'
import { geospatialAPI, rentAPI, groceryAPI, transportAPI } from '../services/api'
import '../App.css'

function LocalityComparison() {
  const [localities, setLocalities] = useState([])
  const [selectedLocalities, setSelectedLocalities] = useState([])
  const [comparisonData, setComparisonData] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadLocalities()
  }, [])

  useEffect(() => {
    if (selectedLocalities.length > 0) {
      loadComparisonData()
    }
  }, [selectedLocalities])

  const loadLocalities = async () => {
    try {
      const response = await geospatialAPI.getLocalities()
      setLocalities(response.data || [])
    } catch (err) {
      setError('Failed to load localities')
      console.error('Error loading localities:', err)
    }
  }

  const loadComparisonData = async () => {
    setLoading(true)
    setError(null)
    try {
      const comparisons = await Promise.all(
        selectedLocalities.map(async (localityId) => {
          const [statsRes, rentRes, groceryRes] = await Promise.all([
            geospatialAPI.getLocalityStats(localityId).catch(() => ({ data: null })),
            rentAPI.getAverageRent(localityId, '2BHK').catch(() => ({ data: null })),
            groceryAPI.calculateMonthlyCost(localityId).catch(() => ({ data: null })),
          ])

          const locality = localities.find(l => l.id === localityId)
          return {
            id: localityId,
            name: locality?.name || 'Unknown',
            stats: statsRes.data,
            avgRent: rentRes.data?.avg_rent || 0,
            groceryCost: groceryRes.data?.monthly_cost || 0,
          }
        })
      )
      setComparisonData(comparisons)
    } catch (err) {
      setError('Failed to load comparison data')
      console.error('Error loading comparison data:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleLocalityToggle = (localityId) => {
    setSelectedLocalities(prev => {
      if (prev.includes(localityId)) {
        return prev.filter(id => id !== localityId)
      } else if (prev.length < 5) {
        return [...prev, localityId]
      }
      return prev
    })
  }

  return (
    <div>
      <h1 style={{ marginBottom: '2rem' }}>Locality Comparison</h1>

      {error && <div className="error">{error}</div>}

      <div className="card">
        <div className="card-title">Select Localities to Compare (max 5)</div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '0.5rem' }}>
          {localities.map(locality => (
            <label key={locality.id} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <input
                type="checkbox"
                checked={selectedLocalities.includes(locality.id)}
                onChange={() => handleLocalityToggle(locality.id)}
                disabled={!selectedLocalities.includes(locality.id) && selectedLocalities.length >= 5}
              />
              {locality.name}
            </label>
          ))}
        </div>
      </div>

      {loading && <div className="loading">Loading comparison data...</div>}

      {comparisonData.length > 0 && (
        <div className="card">
          <div className="card-title">Comparison Results</div>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid #ddd' }}>
                  <th style={{ padding: '0.75rem', textAlign: 'left' }}>Locality</th>
                  <th style={{ padding: '0.75rem', textAlign: 'right' }}>Avg Rent (2BHK)</th>
                  <th style={{ padding: '0.75rem', textAlign: 'right' }}>Grocery Cost/Month</th>
                  <th style={{ padding: '0.75rem', textAlign: 'right' }}>Cost Burden Index</th>
                  <th style={{ padding: '0.75rem', textAlign: 'right' }}>Total Monthly Cost</th>
                </tr>
              </thead>
              <tbody>
                {comparisonData.map(item => {
                  const totalCost = item.avgRent + item.groceryCost + (item.stats?.avg_transport_cost_monthly || 0)
                  return (
                    <tr key={item.id} style={{ borderBottom: '1px solid #eee' }}>
                      <td style={{ padding: '0.75rem' }}>{item.name}</td>
                      <td style={{ padding: '0.75rem', textAlign: 'right' }}>
                        ₹{item.avgRent.toLocaleString()}
                      </td>
                      <td style={{ padding: '0.75rem', textAlign: 'right' }}>
                        ₹{item.groceryCost.toLocaleString()}
                      </td>
                      <td style={{ padding: '0.75rem', textAlign: 'right' }}>
                        {item.stats?.cost_burden_index?.toFixed(2) || 'N/A'}
                      </td>
                      <td style={{ padding: '0.75rem', textAlign: 'right', fontWeight: 'bold' }}>
                        ₹{totalCost.toLocaleString()}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}

export default LocalityComparison

