"""
Recommendation service that compares neighborhoods based on user parameters
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from math import sqrt
from app.models.neighborhood import NeighborhoodData
from app.models.geospatial import Locality
from app.services.neighborhood_service import NeighborhoodService

class RecommendationService:
    """Service to recommend neighborhoods based on user criteria"""
    
    @staticmethod
    def recommend_neighborhoods(
        db: Session,
        city: str,
        number_of_people: int,
        max_travel_distance_km: float,
        budget: float,
        weights: Optional[Dict[str, float]] = None,
        property_type: str = "2BHK"
    ) -> List[Dict]:
        """
        Recommend neighborhoods based on user parameters
        
        Args:
            city: City name
            number_of_people: Number of people in household
            max_travel_distance_km: Maximum travel distance preference
            budget: Monthly budget
            weights: Optional weights for different factors (defaults to equal weights)
            property_type: Property type (1BHK, 2BHK, 3BHK)
        
        Returns:
            List of recommended neighborhoods with scores
        """
        # Default weights if not provided
        if weights is None:
            weights = {
                'rent': 0.25,
                'grocery_cost': 0.15,
                'delivery_availability': 0.10,
                'aqi': 0.15,
                'hygiene': 0.10,
                'amenities': 0.15,
                'connectivity': 0.10
            }
        
        # Normalize weights to sum to 1.0
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: v / total_weight for k, v in weights.items()}
        
        # Get all neighborhoods for the city
        neighborhoods = NeighborhoodService.get_all_neighborhoods_by_city(db, city)
        
        if not neighborhoods:
            return []
        
        # Get locality stats (which contain scraped data) for all localities
        from app.models.geospatial import LocalityStats
        locality_stats_map = {}
        for n in neighborhoods:
            if n.locality_id not in locality_stats_map:
                stats = db.query(LocalityStats).filter(
                    LocalityStats.locality_id == n.locality_id
                ).first()
                locality_stats_map[n.locality_id] = stats
        
        # Get the appropriate rent field based on property type
        rent_field_map = {
            '1BHK': 'avg_rent_1bhk',
            '2BHK': 'avg_rent_2bhk',
            '3BHK': 'avg_rent_3bhk'
        }
        rent_field = rent_field_map.get(property_type, 'avg_rent_2bhk')
        
        # Extract all values for normalization
        # Prefer locality_stats (scraped data) over neighborhood_data
        city_grocery_defaults = {
            "Bhopal": 4500,
            "Indore": 5000,
            "Gwalior": 4200,
            "Jabalpur": 4300,
            "Ujjain": 4000,
            "Sagar": 3800,
            "Ratlam": 3900,
        }
        
        rent_values = []
        grocery_values = []
        for n in neighborhoods:
            stats = locality_stats_map.get(n.locality_id)
            # Prefer scraped data from locality_stats
            if stats:
                rent_val = getattr(stats, rent_field) or getattr(n, rent_field) or 0
                grocery_val = stats.avg_grocery_cost_monthly or n.avg_grocery_cost_monthly or city_grocery_defaults.get(n.city, 4500)
            else:
                rent_val = getattr(n, rent_field) or 0
                grocery_val = n.avg_grocery_cost_monthly or city_grocery_defaults.get(n.city, 4500)
            rent_values.append(rent_val)
            grocery_values.append(grocery_val)
        aqi_values = [n.aqi_value or 50 for n in neighborhoods]
        hygiene_values = [n.avg_restaurant_rating or 0 for n in neighborhoods]
        amenities_scores = [n.amenities_score or 0 for n in neighborhoods]
        connectivity_scores = [n.connectivity_score or 0 for n in neighborhoods]
        
        # Calculate delivery availability scores
        delivery_scores = []
        for n in neighborhoods:
            delivery_count = sum([
                n.blinkit_available,
                n.zomato_available,
                n.swiggy_available
            ])
            delivery_scores.append(delivery_count)
        
        # Normalize all metrics (0-1 scale)
        normalized_data = []
        
        # Safety check: ensure we have values to normalize
        if not rent_values or not grocery_values or not aqi_values:
            return []
        
        for i, neighborhood in enumerate(neighborhoods):
            # Use scraped data from locality_stats if available
            stats = locality_stats_map.get(neighborhood.locality_id)
            if stats:
                rent = getattr(stats, rent_field) or getattr(neighborhood, rent_field) or 0
                grocery = stats.avg_grocery_cost_monthly or neighborhood.avg_grocery_cost_monthly or city_grocery_defaults.get(neighborhood.city, 4500)
            else:
                rent = getattr(neighborhood, rent_field) or 0
                grocery = neighborhood.avg_grocery_cost_monthly or city_grocery_defaults.get(neighborhood.city, 4500)
            aqi = neighborhood.aqi_value or 50
            hygiene = neighborhood.avg_restaurant_rating or 0
            amenities = neighborhood.amenities_score or 0
            connectivity = neighborhood.connectivity_score or 0
            delivery = delivery_scores[i]
            
            # Normalize rent (lower is better, so invert)
            rent_min, rent_max = min(rent_values), max(rent_values)
            if rent_max > rent_min:
                rent_normalized = 1.0 - ((rent - rent_min) / (rent_max - rent_min))
            else:
                rent_normalized = 1.0 if rent <= budget else 0.0
            
            # Normalize grocery cost (lower is better)
            grocery_min, grocery_max = min(grocery_values), max(grocery_values)
            if grocery_max > grocery_min:
                grocery_normalized = 1.0 - ((grocery - grocery_min) / (grocery_max - grocery_min))
            else:
                grocery_normalized = 1.0
            
            # Normalize AQI (lower is better, good AQI = higher score)
            aqi_min, aqi_max = min(aqi_values), max(aqi_values)
            if aqi_max > aqi_min:
                aqi_normalized = 1.0 - ((aqi - aqi_min) / (aqi_max - aqi_min))
            else:
                aqi_normalized = 1.0 if aqi <= 50 else 0.5
            
            # Normalize hygiene (higher is better)
            hygiene_positive = [h for h in hygiene_values if h > 0]
            if hygiene_positive:
                hygiene_min, hygiene_max = min(hygiene_positive), max(hygiene_values)
                if hygiene_max > hygiene_min:
                    hygiene_normalized = (hygiene - hygiene_min) / (hygiene_max - hygiene_min) if hygiene > 0 else 0.0
                else:
                    hygiene_normalized = 1.0 if hygiene > 0 else 0.0
            else:
                hygiene_normalized = 0.0
            
            # Normalize amenities (0-10 scale, already normalized)
            amenities_normalized = amenities / 10.0 if amenities > 0 else 0.0
            
            # Normalize connectivity (0-10 scale, already normalized)
            connectivity_normalized = connectivity / 10.0 if connectivity > 0 else 0.0
            
            # Normalize delivery (0-3 scale)
            delivery_normalized = delivery / 3.0 if delivery > 0 else 0.0
            
            # Calculate weighted score
            score = (
                rent_normalized * weights.get('rent', 0.25) +
                grocery_normalized * weights.get('grocery_cost', 0.15) +
                delivery_normalized * weights.get('delivery_availability', 0.10) +
                aqi_normalized * weights.get('aqi', 0.15) +
                hygiene_normalized * weights.get('hygiene', 0.10) +
                amenities_normalized * weights.get('amenities', 0.15) +
                connectivity_normalized * weights.get('connectivity', 0.10)
            )
            
            # Apply budget filter
            total_monthly_cost = rent + (grocery * number_of_people)
            if total_monthly_cost > budget:
                # Penalize if over budget
                score *= 0.5
            
            # Get locality info
            locality = db.query(Locality).filter(
                Locality.id == neighborhood.locality_id
            ).first()
            
            normalized_data.append({
                'neighborhood_id': neighborhood.id,
                'locality_id': neighborhood.locality_id,
                'locality_name': locality.name if locality else 'Unknown',
                'city': neighborhood.city,
                'score': score,
                'rent': rent,
                'grocery_cost': grocery if grocery > 0 else None,  # Return None if 0
                'total_monthly_cost': total_monthly_cost,
                'aqi': aqi,
                'aqi_category': neighborhood.aqi_category,
                'hygiene_rating': hygiene if hygiene > 0 else None,
                'amenities_score': amenities,
                'connectivity_score': connectivity,
                'delivery_services': {
                    'blinkit': neighborhood.blinkit_available,
                    'zomato': neighborhood.zomato_available,
                    'swiggy': neighborhood.swiggy_available
                },
                'amenities': {
                    'hospitals': neighborhood.hospitals_count or 0,
                    'schools': neighborhood.schools_count or 0,
                    'parks': neighborhood.parks_count or 0,
                    'malls': neighborhood.shopping_malls_count or 0
                },
                # Add food and restaurant data
                'restaurants_count': neighborhood.restaurants_count or 0,
                'highly_rated_restaurants': neighborhood.highly_rated_restaurants_count or 0,
                'avg_restaurant_rating': neighborhood.avg_restaurant_rating if neighborhood.avg_restaurant_rating else None,
                'grocery_stores_count': neighborhood.grocery_stores_count or 0,
                'latitude': locality.latitude if locality else None,
                'longitude': locality.longitude if locality else None,
                'normalized_scores': {
                    'rent': rent_normalized,
                    'grocery': grocery_normalized,
                    'aqi': aqi_normalized,
                    'hygiene': hygiene_normalized,
                    'amenities': amenities_normalized,
                    'connectivity': connectivity_normalized,
                    'delivery': delivery_normalized
                }
            })
        
        # Sort by score (descending)
        normalized_data.sort(key=lambda x: x['score'], reverse=True)
        
        return normalized_data
    
    @staticmethod
    def get_top_recommendations(
        db: Session,
        city: str,
        number_of_people: int,
        max_travel_distance_km: float,
        budget: float,
        weights: Optional[Dict[str, float]] = None,
        property_type: str = "2BHK",
        top_n: int = 10
    ) -> List[Dict]:
        """Get top N recommendations"""
        recommendations = RecommendationService.recommend_neighborhoods(
            db=db,
            city=city,
            number_of_people=number_of_people,
            max_travel_distance_km=max_travel_distance_km,
            budget=budget,
            weights=weights,
            property_type=property_type
        )
        
        return recommendations[:top_n]

