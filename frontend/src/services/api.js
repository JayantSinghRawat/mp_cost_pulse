import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add token to requests if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Handle 401 errors (unauthorized)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const rentAPI = {
  getListings: (params) => api.get('/rents/', { params }),
  getAverageRent: (localityId, propertyType) => 
    api.get(`/rents/avg/${localityId}`, { params: { property_type: propertyType } }),
}

export const groceryAPI = {
  getStores: (params) => api.get('/groceries/stores', { params }),
  getStoreItems: (storeId, category) => 
    api.get(`/groceries/stores/${storeId}/items`, { params: { category } }),
  calculateMonthlyCost: (localityId) => 
    api.get(`/groceries/cost/${localityId}`),
}

export const transportAPI = {
  getRoutes: (params) => api.get('/transport/routes', { params }),
  getRouteFares: (routeId) => api.get(`/transport/routes/${routeId}/fares`),
  calculateMonthlyCost: (sourceId, destId, tripsPerMonth = 60) =>
    api.get(`/transport/cost/${sourceId}/${destId}`, { params: { trips_per_month: tripsPerMonth } }),
}

export const inflationAPI = {
  getData: (params) => api.get('/inflation/', { params }),
  getLatest: (category) => api.get('/inflation/latest', { params: { category } }),
}

export const geospatialAPI = {
  getLocalities: (params) => api.get('/geospatial/localities', { params }),
  getLocalityStats: (localityId) => api.get(`/geospatial/localities/${localityId}/stats`),
  findNearby: (lat, lng, radiusKm = 5) => 
    api.get('/geospatial/nearby', { params: { latitude: lat, longitude: lng, radius_km: radiusKm } }),
  getHeatmapData: (dataType = 'rent') => 
    api.get('/geospatial/heatmap', { params: { data_type: dataType } }),
  calculateIsochrone: (lat, lng, timeMinutes = 30, transportMode = 'driving') =>
    api.get('/geospatial/isochrone', { 
      params: { 
        latitude: lat, 
        longitude: lng, 
        time_minutes: timeMinutes,
        transport_mode: transportMode 
      } 
    }),
  updateLocalityStats: (localityId) => 
    api.post(`/geospatial/localities/${localityId}/update-stats`),
}

export const authAPI = {
  login: (username, password) => 
    api.post('/auth/login-json', { username, password }),
  verifyOtp: (sessionToken, otpCode) =>
    api.post('/auth/verify-otp', { session_token: sessionToken, otp_code: otpCode }),
  register: (userData) => 
    api.post('/auth/register', userData),
  getCurrentUser: () => 
    api.get('/auth/me'),
}

export const mlAPI = {
  predictCost: (userProfile, localityId) =>
    api.post('/ml/predict-cost', { user_profile: userProfile, locality_id: localityId }),
  classifyRent: (listingId, localityId) =>
    api.post(`/ml/classify-rent/${listingId}`, { locality_id: localityId }),
  getModelVersion: (modelName) =>
    api.get(`/ml/models/${modelName}/version`),
}

export const recommendationAPI = {
  getNeighborhoodRecommendations: (requestData) =>
    api.post('/recommendations/neighborhoods', requestData),
  aggregateNeighborhood: (localityId, city) =>
    api.post(`/recommendations/aggregate/${localityId}`, null, { params: { city } }),
  refreshCityNeighborhoods: (city) =>
    api.post(`/recommendations/refresh/${city}`),
}

export default api

