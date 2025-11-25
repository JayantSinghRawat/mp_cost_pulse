import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { mlAPI, geospatialAPI } from '../services/api'
import '../App.css'

function UserProfile() {
  const { user } = useAuth()
  const [profile, setProfile] = useState({
    income: 50000,
    family_size: 1,
    property_type_preference: 2,
    commute_days_per_week: 5,
    distance_to_work_km: 10,
    amenities_priority: 2,
  })
  const [localities, setLocalities] = useState([])
  const [selectedLocality, setSelectedLocality] = useState(null)
  const [prediction, setPrediction] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadLocalities()
  }, [])

  const loadLocalities = async () => {
    try {
      const response = await geospatialAPI.getLocalities()
      setLocalities(response.data || [])
    } catch (err) {
      console.error('Error loading localities:', err)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!selectedLocality) {
      setError('Please select a locality')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const userProfile = {
        income: parseFloat(profile.income),
        family_size: parseInt(profile.family_size),
        property_type_preference: parseInt(profile.property_type_preference),
        commute_days_per_week: parseInt(profile.commute_days_per_week),
        distance_to_work_km: parseFloat(profile.distance_to_work_km) || 0,
        amenities_priority: parseInt(profile.amenities_priority),
      }

      const response = await mlAPI.predictCost(userProfile, selectedLocality)
      setPrediction(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to get prediction')
      console.error('Prediction error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1 style={{ marginBottom: '2rem' }}>Personalized Cost Prediction</h1>

      <div className="card" style={{ marginBottom: '2rem' }}>
        <div className="card-title">Your Profile</div>
        <form onSubmit={handleSubmit}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem', marginBottom: '1rem' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                Monthly Income (₹)
              </label>
              <input
                type="number"
                value={profile.income}
                onChange={(e) => setProfile({ ...profile, income: parseFloat(e.target.value) || 0 })}
                required
                style={{ width: '100%', padding: '0.75rem', border: '1px solid #ddd', borderRadius: '4px' }}
                placeholder="50000"
              />
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                Family Size
              </label>
              <input
                type="number"
                min="1"
                max="10"
                value={profile.family_size}
                onChange={(e) => setProfile({ ...profile, family_size: e.target.value })}
                required
                style={{ width: '100%', padding: '0.75rem', border: '1px solid #ddd', borderRadius: '4px' }}
              />
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                Property Type Preference
              </label>
              <select
                value={profile.property_type_preference}
                onChange={(e) => setProfile({ ...profile, property_type_preference: e.target.value })}
                style={{ width: '100%', padding: '0.75rem', border: '1px solid #ddd', borderRadius: '4px' }}
              >
                <option value={1}>1 BHK</option>
                <option value={2}>2 BHK</option>
                <option value={3}>3 BHK</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                Commute Days/Week
              </label>
              <input
                type="number"
                min="1"
                max="7"
                value={profile.commute_days_per_week}
                onChange={(e) => setProfile({ ...profile, commute_days_per_week: e.target.value })}
                required
                style={{ width: '100%', padding: '0.75rem', border: '1px solid #ddd', borderRadius: '4px' }}
              />
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                Distance to Work (km)
              </label>
              <input
                type="number"
                step="0.1"
                value={profile.distance_to_work_km}
                onChange={(e) => setProfile({ ...profile, distance_to_work_km: parseFloat(e.target.value) || 0 })}
                required
                style={{ width: '100%', padding: '0.75rem', border: '1px solid #ddd', borderRadius: '4px' }}
                placeholder="10"
              />
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                Amenities Priority
              </label>
              <select
                value={profile.amenities_priority}
                onChange={(e) => setProfile({ ...profile, amenities_priority: e.target.value })}
                style={{ width: '100%', padding: '0.75rem', border: '1px solid #ddd', borderRadius: '4px' }}
              >
                <option value={1}>Low</option>
                <option value={2}>Medium</option>
                <option value={3}>High</option>
              </select>
            </div>
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
              Select Locality
            </label>
            <select
              value={selectedLocality || ''}
              onChange={(e) => setSelectedLocality(parseInt(e.target.value))}
              required
              style={{ width: '100%', padding: '0.75rem', border: '1px solid #ddd', borderRadius: '4px' }}
            >
              <option value="">-- Select a locality --</option>
              {localities.map(loc => (
                <option key={loc.id} value={loc.id}>{loc.name}</option>
              ))}
            </select>
          </div>

          {error && <div className="error" style={{ marginBottom: '1rem' }}>{error}</div>}

          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              padding: '0.75rem',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              fontSize: '1rem',
              fontWeight: '600',
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.7 : 1
            }}
          >
            {loading ? 'Predicting...' : 'Get Cost Prediction'}
          </button>
        </form>
      </div>

      {prediction && (
        <div className="card">
          <div className="card-title">Prediction Results</div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem' }}>
            <div>
              <div style={{ fontSize: '0.9rem', color: '#666', marginBottom: '0.5rem' }}>Predicted Monthly Cost</div>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#667eea' }}>
                ₹{prediction.predicted_monthly_cost?.toLocaleString() || 'N/A'}
              </div>
            </div>
            <div>
              <div style={{ fontSize: '0.9rem', color: '#666', marginBottom: '0.5rem' }}>Rent</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
                ₹{prediction.breakdown?.rent?.toLocaleString() || 'N/A'}
              </div>
            </div>
            <div>
              <div style={{ fontSize: '0.9rem', color: '#666', marginBottom: '0.5rem' }}>Groceries</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
                ₹{prediction.breakdown?.groceries?.toLocaleString() || 'N/A'}
              </div>
            </div>
            <div>
              <div style={{ fontSize: '0.9rem', color: '#666', marginBottom: '0.5rem' }}>Transport</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
                ₹{prediction.breakdown?.transport?.toLocaleString() || 'N/A'}
              </div>
            </div>
          </div>
          {prediction.confidence && (
            <div style={{ marginTop: '1rem', padding: '1rem', background: '#f5f5f5', borderRadius: '4px' }}>
              <div style={{ fontSize: '0.9rem', color: '#666' }}>
                Prediction Confidence: {(prediction.confidence * 100).toFixed(1)}%
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default UserProfile

