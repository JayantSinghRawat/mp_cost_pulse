"""
Scraping services for neighborhood data including AQI, delivery availability, 
hygiene indicators, and amenities
"""
import requests
import time
from typing import Dict, List, Optional
from datetime import datetime
from app.core.config import settings

class AQIScrapingService:
    """Service to scrape Air Quality Index data"""
    
    @staticmethod
    def get_aqi_by_location(latitude: float, longitude: float, city: str) -> Dict:
        """
        Get AQI data for a location
        Uses OpenWeatherMap or AQICN API (free tier available)
        """
        try:
            # Option 1: Using OpenWeatherMap Air Pollution API
            # Requires API key in config
            api_key = getattr(settings, 'OPENWEATHER_API_KEY', None)
            if api_key:
                url = "http://api.openweathermap.org/data/2.5/air_pollution"
                params = {
                    'lat': latitude,
                    'lon': longitude,
                    'appid': api_key
                }
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    components = data.get('list', [{}])[0].get('components', {})
                    aqi = data.get('list', [{}])[0].get('main', {}).get('aqi', 0)
                    
                    return {
                        'aqi_value': aqi,
                        'aqi_category': AQIScrapingService._get_aqi_category(aqi),
                        'aqi_pm25': components.get('pm2_5', 0),
                        'aqi_pm10': components.get('pm10', 0),
                        'aqi_no2': components.get('no2', 0),
                        'source': 'openweathermap',
                        'timestamp': datetime.utcnow().isoformat()
                    }
            
            # Option 2: Using AQICN API (free, no key required for basic usage)
            # Fallback if OpenWeatherMap not available
            url = f"https://api.waqi.info/feed/geo:{latitude};{longitude}/"
            token = getattr(settings, 'AQICN_TOKEN', 'demo')  # 'demo' token for testing
            params = {'token': token}
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'ok':
                    aqi_data = data.get('data', {})
                    iaqi = aqi_data.get('iaqi', {})
                    
                    return {
                        'aqi_value': aqi_data.get('aqi', 0),
                        'aqi_category': AQIScrapingService._get_aqi_category(aqi_data.get('aqi', 0)),
                        'aqi_pm25': iaqi.get('pm25', {}).get('v', 0) if isinstance(iaqi.get('pm25'), dict) else 0,
                        'aqi_pm10': iaqi.get('pm10', {}).get('v', 0) if isinstance(iaqi.get('pm10'), dict) else 0,
                        'aqi_no2': iaqi.get('no2', {}).get('v', 0) if isinstance(iaqi.get('no2'), dict) else 0,
                        'source': 'aqicn',
                        'timestamp': datetime.utcnow().isoformat()
                    }
            
            # Fallback: Return default values if APIs fail
            return {
                'aqi_value': 50,  # Moderate
                'aqi_category': 'Moderate',
                'aqi_pm25': 0,
                'aqi_pm10': 0,
                'aqi_no2': 0,
                'source': 'default',
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"Error fetching AQI: {e}")
            return {
                'aqi_value': 50,
                'aqi_category': 'Moderate',
                'aqi_pm25': 0,
                'aqi_pm10': 0,
                'aqi_no2': 0,
                'source': 'error',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    @staticmethod
    def _get_aqi_category(aqi: float) -> str:
        """Convert AQI value to category"""
        if aqi <= 50:
            return 'Good'
        elif aqi <= 100:
            return 'Moderate'
        elif aqi <= 150:
            return 'Unhealthy for Sensitive Groups'
        elif aqi <= 200:
            return 'Unhealthy'
        elif aqi <= 300:
            return 'Very Unhealthy'
        else:
            return 'Hazardous'


class DeliveryAvailabilityService:
    """Service to check delivery availability (Blinkit, Zomato, Swiggy)"""
    
    @staticmethod
    def check_blinkit_availability(latitude: float, longitude: float, city: str) -> Dict:
        """Check if Blinkit delivers to this location"""
        try:
            # Blinkit API endpoint (may require API key or scraping)
            # This is a placeholder - actual implementation would use their API
            url = "https://blinkit.com/api/location/check"
            headers = {
                'User-Agent': settings.USER_AGENT,
                'Accept': 'application/json'
            }
            params = {
                'lat': latitude,
                'lng': longitude,
                'city': city
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    'available': data.get('serviceable', False),
                    'delivery_time': data.get('estimated_delivery_time', None),
                    'source': 'blinkit_api',
                    'timestamp': datetime.utcnow().isoformat()
                }
        except Exception as e:
            print(f"Error checking Blinkit availability: {e}")
        
        # Fallback: Try to determine based on city (Blinkit operates in major cities)
        major_cities = ['Delhi', 'Mumbai', 'Bangalore', 'Hyderabad', 'Pune', 'Chennai', 'Kolkata']
        return {
            'available': city in major_cities or 'Bhopal' in city,
            'delivery_time': None,
            'source': 'fallback',
            'timestamp': datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def check_zomato_availability(latitude: float, longitude: float, city: str) -> Dict:
        """Check if Zomato delivers to this location"""
        try:
            # Zomato API (requires API key)
            api_key = getattr(settings, 'ZOMATO_API_KEY', None)
            if api_key:
                url = "https://developers.zomato.com/api/v2.1/geocode"
                headers = {
                    'user-key': api_key,
                    'Accept': 'application/json'
                }
                params = {
                    'lat': latitude,
                    'lon': longitude
                }
                
                response = requests.get(url, headers=headers, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    restaurants = data.get('nearby_restaurants', [])
                    return {
                        'available': len(restaurants) > 0,
                        'restaurants_count': len(restaurants),
                        'source': 'zomato_api',
                        'timestamp': datetime.utcnow().isoformat()
                    }
        except Exception as e:
            print(f"Error checking Zomato availability: {e}")
        
        # Fallback
        return {
            'available': True,  # Zomato is widely available
            'restaurants_count': 0,
            'source': 'fallback',
            'timestamp': datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def check_swiggy_availability(latitude: float, longitude: float, city: str) -> Dict:
        """Check if Swiggy delivers to this location"""
        try:
            # Swiggy API endpoint (may require scraping or API key)
            url = "https://www.swiggy.com/api/restaurants"
            headers = {
                'User-Agent': settings.USER_AGENT,
                'Accept': 'application/json'
            }
            params = {
                'lat': latitude,
                'lng': longitude
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                restaurants = data.get('data', {}).get('cards', [])
                return {
                    'available': len(restaurants) > 0,
                    'restaurants_count': len(restaurants),
                    'source': 'swiggy_api',
                    'timestamp': datetime.utcnow().isoformat()
                }
        except Exception as e:
            print(f"Error checking Swiggy availability: {e}")
        
        # Fallback
        return {
            'available': True,
            'restaurants_count': 0,
            'source': 'fallback',
            'timestamp': datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def get_all_delivery_services(latitude: float, longitude: float, city: str) -> Dict:
        """Get availability for all delivery services"""
        return {
            'blinkit': DeliveryAvailabilityService.check_blinkit_availability(latitude, longitude, city),
            'zomato': DeliveryAvailabilityService.check_zomato_availability(latitude, longitude, city),
            'swiggy': DeliveryAvailabilityService.check_swiggy_availability(latitude, longitude, city)
        }


class HygieneIndicatorService:
    """Service to get restaurant hygiene indicators and ratings"""
    
    @staticmethod
    def get_restaurant_ratings(latitude: float, longitude: float, city: str, radius_km: float = 2.0) -> Dict:
        """
        Get restaurant ratings and hygiene indicators
        Uses Zomato API or Google Places API
        """
        try:
            # Option 1: Zomato API
            api_key = getattr(settings, 'ZOMATO_API_KEY', None)
            if api_key:
                url = "https://developers.zomato.com/api/v2.1/search"
                headers = {
                    'user-key': api_key,
                    'Accept': 'application/json'
                }
                params = {
                    'lat': latitude,
                    'lon': longitude,
                    'radius': int(radius_km * 1000),  # Convert to meters
                    'count': 100  # Get up to 100 restaurants
                }
                
                response = requests.get(url, headers=headers, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    restaurants = data.get('restaurants', [])
                    
                    if restaurants:
                        ratings = [r['restaurant'].get('user_rating', {}).get('aggregate_rating', 0) 
                                 for r in restaurants if r['restaurant'].get('user_rating', {}).get('aggregate_rating')]
                        ratings = [float(r) for r in ratings if r and r != '0']
                        
                        if ratings:
                            avg_rating = sum(ratings) / len(ratings)
                            highly_rated = len([r for r in ratings if r >= 4.0])
                            
                            return {
                                'avg_restaurant_rating': avg_rating,
                                'restaurants_count': len(restaurants),
                                'highly_rated_restaurants_count': highly_rated,
                                'source': 'zomato_api',
                                'timestamp': datetime.utcnow().isoformat()
                            }
            
            # Option 2: Google Places API (fallback)
            google_api_key = getattr(settings, 'GOOGLE_PLACES_API_KEY', None)
            if google_api_key:
                url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
                params = {
                    'location': f"{latitude},{longitude}",
                    'radius': int(radius_km * 1000),
                    'type': 'restaurant',
                    'key': google_api_key
                }
                
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    restaurants = data.get('results', [])
                    
                    if restaurants:
                        ratings = [r.get('rating', 0) for r in restaurants if r.get('rating')]
                        ratings = [float(r) for r in ratings if r and r > 0]
                        
                        if ratings:
                            avg_rating = sum(ratings) / len(ratings)
                            highly_rated = len([r for r in ratings if r >= 4.0])
                            
                            return {
                                'avg_restaurant_rating': avg_rating,
                                'restaurants_count': len(restaurants),
                                'highly_rated_restaurants_count': highly_rated,
                                'source': 'google_places',
                                'timestamp': datetime.utcnow().isoformat()
                            }
            
            # Fallback
            return {
                'avg_restaurant_rating': 3.5,
                'restaurants_count': 0,
                'highly_rated_restaurants_count': 0,
                'source': 'fallback',
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"Error fetching restaurant ratings: {e}")
            return {
                'avg_restaurant_rating': 3.5,
                'restaurants_count': 0,
                'highly_rated_restaurants_count': 0,
                'source': 'error',
                'timestamp': datetime.utcnow().isoformat()
            }


class GroceryStoresService:
    """Service to find nearby grocery stores using Google Places API"""
    
    @staticmethod
    def get_nearby_grocery_stores(latitude: float, longitude: float, city: str, radius_km: float = 2.0) -> Dict:
        """
        Get nearby grocery stores using Google Places API
        """
        try:
            google_api_key = getattr(settings, 'GOOGLE_PLACES_API_KEY', None)
            if google_api_key:
                url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
                
                # Search for grocery stores and supermarkets
                grocery_types = ['supermarket', 'grocery_or_supermarket', 'store']
                all_stores = []
                
                for place_type in grocery_types:
                    try:
                        params = {
                            'location': f"{latitude},{longitude}",
                            'radius': int(radius_km * 1000),
                            'type': place_type,
                            'key': google_api_key
                        }
                        
                        response = requests.get(url, params=params, timeout=10)
                        if response.status_code == 200:
                            data = response.json()
                            results = data.get('results', [])
                            all_stores.extend(results)
                        time.sleep(0.1)
                    except Exception as e:
                        print(f"Error fetching {place_type}: {e}")
                
                # Remove duplicates by place_id
                unique_stores = {}
                for store in all_stores:
                    place_id = store.get('place_id')
                    if place_id and place_id not in unique_stores:
                        unique_stores[place_id] = store
                
                return {
                    'grocery_stores_count': len(unique_stores),
                    'stores': list(unique_stores.values())[:20],  # Limit to 20
                    'source': 'google_places',
                    'timestamp': datetime.utcnow().isoformat()
                }
        except Exception as e:
            print(f"Error fetching grocery stores: {e}")
        
        return {
            'grocery_stores_count': 0,
            'stores': [],
            'source': 'fallback',
            'timestamp': datetime.utcnow().isoformat()
        }


class AmenitiesService:
    """Service to find nearby amenities and services"""
    
    @staticmethod
    def get_nearby_amenities(latitude: float, longitude: float, city: str, radius_km: float = 2.0) -> Dict:
        """
        Get nearby amenities using Google Places API or OpenStreetMap
        """
        amenities = {
            'hospitals_count': 0,
            'schools_count': 0,
            'parks_count': 0,
            'shopping_malls_count': 0,
            'metro_stations_count': 0,
            'bus_stops_count': 0,
            'source': 'fallback',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        try:
            # Use Google Places API if available
            google_api_key = getattr(settings, 'GOOGLE_PLACES_API_KEY', None)
            if google_api_key:
                place_types = {
                    'hospitals_count': 'hospital',
                    'schools_count': 'school',
                    'parks_count': 'park',
                    'shopping_malls_count': 'shopping_mall',
                    'metro_stations_count': 'subway_station',
                    'bus_stops_count': 'bus_station'
                }
                
                for count_key, place_type in place_types.items():
                    try:
                        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
                        params = {
                            'location': f"{latitude},{longitude}",
                            'radius': int(radius_km * 1000),
                            'type': place_type,
                            'key': google_api_key
                        }
                        
                        response = requests.get(url, params=params, timeout=10)
                        if response.status_code == 200:
                            data = response.json()
                            amenities[count_key] = len(data.get('results', []))
                        
                        time.sleep(0.1)  # Rate limiting
                    except Exception as e:
                        print(f"Error fetching {place_type}: {e}")
                
                amenities['source'] = 'google_places'
                amenities['timestamp'] = datetime.utcnow().isoformat()
                return amenities
            
            # Fallback: Use Overpass API (OpenStreetMap) - free, no key required
            overpass_url = "https://overpass-api.de/api/interpreter"
            
            # Query for hospitals
            try:
                query = f"""
                [out:json][timeout:25];
                (
                  node["amenity"="hospital"](around:{int(radius_km * 1000)},{latitude},{longitude});
                  way["amenity"="hospital"](around:{int(radius_km * 1000)},{latitude},{longitude});
                );
                out count;
                """
                response = requests.post(overpass_url, data=query, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    amenities['hospitals_count'] = len(data.get('elements', []))
            except Exception as e:
                print(f"Error fetching hospitals from OSM: {e}")
            
            # Query for schools
            try:
                query = f"""
                [out:json][timeout:25];
                (
                  node["amenity"="school"](around:{int(radius_km * 1000)},{latitude},{longitude});
                  way["amenity"="school"](around:{int(radius_km * 1000)},{latitude},{longitude});
                );
                out count;
                """
                response = requests.post(overpass_url, data=query, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    amenities['schools_count'] = len(data.get('elements', []))
            except Exception as e:
                print(f"Error fetching schools from OSM: {e}")
            
            # Query for parks
            try:
                query = f"""
                [out:json][timeout:25];
                (
                  node["leisure"="park"](around:{int(radius_km * 1000)},{latitude},{longitude});
                  way["leisure"="park"](around:{int(radius_km * 1000)},{latitude},{longitude});
                );
                out count;
                """
                response = requests.post(overpass_url, data=query, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    amenities['parks_count'] = len(data.get('elements', []))
            except Exception as e:
                print(f"Error fetching parks from OSM: {e}")
            
            amenities['source'] = 'openstreetmap'
            amenities['timestamp'] = datetime.utcnow().isoformat()
            
        except Exception as e:
            print(f"Error fetching amenities: {e}")
        
        return amenities

