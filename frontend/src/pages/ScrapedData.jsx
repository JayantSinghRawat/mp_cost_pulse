import React, { useState, useEffect } from 'react'
import { rentAPI, groceryAPI, geospatialAPI } from '../services/api'
import '../App.css'

function ScrapedData() {
  const [localities, setLocalities] = useState([])
  const [selectedLocality, setSelectedLocality] = useState(null)
  const [rentListings, setRentListings] = useState([])
  const [groceryItems, setGroceryItems] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('rent') // 'rent' or 'grocery'

  useEffect(() => {
    loadLocalities()
  }, [])

  useEffect(() => {
    if (selectedLocality) {
      loadData()
    }
  }, [selectedLocality, activeTab])

  const loadLocalities = async () => {
    try {
      const response = await geospatialAPI.getLocalities({ city: 'Bhopal' })
      setLocalities(response.data || [])
      if (response.data && response.data.length > 0) {
        setSelectedLocality(response.data[0].id)
      }
    } catch (err) {
      setError('Failed to load localities')
      console.error('Error loading localities:', err)
    }
  }

  const loadData = async () => {
    if (!selectedLocality) return
    
    setLoading(true)
    setError(null)
    
    try {
      if (activeTab === 'rent') {
        const response = await rentAPI.getListings({ locality_id: selectedLocality, limit: 100 })
        setRentListings(response.data || [])
      } else {
        // Get grocery stores for locality
        const storesResponse = await groceryAPI.getStores({ locality_id: selectedLocality })
        const stores = storesResponse.data || []
        
        if (stores.length > 0) {
          // Get items from first store
          const itemsResponse = await groceryAPI.getStoreItems(stores[0].id)
          setGroceryItems(itemsResponse.data || [])
        } else {
          setGroceryItems([])
        }
      }
    } catch (err) {
      setError('Failed to load data')
      console.error('Error loading data:', err)
    } finally {
      setLoading(false)
    }
  }

  const selectedLocalityName = localities.find(l => l.id === selectedLocality)?.name || 'Select Locality'

  return (
    <div style={{ padding: '2rem', maxWidth: '1400px', margin: '0 auto' }}>
      <h1 style={{ marginBottom: '2rem', color: '#333' }}>Scraped Data - Bhopal</h1>

      {error && <div className="error" style={{ marginBottom: '1rem' }}>{error}</div>}

      {/* Locality Selector */}
      <div className="card" style={{ marginBottom: '2rem' }}>
        <div className="card-title">Select Locality</div>
        <select
          value={selectedLocality || ''}
          onChange={(e) => setSelectedLocality(parseInt(e.target.value))}
          style={{
            width: '100%',
            padding: '0.75rem',
            border: '1px solid #ddd',
            borderRadius: '4px',
            fontSize: '1rem'
          }}
        >
          {localities.map(loc => (
            <option key={loc.id} value={loc.id}>{loc.name}</option>
          ))}
        </select>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem', borderBottom: '2px solid #ddd' }}>
        <button
          onClick={() => setActiveTab('rent')}
          style={{
            padding: '0.75rem 1.5rem',
            background: activeTab === 'rent' ? '#667eea' : 'transparent',
            color: activeTab === 'rent' ? 'white' : '#667eea',
            border: 'none',
            borderBottom: activeTab === 'rent' ? '3px solid #667eea' : '3px solid transparent',
            cursor: 'pointer',
            fontWeight: '600',
            fontSize: '1rem'
          }}
        >
          Rent Listings ({rentListings.length})
        </button>
        <button
          onClick={() => setActiveTab('grocery')}
          style={{
            padding: '0.75rem 1.5rem',
            background: activeTab === 'grocery' ? '#667eea' : 'transparent',
            color: activeTab === 'grocery' ? 'white' : '#667eea',
            border: 'none',
            borderBottom: activeTab === 'grocery' ? '3px solid #667eea' : '3px solid transparent',
            cursor: 'pointer',
            fontWeight: '600',
            fontSize: '1rem'
          }}
        >
          Grocery Items ({groceryItems.length})
        </button>
      </div>

      {loading && <div className="loading">Loading data...</div>}

      {/* Rent Listings */}
      {activeTab === 'rent' && !loading && (
        <div>
          <div style={{ marginBottom: '1rem', color: '#666' }}>
            Showing {rentListings.length} rent listings for <strong>{selectedLocalityName}</strong>
          </div>
          
          {rentListings.length === 0 ? (
            <div className="card" style={{ textAlign: 'center', padding: '3rem', color: '#666' }}>
              No rent listings found for this locality
            </div>
          ) : (
            <div style={{ display: 'grid', gap: '1rem' }}>
              {rentListings.map(listing => (
                <div key={listing.id} className="card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
                    <div>
                      <h3 style={{ margin: 0, marginBottom: '0.5rem', color: '#667eea' }}>
                        {listing.title || `${listing.property_type} in ${selectedLocalityName}`}
                      </h3>
                      <div style={{ display: 'flex', gap: '1rem', color: '#666', fontSize: '0.9rem' }}>
                        {listing.property_type && (
                          <span>Type: <strong>{listing.property_type}</strong></span>
                        )}
                        {listing.area_sqft && (
                          <span>Area: <strong>{listing.area_sqft} sqft</strong></span>
                        )}
                        {listing.source && (
                          <span>Source: <strong>{listing.source}</strong></span>
                        )}
                      </div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: '1.8rem', fontWeight: 'bold', color: '#667eea' }}>
                        ₹{listing.rent_amount?.toLocaleString()}
                      </div>
                      <div style={{ fontSize: '0.85rem', color: '#666' }}>per month</div>
                    </div>
                  </div>
                  
                  {listing.description && (
                    <div style={{ color: '#666', marginBottom: '0.5rem' }}>
                      {listing.description}
                    </div>
                  )}
                  
                  {listing.address && (
                    <div style={{ color: '#666', fontSize: '0.9rem' }}>
                      📍 {listing.address}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Grocery Items */}
      {activeTab === 'grocery' && !loading && (
        <div>
          <div style={{ marginBottom: '1rem', color: '#666' }}>
            Showing {groceryItems.length} grocery items for <strong>{selectedLocalityName}</strong>
          </div>
          
          {groceryItems.length === 0 ? (
            <div className="card" style={{ textAlign: 'center', padding: '3rem', color: '#666' }}>
              No grocery items found for this locality
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '1rem' }}>
              {groceryItems.map(item => (
                <div key={item.id} className="card">
                  <div style={{ marginBottom: '0.5rem' }}>
                    <h4 style={{ margin: 0, color: '#333' }}>{item.name}</h4>
                    {item.category && (
                      <div style={{ fontSize: '0.85rem', color: '#666' }}>
                        {item.category}
                      </div>
                    )}
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#667eea' }}>
                      ₹{item.price?.toLocaleString()}
                    </div>
                    {item.unit && (
                      <div style={{ fontSize: '0.85rem', color: '#666' }}>
                        per {item.unit}
                      </div>
                    )}
                  </div>
                  {item.brand && (
                    <div style={{ fontSize: '0.85rem', color: '#666', marginTop: '0.5rem' }}>
                      Brand: {item.brand}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default ScrapedData

