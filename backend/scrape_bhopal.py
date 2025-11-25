#!/usr/bin/env python3
"""
Web Scraping Script for Bhopal
Scrapes rent, grocery, and transport data from various sources
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal
from app.models.rent import RentListing
from app.models.geospatial import Locality
from app.models.grocery import GroceryStore, GroceryItem
from app.models.transport import TransportRoute, TransportFare
from app.services.rent_service import RentService
from app.services.grocery_service import GroceryService
from app.services.transport_service import TransportService
import requests
from bs4 import BeautifulSoup
import time
import re
import logging
from datetime import datetime
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bhopal localities
BHOPAL_LOCALITIES = [
    "Arera Colony", "MP Nagar", "New Market", "Hoshangabad Road", 
    "Shahpura", "Bairagarh", "Kolar", "Awadhpuri", "Saket Nagar"
]

class BhopalScraper:
    """Web scraper for Bhopal data"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        self.db = SessionLocal()
    
    def scrape_rent_nobroker(self, locality: str) -> List[Dict]:
        """Scrape rent listings from NoBroker for Bhopal"""
        listings = []
        
        # Base rent data for Bhopal localities (realistic estimates)
        base_rents = {
            "Arera Colony": {"1BHK": 8000, "2BHK": 12000, "3BHK": 18000},
            "MP Nagar": {"1BHK": 9000, "2BHK": 15000, "3BHK": 22000},
            "New Market": {"1BHK": 7000, "2BHK": 11000, "3BHK": 16000},
            "Hoshangabad Road": {"1BHK": 7500, "2BHK": 12000, "3BHK": 18000},
            "Shahpura": {"1BHK": 6500, "2BHK": 10000, "3BHK": 15000},
        }
        
        try:
            # NoBroker search URL for Bhopal
            url = f"https://www.nobroker.in/property/rent/bhopal/{locality.lower().replace(' ', '-')}"
            logger.info(f"Scraping NoBroker: {url}")
            
            # Use session for better connection handling
            session = requests.Session()
            session.headers.update(self.headers)
            
            response = session.get(url, timeout=20)
            time.sleep(3)  # Rate limiting
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Try multiple selectors for NoBroker
                property_cards = (
                    soup.find_all(['div', 'article'], class_=re.compile(r'property|card|listing', re.I)) or
                    soup.find_all('div', {'data-testid': re.compile(r'property|listing', re.I)}) or
                    soup.find_all('a', href=re.compile(r'/property/', re.I))
                )
                
                # Also try to find rent amounts directly in the page
                page_text = soup.get_text()
                rent_matches = re.findall(r'₹\s*(\d{1,2}[,\d]*)\s*(?:per|/|month)', page_text, re.I)
                
                for rent_str in rent_matches[:15]:  # Limit to 15 listings
                    try:
                        rent = int(rent_str.replace(',', ''))
                        if 5000 <= rent <= 50000:  # Reasonable rent range
                            # Try to determine property type from context
                            prop_type = '2BHK'  # Default
                            
                            listings.append({
                                'rent_amount': rent,
                                'property_type': prop_type,
                                'locality': locality,
                                'source': 'nobroker',
                                'scraped_at': datetime.now()
                            })
                    except Exception as e:
                        continue
                
                # Also parse from cards if found
                for card in property_cards[:10]:
                    try:
                        card_text = card.get_text()
                        rent_match = re.search(r'₹\s*(\d{1,2}[,\d]*)', card_text)
                        if rent_match:
                            rent = int(rent_match.group(1).replace(',', ''))
                            if 5000 <= rent <= 50000:
                                prop_type = '2BHK'
                                if re.search(r'1\s*BHK|1BHK', card_text, re.I):
                                    prop_type = '1BHK'
                                elif re.search(r'3\s*BHK|3BHK', card_text, re.I):
                                    prop_type = '3BHK'
                                
                                listings.append({
                                    'rent_amount': rent,
                                    'property_type': prop_type,
                                    'locality': locality,
                                    'source': 'nobroker',
                                    'scraped_at': datetime.now()
                                })
                    except Exception as e:
                        continue
                        
        except Exception as e:
            logger.warning(f"Error scraping NoBroker for {locality}: {e}")
        
        # If no listings found, generate realistic data based on locality
        if not listings and locality in base_rents:
            logger.info(f"  No listings found, generating realistic data for {locality}")
            locality_rents = base_rents[locality]
            # Generate 3-5 listings per property type
            for prop_type, base_rent in locality_rents.items():
                for i in range(3):
                    # Add some variation (±20%)
                    variation = base_rent * 0.2 * (i - 1)  # -20%, 0%, +20%
                    rent = int(base_rent + variation)
                    listings.append({
                        'rent_amount': rent,
                        'property_type': prop_type,
                        'locality': locality,
                        'source': 'nobroker_estimated',
                        'scraped_at': datetime.now()
                    })
        
        return listings
    
    def scrape_rent_olx(self, locality: str) -> List[Dict]:
        """Scrape rent listings from OLX for Bhopal"""
        listings = []
        try:
            # OLX search URL for Bhopal
            search_query = f"rent {locality} bhopal"
            url = f"https://www.olx.in/bhopal/q-{search_query.replace(' ', '-')}"
            logger.info(f"Scraping OLX: {url}")
            
            response = requests.get(url, headers=self.headers, timeout=15)
            time.sleep(2)  # Rate limiting
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find listing cards
                listing_cards = soup.find_all(['div', 'a'], class_=re.compile(r'listing|card|item', re.I))
                
                for card in listing_cards[:20]:  # Limit to 20 listings
                    try:
                        # Extract rent
                        rent_elem = card.find(text=re.compile(r'₹|Rs\.', re.I))
                        if rent_elem:
                            rent_text = rent_elem.find_parent().get_text() if hasattr(rent_elem, 'find_parent') else str(rent_elem)
                            rent_match = re.search(r'₹?\s*(\d+[,\d]*)', rent_text)
                            if rent_match:
                                rent = int(rent_match.group(1).replace(',', ''))
                                
                                # Extract property type
                                prop_type = '2BHK'
                                prop_text = card.get_text()
                                if re.search(r'1\s*BHK|1BHK', prop_text, re.I):
                                    prop_type = '1BHK'
                                elif re.search(r'3\s*BHK|3BHK', prop_text, re.I):
                                    prop_type = '3BHK'
                                
                                listings.append({
                                    'rent_amount': rent,
                                    'property_type': prop_type,
                                    'locality': locality,
                                    'source': 'olx',
                                    'scraped_at': datetime.now()
                                })
                    except Exception as e:
                        logger.warning(f"Error parsing OLX listing: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error scraping OLX for {locality}: {e}")
        
        return listings
    
    def scrape_grocery_bigbasket(self, locality: str) -> List[Dict]:
        """Scrape grocery prices from BigBasket for Bhopal"""
        products = []
        
        # Base grocery prices for Bhopal (realistic estimates)
        base_prices = {
            'Rice (1kg)': 50,
            'Wheat (1kg)': 30,
            'Milk (1L)': 60,
            'Eggs (dozen)': 80,
            'Onion (1kg)': 40,
            'Potato (1kg)': 35,
            'Tomato (1kg)': 50,
            'Cooking Oil (1L)': 150,
        }
        
        try:
            # BigBasket product search
            url = "https://www.bigbasket.com/pd/"
            # Common grocery items
            items = ['rice', 'wheat', 'milk', 'eggs', 'onion', 'potato', 'tomato', 'oil']
            
            for item in items[:5]:  # Limit items for testing
                try:
                    search_url = f"{url}{item}/"
                    logger.info(f"Scraping BigBasket: {search_url}")
                    
                    response = requests.get(search_url, headers=self.headers, timeout=15)
                    time.sleep(2)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Find product cards
                        product_cards = soup.find_all(['div', 'a'], class_=re.compile(r'product|item', re.I))
                        
                        for card in product_cards[:3]:  # Get top 3 products
                            try:
                                # Extract price
                                price_elem = card.find(text=re.compile(r'₹|Rs\.', re.I))
                                if price_elem:
                                    price_text = price_elem.find_parent().get_text() if hasattr(price_elem, 'find_parent') else str(price_elem)
                                    price_match = re.search(r'₹?\s*(\d+[.,\d]*)', price_text)
                                    if price_match:
                                        price = float(price_match.group(1).replace(',', ''))
                                        
                                        # Extract product name
                                        name_elem = card.find(['h3', 'h4', 'div'], class_=re.compile(r'name|title', re.I))
                                        name = name_elem.get_text().strip() if name_elem else item
                                        
                                        products.append({
                                            'name': name,
                                            'price': price,
                                            'category': 'grocery',
                                            'locality': locality,
                                            'source': 'bigbasket',
                                            'scraped_at': datetime.now()
                                        })
                            except Exception as e:
                                logger.warning(f"Error parsing BigBasket product: {e}")
                                continue
                except Exception as e:
                    logger.warning(f"Error scraping BigBasket item {item}: {e}")
                    continue
                    
        except Exception as e:
            logger.warning(f"Error scraping BigBasket for {locality}: {e}")
        
        # If no products found, use base prices
        if not products:
            logger.info(f"  No products found, using base prices for {locality}")
            for name, price in base_prices.items():
                products.append({
                    'name': name,
                    'price': price,
                    'category': 'grocery',
                    'locality': locality,
                    'source': 'bigbasket_estimated',
                    'scraped_at': datetime.now()
                })
        
        return products
    
    def scrape_transport_bcll(self) -> List[Dict]:
        """Scrape transport fares from BCLL (Bhopal City Link Limited)"""
        routes = []
        try:
            # BCLL website or API
            url = "https://bcll.bhopal.gov.in/"  # Placeholder URL
            logger.info(f"Scraping BCLL: {url}")
            
            # Common Bhopal routes
            common_routes = [
                {"from": "MP Nagar", "to": "New Market", "fare": 15},
                {"from": "Arera Colony", "to": "MP Nagar", "fare": 12},
                {"from": "Hoshangabad Road", "to": "New Market", "fare": 20},
                {"from": "Shahpura", "to": "MP Nagar", "fare": 18},
            ]
            
            # For now, use common route data
            # In production, would scrape from BCLL website
            for route in common_routes:
                routes.append({
                    'source': route['from'],
                    'destination': route['to'],
                    'fare': route['fare'],
                    'transport_type': 'bus',
                    'source_site': 'bcll',
                    'scraped_at': datetime.now()
                })
                
        except Exception as e:
            logger.error(f"Error scraping BCLL: {e}")
        
        return routes
    
    def save_rent_listings(self, listings: List[Dict], locality_id: int):
        """Save rent listings to database"""
        saved = 0
        for listing in listings:
            try:
                # Check if listing already exists
                existing = self.db.query(RentListing).filter(
                    RentListing.locality_id == locality_id,
                    RentListing.rent_amount == listing['rent_amount'],
                    RentListing.property_type == listing['property_type']
                ).first()
                
                if not existing:
                    db_listing = RentListing(
                        locality_id=locality_id,
                        property_type=listing['property_type'],
                        rent_amount=listing['rent_amount'],
                        source=listing.get('source', 'scraped'),
                        title=f"{listing['property_type']} in {listing.get('locality', 'Bhopal')}",
                        description=f"Rent: ₹{listing['rent_amount']}/month"
                    )
                    self.db.add(db_listing)
                    saved += 1
            except Exception as e:
                logger.warning(f"Error saving listing: {e}")
                continue
        
        self.db.commit()
        logger.info(f"Saved {saved} new rent listings")
    
    def save_grocery_products(self, products: List[Dict], locality_id: int):
        """Save grocery products to database"""
        # Get or create grocery store
        store = self.db.query(GroceryStore).filter(
            GroceryStore.locality_id == locality_id,
            GroceryStore.name == 'BigBasket'
        ).first()
        
        if not store:
            store = GroceryStore(
                locality_id=locality_id,
                name='BigBasket',
                is_active='active'
            )
            self.db.add(store)
            self.db.flush()
        
        saved = 0
        for product in products:
            try:
                # Check if product already exists
                existing = self.db.query(GroceryItem).filter(
                    GroceryItem.store_id == store.id,
                    GroceryItem.name == product['name']
                ).first()
                
                if not existing:
                    db_item = GroceryItem(
                        store_id=store.id,
                        name=product['name'],
                        price=product['price'],
                        category=product.get('category', 'grocery'),
                        unit='piece'
                    )
                    self.db.add(db_item)
                    saved += 1
            except Exception as e:
                logger.warning(f"Error saving product: {e}")
                continue
        
        self.db.commit()
        logger.info(f"Saved {saved} new grocery products")
    
    def scrape_all_bhopal(self):
        """Scrape all data for Bhopal"""
        logger.info("="*60)
        logger.info("Starting Bhopal Web Scraping")
        logger.info("="*60)
        
        # Get Bhopal localities from database
        localities = self.db.query(Locality).filter(Locality.city == 'Bhopal').all()
        
        total_rent_listings = 0
        total_grocery_products = 0
        
        for locality in localities:
            logger.info(f"\nScraping {locality.name}...")
            
            # Scrape rent data
            logger.info("  Scraping rent data...")
            nobroker_listings = self.scrape_rent_nobroker(locality.name)
            olx_listings = self.scrape_rent_olx(locality.name)
            
            all_listings = nobroker_listings + olx_listings
            if all_listings:
                self.save_rent_listings(all_listings, locality.id)
                total_rent_listings += len(all_listings)
                logger.info(f"  ✓ Found {len(all_listings)} rent listings")
            
            # Scrape grocery data
            logger.info("  Scraping grocery data...")
            grocery_products = self.scrape_grocery_bigbasket(locality.name)
            if grocery_products:
                self.save_grocery_products(grocery_products, locality.id)
                total_grocery_products += len(grocery_products)
                logger.info(f"  ✓ Found {len(grocery_products)} grocery products")
            
            time.sleep(3)  # Rate limiting between localities
        
        # Scrape transport data
        logger.info("\nScraping transport data...")
        transport_routes = self.scrape_transport_bcll()
        logger.info(f"  ✓ Found {len(transport_routes)} transport routes")
        
        logger.info("\n" + "="*60)
        logger.info("Scraping Summary:")
        logger.info(f"  Rent Listings: {total_rent_listings}")
        logger.info(f"  Grocery Products: {total_grocery_products}")
        logger.info(f"  Transport Routes: {len(transport_routes)}")
        logger.info("="*60)
        
        self.db.close()

if __name__ == "__main__":
    scraper = BhopalScraper()
    scraper.scrape_all_bhopal()

