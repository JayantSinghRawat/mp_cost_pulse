from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import requests
import os

default_args = {
    'owner': 'mpcostpulse',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def scrape_rents(**context):
    """Scrape rent listings from NoBroker and OLX"""
    api_url = os.getenv('API_BASE_URL', 'http://backend:8000/api/v1')
    localities = ['Arera Colony', 'New Market', 'MP Nagar', 'Hoshangabad Road']
    
    for locality in localities:
        try:
            # Trigger NoBroker scraping
            requests.post(f"{api_url}/rents/scrape/nobroker", 
                         params={"locality": locality, "city": "Bhopal"},
                         timeout=30)
            # Trigger OLX scraping
            requests.post(f"{api_url}/rents/scrape/olx",
                         params={"locality": locality, "city": "Bhopal"},
                         timeout=30)
        except Exception as e:
            print(f"Error scraping rents for {locality}: {e}")

def fetch_groceries(**context):
    """Fetch grocery data from BigBasket and Blinkit"""
    api_url = os.getenv('API_BASE_URL', 'http://backend:8000/api/v1')
    localities = ['Arera Colony', 'New Market', 'MP Nagar', 'Hoshangabad Road']
    
    for locality in localities:
        try:
            requests.post(f"{api_url}/groceries/fetch/bigbasket",
                         params={"locality": locality, "city": "Bhopal"},
                         timeout=30)
            requests.post(f"{api_url}/groceries/fetch/blinkit",
                         params={"locality": locality, "city": "Bhopal"},
                         timeout=30)
        except Exception as e:
            print(f"Error fetching groceries for {locality}: {e}")

def fetch_transport(**context):
    """Fetch transport fares from BCLL"""
    api_url = os.getenv('API_BASE_URL', 'http://backend:8000/api/v1')
    try:
        requests.post(f"{api_url}/transport/fetch/bcll", timeout=30)
    except Exception as e:
        print(f"Error fetching transport data: {e}")

def fetch_inflation(**context):
    """Fetch inflation data from RBI and MP Govt"""
    api_url = os.getenv('API_BASE_URL', 'http://backend:8000/api/v1')
    try:
        requests.post(f"{api_url}/inflation/fetch/rbi", timeout=30)
        requests.post(f"{api_url}/inflation/fetch/mp-govt", timeout=30)
    except Exception as e:
        print(f"Error fetching inflation data: {e}")

def update_locality_stats(**context):
    """Update statistics for all localities"""
    api_url = os.getenv('API_BASE_URL', 'http://backend:8000/api/v1')
    try:
        # Get all localities
        response = requests.get(f"{api_url}/geospatial/localities", timeout=30)
        localities = response.json()
        
        for locality in localities:
            try:
                requests.post(f"{api_url}/geospatial/localities/{locality['id']}/update-stats",
                             timeout=30)
            except Exception as e:
                print(f"Error updating stats for locality {locality['id']}: {e}")
    except Exception as e:
        print(f"Error updating locality stats: {e}")

def aggregate_neighborhood_data(**context):
    """Aggregate neighborhood data (AQI, delivery, hygiene, amenities) for all cities"""
    api_url = os.getenv('API_BASE_URL', 'http://backend:8000/api/v1')
    cities = ['Bhopal']  # Can be extended to multiple cities
    
    for city in cities:
        try:
            print(f"Aggregating neighborhood data for {city}...")
            response = requests.post(
                f"{api_url}/recommendations/refresh/{city}",
                timeout=300  # 5 minutes timeout for aggregation
            )
            if response.status_code == 200:
                result = response.json()
                print(f"Successfully aggregated {result.get('refreshed_count', 0)} neighborhoods in {city}")
                if result.get('errors'):
                    print(f"Errors: {result.get('errors')}")
            else:
                print(f"Error aggregating data for {city}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error aggregating neighborhood data for {city}: {e}")

with DAG(
    'mpcostpulse_scraping',
    default_args=default_args,
    description='Scrape and update cost of living data',
    schedule_interval=timedelta(hours=12),  # Run every 12 hours (can be adjusted to 6-24 hours)
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['scraping', 'data-update'],
) as dag:

    scrape_rents_task = PythonOperator(
        task_id='scrape_rents',
        python_callable=scrape_rents,
    )

    fetch_groceries_task = PythonOperator(
        task_id='fetch_groceries',
        python_callable=fetch_groceries,
    )

    fetch_transport_task = PythonOperator(
        task_id='fetch_transport',
        python_callable=fetch_transport,
    )

    fetch_inflation_task = PythonOperator(
        task_id='fetch_inflation',
        python_callable=fetch_inflation,
    )

    update_stats_task = PythonOperator(
        task_id='update_locality_stats',
        python_callable=update_locality_stats,
    )

    aggregate_neighborhoods_task = PythonOperator(
        task_id='aggregate_neighborhood_data',
        python_callable=aggregate_neighborhood_data,
    )

    # Set task dependencies
    # First scrape basic data, then aggregate comprehensive neighborhood data
    [scrape_rents_task, fetch_groceries_task, fetch_transport_task, fetch_inflation_task] >> update_stats_task
    update_stats_task >> aggregate_neighborhoods_task

