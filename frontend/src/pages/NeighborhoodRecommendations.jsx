import React, { useState } from 'react'
import { recommendationAPI } from '../services/api'
import '../App.css'

function NeighborhoodRecommendations() {
  const [formData, setFormData] = useState({
    city: 'Bhopal',
    number_of_people: 2,
    max_travel_distance_km: 5,
    budget: 30000,
    property_type: '2BHK',
    top_n: 10
  })
  
  const [weights, setWeights] = useState({
    rent: 0.25,
    grocery_cost: 0.15,
    delivery_availability: 0.10,
    aqi: 0.15,
    hygiene: 0.10,
    amenities: 0.15,
    connectivity: 0.10
  })
  
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: name === 'number_of_people' || name === 'top_n' ? parseInt(value) : 
              name === 'max_travel_distance_km' || name === 'budget' ? parseFloat(value) : value
    }))
  }

  const handleWeightChange = (factor, value) => {
    setWeights(prev => ({
      ...prev,
      [factor]: parseFloat(value) || 0
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    
    try {
      const response = await recommendationAPI.getNeighborhoodRecommendations({
        ...formData,
        weights: weights
      })
      setRecommendations(response.data.recommendations || [])
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to get recommendations')
    } finally {
      setLoading(false)
    }
  }

  const getScoreColor = (score) => {
    if (score >= 0.8) return '#4caf50'
    if (score >= 0.6) return '#8bc34a'
    if (score >= 0.4) return '#ffc107'
    return '#ff9800'
  }

  const getAQIColor = (aqi) => {
    if (aqi <= 50) return '#4caf50'
    if (aqi <= 100) return '#8bc34a'
    if (aqi <= 150) return '#ffc107'
    if (aqi <= 200) return '#ff9800'
    return '#f44336'
  }

  return (
    <div style={{ padding: '2rem', maxWidth: '1400px', margin: '0 auto' }}>
      <h1 style={{ marginBottom: '2rem', color: '#333' }}>Find Your Perfect Neighborhood</h1>
      
      <div className="card" style={{ marginBottom: '2rem' }}>
        <h2 className="card-title">Search Parameters</h2>
        <form onSubmit={handleSubmit}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>City</label>
              <select
                name="city"
                value={formData.city}
                onChange={handleInputChange}
                required
                style={{ width: '100%', padding: '0.75rem', border: '1px solid #ddd', borderRadius: '4px' }}
              >
                <option value="Bhopal">Bhopal</option>
                <option value="Indore">Indore</option>
                <option value="Gwalior">Gwalior</option>
                <option value="Jabalpur">Jabalpur</option>
                <option value="Ujjain">Ujjain</option>
                <option value="Sagar">Sagar</option>
                <option value="Ratlam">Ratlam</option>
              </select>
            </div>
            
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>Number of People</label>
              <input
                type="number"
                name="number_of_people"
                value={formData.number_of_people}
                onChange={handleInputChange}
                min="1"
                max="10"
                required
                style={{ width: '100%', padding: '0.75rem', border: '1px solid #ddd', borderRadius: '4px' }}
              />
            </div>
            
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>Max Travel Distance (km)</label>
              <input
                type="number"
                name="max_travel_distance_km"
                value={formData.max_travel_distance_km}
                onChange={handleInputChange}
                min="0"
                max="50"
                step="0.5"
                required
                style={{ width: '100%', padding: '0.75rem', border: '1px solid #ddd', borderRadius: '4px' }}
              />
            </div>
            
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>Monthly Budget (₹)</label>
              <input
                type="number"
                name="budget"
                value={formData.budget}
                onChange={handleInputChange}
                min="0"
                step="1000"
                required
                style={{ width: '100%', padding: '0.75rem', border: '1px solid #ddd', borderRadius: '4px' }}
              />
            </div>
            
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>Property Type</label>
              <select
                name="property_type"
                value={formData.property_type}
                onChange={handleInputChange}
                style={{ width: '100%', padding: '0.75rem', border: '1px solid #ddd', borderRadius: '4px' }}
              >
                <option value="1BHK">1 BHK</option>
                <option value="2BHK">2 BHK</option>
                <option value="3BHK">3 BHK</option>
              </select>
            </div>
            
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>Top N Results</label>
              <input
                type="number"
                name="top_n"
                value={formData.top_n}
                onChange={handleInputChange}
                min="1"
                max="50"
                required
                style={{ width: '100%', padding: '0.75rem', border: '1px solid #ddd', borderRadius: '4px' }}
              />
            </div>
          </div>

          <div style={{ marginBottom: '1.5rem' }}>
            <h3 style={{ marginBottom: '1rem', fontSize: '1.1rem', fontWeight: '600' }}>Factor Weights (adjust importance)</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
              {Object.entries(weights).map(([factor, weight]) => (
                <div key={factor}>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem' }}>
                    {factor.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    value={weight}
                    onChange={(e) => handleWeightChange(factor, e.target.value)}
                    style={{ width: '100%' }}
                  />
                  <span style={{ fontSize: '0.85rem', color: '#666' }}>{(weight * 100).toFixed(0)}%</span>
                </div>
              ))}
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            style={{
              padding: '0.75rem 2rem',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '1rem',
              fontWeight: '600',
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.7 : 1
            }}
          >
            {loading ? 'Finding Recommendations...' : 'Get Recommendations'}
          </button>
        </form>
      </div>

      {error && (
        <div className="error" style={{ marginBottom: '1rem' }}>
          {error}
        </div>
      )}

      {recommendations.length > 0 && (
        <div>
          <h2 style={{ marginBottom: '1rem', color: '#333' }}>
            Top {recommendations.length} Recommendations
          </h2>
          
          <div style={{ display: 'grid', gap: '1.5rem' }}>
            {recommendations.map((rec, index) => (
              <div key={rec.neighborhood_id} className="card" style={{ position: 'relative' }}>
                <div style={{
                  position: 'absolute',
                  top: '1rem',
                  right: '1rem',
                  background: getScoreColor(rec.score),
                  color: 'white',
                  padding: '0.5rem 1rem',
                  borderRadius: '20px',
                  fontWeight: 'bold',
                  fontSize: '0.9rem'
                }}>
                  #{index + 1} Score: {(rec.score * 100).toFixed(1)}%
                </div>
                
                <h3 style={{ fontSize: '1.5rem', marginBottom: '0.5rem', color: '#667eea' }}>
                  {rec.locality_name}
                </h3>
                
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1rem' }}>
                  <div>
                    <strong>Rent:</strong> ₹{rec.rent.toLocaleString()}/month
                  </div>
                  <div>
                    <strong>Grocery Cost:</strong> ₹{rec.grocery_cost?.toLocaleString() || 'N/A'}/month
                    {rec.grocery_stores_count > 0 && (
                      <span style={{ fontSize: '0.85rem', color: '#666', marginLeft: '0.5rem' }}>
                        ({rec.grocery_stores_count} stores)
                      </span>
                    )}
                  </div>
                  <div>
                    <strong>Total Monthly:</strong> ₹{rec.total_monthly_cost.toLocaleString()}
                  </div>
                  <div>
                    <strong>AQI:</strong> 
                    <span style={{
                      color: getAQIColor(rec.aqi),
                      fontWeight: 'bold',
                      marginLeft: '0.5rem'
                    }}>
                      {rec.aqi.toFixed(0)} ({rec.aqi_category})
                    </span>
                  </div>
                  <div>
                    <strong>Hygiene Rating:</strong> {rec.hygiene_rating?.toFixed(1) || 'N/A'}/5.0
                    {rec.restaurants_count > 0 && (
                      <span style={{ fontSize: '0.85rem', color: '#666', marginLeft: '0.5rem' }}>
                        ({rec.restaurants_count} restaurants)
                      </span>
                    )}
                  </div>
                  <div>
                    <strong>Amenities Score:</strong> {rec.amenities_score.toFixed(1)}/10
                  </div>
                </div>

                {/* Food & Beverages Section */}
                <div style={{ marginBottom: '1rem', padding: '1rem', background: '#f9f9f9', borderRadius: '8px' }}>
                  <strong>🍽️ Food & Beverages:</strong>
                  <div style={{ display: 'flex', gap: '1.5rem', marginTop: '0.5rem', flexWrap: 'wrap' }}>
                    {rec.restaurants_count > 0 ? (
                      <span>
                        <strong>Restaurants:</strong> {rec.restaurants_count}
                        {rec.highly_rated_restaurants > 0 && (
                          <span style={{ color: '#4caf50', marginLeft: '0.5rem' }}>
                            ({rec.highly_rated_restaurants} highly rated ⭐)
                          </span>
                        )}
                      </span>
                    ) : (
                      <span style={{ color: '#999' }}>
                        <strong>Restaurants:</strong> Data being collected
                      </span>
                    )}
                    {rec.avg_restaurant_rating ? (
                      <span>
                        <strong>Avg Rating:</strong> {rec.avg_restaurant_rating.toFixed(1)}/5.0
                      </span>
                    ) : rec.hygiene_rating ? (
                      <span>
                        <strong>Hygiene Rating:</strong> {rec.hygiene_rating.toFixed(1)}/5.0
                      </span>
                    ) : null}
                    {rec.grocery_stores_count > 0 ? (
                      <span>
                        <strong>Grocery Stores:</strong> {rec.grocery_stores_count}
                      </span>
                    ) : (
                      <span style={{ color: '#999' }}>
                        <strong>Grocery Stores:</strong> Data being collected
                      </span>
                    )}
                  </div>
                </div>

                <div style={{ marginBottom: '1rem' }}>
                  <strong>Delivery Services:</strong>
                  <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem' }}>
                    {rec.delivery_services.blinkit && <span style={{ background: '#f0f0f0', padding: '0.25rem 0.75rem', borderRadius: '4px' }}>Blinkit</span>}
                    {rec.delivery_services.zomato && <span style={{ background: '#f0f0f0', padding: '0.25rem 0.75rem', borderRadius: '4px' }}>Zomato</span>}
                    {rec.delivery_services.swiggy && <span style={{ background: '#f0f0f0', padding: '0.25rem 0.75rem', borderRadius: '4px' }}>Swiggy</span>}
                    {!rec.delivery_services.blinkit && !rec.delivery_services.zomato && !rec.delivery_services.swiggy && 
                      <span style={{ color: '#999' }}>No delivery services</span>}
                  </div>
                </div>

                <div>
                  <strong>Amenities:</strong>
                  <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem', flexWrap: 'wrap' }}>
                    <span>🏥 Hospitals: {rec.amenities.hospitals}</span>
                    <span>🏫 Schools: {rec.amenities.schools}</span>
                    <span>🌳 Parks: {rec.amenities.parks}</span>
                    <span>🛍️ Malls: {rec.amenities.malls}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default NeighborhoodRecommendations

