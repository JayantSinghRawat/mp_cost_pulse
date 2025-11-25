import React, { useState, useEffect } from 'react'
import { mlAPI } from '../services/api'
import '../App.css'

function RentListingCard({ listing, localityAvgRent }) {
  const [classification, setClassification] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (listing.id) {
      classifyListing()
    }
  }, [listing.id])

  const classifyListing = async () => {
    setLoading(true)
    try {
      const response = await mlAPI.classifyRent(listing.id, listing.locality_id)
      setClassification(response.data)
    } catch (err) {
      console.error('Classification error:', err)
    } finally {
      setLoading(false)
    }
  }

  const getClassificationColor = () => {
    if (!classification) return '#666'
    return classification.classification === 'fair' ? '#4caf50' : '#f44336'
  }

  return (
    <div className="card" style={{ marginBottom: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '0.5rem' }}>
        <h3 style={{ margin: 0, fontSize: '1.2rem' }}>{listing.title}</h3>
        {classification && (
          <span
            style={{
              padding: '0.25rem 0.75rem',
              borderRadius: '12px',
              fontSize: '0.85rem',
              fontWeight: '600',
              background: getClassificationColor() + '20',
              color: getClassificationColor()
            }}
          >
            {classification.classification === 'fair' ? '✓ Fair Price' : '⚠ Overpriced'}
          </span>
        )}
      </div>
      
      <div style={{ color: '#666', marginBottom: '0.5rem' }}>
        {listing.address && <div>{listing.address}</div>}
        {listing.property_type && <div>Type: {listing.property_type}</div>}
        {listing.area_sqft && <div>Area: {listing.area_sqft} sqft</div>}
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#667eea' }}>
            ₹{listing.rent_amount?.toLocaleString()}
          </div>
          {localityAvgRent && (
            <div style={{ fontSize: '0.85rem', color: '#666' }}>
              Avg: ₹{localityAvgRent.toLocaleString()}
            </div>
          )}
        </div>
        {loading && <div style={{ color: '#666' }}>Analyzing...</div>}
      </div>

      {classification && classification.price_comparison && (
        <div style={{ marginTop: '0.5rem', padding: '0.5rem', background: '#f5f5f5', borderRadius: '4px', fontSize: '0.85rem' }}>
          {classification.price_comparison.difference_percent > 0 ? (
            <span style={{ color: '#f44336' }}>
              {classification.price_comparison.difference_percent.toFixed(1)}% above average
            </span>
          ) : (
            <span style={{ color: '#4caf50' }}>
              {Math.abs(classification.price_comparison.difference_percent).toFixed(1)}% below average
            </span>
          )}
        </div>
      )}
    </div>
  )
}

export default RentListingCard

