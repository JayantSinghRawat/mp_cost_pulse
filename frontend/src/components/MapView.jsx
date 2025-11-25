import React, { useEffect, useRef } from 'react'
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Fix for default marker icons
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
})

function MapUpdater({ center, zoom }) {
  const map = useMap()
  useEffect(() => {
    map.setView(center, zoom)
  }, [map, center, zoom])
  return null
}

function MapView({ data, center = [23.2599, 77.4126], zoom = 12, onMarkerClick }) {
  const mapRef = useRef(null)

  const getColor = (value, maxValue) => {
    if (!value || !maxValue) return '#808080'
    const ratio = value / maxValue
    if (ratio > 0.7) return '#d73027'
    if (ratio > 0.5) return '#f46d43'
    if (ratio > 0.3) return '#fdae61'
    return '#fee08b'
  }

  const maxValue = data.length > 0 
    ? Math.max(...data.map(d => d.value || 0).filter(v => v > 0))
    : 1

  return (
    <div style={{ height: '500px', width: '100%', borderRadius: '8px', overflow: 'hidden' }}>
      <MapContainer
        center={center}
        zoom={zoom}
        style={{ height: '100%', width: '100%' }}
        ref={mapRef}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <MapUpdater center={center} zoom={zoom} />
        {data.map((point) => {
          if (!point.latitude || !point.longitude) return null
          const radius = point.value ? Math.max(5, (point.value / maxValue) * 20) : 5
          return (
            <CircleMarker
              key={point.id}
              center={[point.latitude, point.longitude]}
              radius={radius}
              pathOptions={{
                color: getColor(point.value, maxValue),
                fillColor: getColor(point.value, maxValue),
                fillOpacity: 0.6,
                weight: 2,
              }}
              eventHandlers={{
                click: () => onMarkerClick && onMarkerClick(point),
              }}
            >
              <Popup>
                <div>
                  <strong>{point.name}</strong>
                  {point.value !== undefined && (
                    <div>Value: {point.value.toFixed(2)}</div>
                  )}
                  {point.metadata && (
                    <div>
                      {Object.entries(point.metadata).map(([key, val]) => (
                        <div key={key}>{key}: {val}</div>
                      ))}
                    </div>
                  )}
                </div>
              </Popup>
            </CircleMarker>
          )
        })}
      </MapContainer>
    </div>
  )
}

export default MapView

