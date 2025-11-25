# Complete File Structure Documentation

This document explains every file and directory in the MP Cost Pulse project, from the root level down to individual implementation files.

---

## Root Directory Files

### Configuration Files

**`docker-compose.yml`**
- Main orchestration file for all Docker containers
- Defines services: PostgreSQL, Backend, Frontend, Nginx, ML Worker, Airflow
- Configures networking, volumes, environment variables, and dependencies
- Sets up health checks and restart policies
- Maps ports and volumes for development and production

### Documentation Files

**`README.md`**
- Main project documentation
- Overview of features, tech stack, installation instructions
- API endpoint documentation
- Quick start guide

**`PROJECT_OVERVIEW.md`**
- High-level project explanation (500 words)
- Business value and use cases
- Target audience and impact

**`SUMMARY.md`**
- Implementation status summary
- List of completed features
- Quick reference for what's been built

**`QUICKSTART.md`**
- Step-by-step setup instructions
- Commands to get the project running quickly
- Common troubleshooting tips

**`PRODUCTION.md`**
- Production deployment guide
- Security considerations
- Scaling strategies
- Performance optimization tips

**`TESTING.md`**
- Testing strategies and approaches
- How to run tests
- Test coverage information

**`SCRAPE_BHOPAL.md`**
- Documentation for Bhopal data scraping
- How to use scraping endpoints
- Data sources and verification

**`SCRAPED_DATA_INTEGRATION.md`**
- How scraped data integrates into the system
- Data flow from scraping to recommendations
- Update processes

**`DATA_SOURCES.md`**
- List of all external data sources
- API keys and authentication requirements
- Data source reliability and update frequency

**`GOOGLE_PLACES_SETUP.md`**
- Instructions for setting up Google Places API
- API key configuration
- Usage examples

**`SETUP_GOOGLE_MAPS.md`**
- Mapbox/Google Maps integration guide
- API key setup for mapping features

**`HOW_TO_ACCESS.md`**
- URLs and ports for accessing different services
- Default credentials
- Service endpoints

**`ACCESS_GUIDE.md`**
- User access guide
- How to navigate the application
- Feature explanations

**`VIEW_SCRAPED_DATA.md`**
- How to view and verify scraped data
- Database queries for data inspection

**`QUICK_START_GOOGLE_MAPS.txt`**
- Quick reference for Google Maps setup
- Essential configuration steps

**`QUICK_TEST.md`**
- Quick testing guide
- Sample test commands

### Script Files

**`test_all.sh`**
- Shell script to run all tests
- Automated testing suite

**`test_cost_prediction.sh`**
- Script to test cost prediction functionality
- ML model testing

**`test_frontend.sh`**
- Frontend testing script
- UI component tests

---

## Backend Directory (`/backend`)

### Main Application Files

**`main.py`**
- FastAPI application entry point
- Creates FastAPI app instance
- Configures CORS middleware
- Includes API router
- Defines root and health check endpoints
- This is where the server starts

**`requirements.txt`**
- Python package dependencies
- Lists all required libraries (FastAPI, SQLAlchemy, etc.)
- Version specifications for reproducibility

**`init_db.sql`**
- Database initialization script
- Creates PostGIS extension
- Sets up initial database structure
- Runs automatically on first container startup

### Docker Files

**`Dockerfile`**
- Development Docker image configuration
- Installs Python dependencies
- Sets up working directory
- Configures environment for development

**`Dockerfile.prod`**
- Production Docker image configuration
- Optimized build with multi-stage process
- Smaller image size
- Production-specific optimizations

### Utility Scripts

**`scrape_bhopal.py`**
- Web scraping script for Bhopal data
- Scrapes rent listings from NoBroker and OLX
- Fetches grocery prices from BigBasket
- Collects transport route data
- Saves data to database

**`seed_bhopal_localities.py`**
- Creates Bhopal locality entries in database
- Adds coordinates and initial statistics
- Seeds base data for Bhopal neighborhoods

**`seed_mp_cities.py`**
- Seeds localities for all MP cities (except Bhopal)
- Creates Indore, Gwalior, Jabalpur, Ujjain, Sagar, Ratlam
- Adds coordinates and default statistics
- Creates initial neighborhood data

**`create_bhopal_neighborhood_data.py`**
- Creates neighborhood_data entries for Bhopal
- Aggregates data from scraped listings
- Calculates averages and statistics
- Required for recommendations to work

**`create_missing_stats.py`**
- Utility to create missing locality statistics
- Fills gaps in data
- Calculates default values where needed

**`update_stats_from_scraped_data.py`**
- Updates locality statistics from scraped data
- Recalculates averages after new scraping
- Keeps statistics current

**`refresh_bhopal_places_data.py`**
- Refreshes Bhopal neighborhood data using Google Places API
- Updates restaurants, grocery stores, hospitals, schools
- Fetches real-time amenity data

**`refresh_all_neighborhoods.py`**
- Refreshes neighborhood data for all cities
- Batch processing utility
- Updates all localities at once

---

## Backend Application Structure (`/backend/app`)

### Core Module (`/backend/app/core`)

**`__init__.py`**
- Python package marker
- Makes core a Python module

**`config.py`**
- Application configuration settings
- Loads environment variables
- Defines database URLs, API keys, CORS settings
- Security settings (JWT, secrets)
- Email/SMTP configuration
- OTP settings
- Centralized configuration management

**`database.py`**
- Database connection setup
- Creates SQLAlchemy engine and session factory
- Defines database dependency injection
- Initializes database tables
- Database connection pooling

**`security.py`**
- Security utilities
- Password hashing (bcrypt)
- JWT token creation and validation
- Token expiration handling
- Authentication helpers

### Models (`/backend/app/models`)

Models define database table structures using SQLAlchemy ORM.

**`__init__.py`**
- Package initialization
- Exports all models

**`user.py`**
- User model for authentication
- Stores username, email, hashed password
- User profile information
- Relationships to other tables

**`geospatial.py`**
- Locality model (geographic areas)
- LocalityStats model (aggregated statistics)
- PostGIS geometry fields
- Coordinates and location data
- Relationships to rent, grocery, transport data

**`rent.py`**
- RentListing model
- Stores rental property information
- Property type, rent amount, locality
- Source tracking (NoBroker, OLX)
- Relationships to localities

**`grocery.py`**
- GroceryStore model (stores in localities)
- GroceryItem model (products with prices)
- Store location and availability
- Price tracking and categories

**`transport.py`**
- TransportRoute model (bus routes)
- TransportFare model (fare information)
- Route source and destination
- Fare amounts and transport types

**`inflation.py`**
- InflationData model
- Time series inflation data
- Category-based inflation rates
- Source tracking (RBI, MP Government)

**`neighborhood.py`**
- NeighborhoodData model
- Aggregated neighborhood information
- Rent averages, grocery costs, AQI
- Amenity counts (hospitals, schools, parks)
- Delivery service availability
- Calculated scores (safety, connectivity, amenities)

**`ml_models.py`**
- MLModelVersion model
- Tracks machine learning model versions
- Model metadata and performance metrics
- Model file paths and training dates

**`otp.py`**
- OTP model for email verification
- Stores OTP codes and expiration
- User session tokens

### Schemas (`/backend/app/schemas`)

Schemas define request/response data structures using Pydantic for validation.

**`__init__.py`**
- Package initialization

**`auth.py`**
- User registration schema
- Login request/response schemas
- Token response schemas
- OTP verification schemas

**`geospatial.py`**
- Locality request/response schemas
- Locality stats schemas
- Nearby search schemas
- Heatmap data schemas

**`rent.py`**
- Rent listing schemas
- Rent query parameters
- Average rent response schemas

**`grocery.py`**
- Grocery store schemas
- Grocery item schemas
- Monthly cost calculation schemas

**`transport.py`**
- Transport route schemas
- Fare information schemas
- Cost calculation schemas

**`inflation.py`**
- Inflation data schemas
- Time series schemas
- Category-based schemas

**`ml.py`**
- Cost prediction request/response schemas
- Rent classification schemas
- Model version schemas

**`recommendation.py`**
- Recommendation request schema (user preferences)
- Recommendation response schema (neighborhood data)
- Weight configuration schemas

### Services (`/backend/app/services`)

Services contain business logic and external API integrations.

**`__init__.py`**
- Package initialization

**`auth_service.py`**
- User authentication logic
- Password verification
- Token generation
- User registration validation

**`email_service.py`**
- Email sending functionality
- OTP email templates
- SMTP connection management
- Email delivery

**`rent_service.py`**
- Rent data operations
- Average rent calculations
- NoBroker scraping logic
- OLX scraping logic
- Rent listing aggregation

**`grocery_service.py`**
- Grocery store operations
- Product price calculations
- BigBasket API integration
- Blinkit API integration
- Monthly cost calculations

**`transport_service.py`**
- Transport route operations
- Fare calculations
- BCLL data fetching
- Monthly commute cost calculations

**`inflation_service.py`**
- Inflation data operations
- RBI data fetching
- MP Government data fetching
- Time series processing

**`geospatial_service.py`**
- PostGIS queries
- Nearby locality search
- Heatmap data generation
- Isochrone calculations
- Distance calculations

**`scraping_service.py`**
- Web scraping utilities
- AQI data scraping
- Delivery availability checking
- Restaurant rating scraping
- Amenity data scraping
- Google Places API integration

**`neighborhood_service.py`**
- Neighborhood data aggregation
- Combines data from multiple sources
- Calculates neighborhood scores
- Updates neighborhood statistics
- Safety, connectivity, amenities scoring

**`recommendation_service.py`**
- Neighborhood recommendation algorithm
- Score calculation based on user preferences
- Data normalization
- Ranking and filtering
- Weight-based scoring system

**`ml_service.py`**
- Machine learning model loading
- Cost prediction using XGBoost
- Rent classification using DistilBERT
- Model version management
- Prediction history tracking

### API Routes (`/backend/app/api/v1`)

API routes define HTTP endpoints and request handlers.

**`__init__.py`**
- Package initialization

**`router.py`**
- Main API router
- Includes all sub-routers
- Central routing configuration

**`auth.py`**
- Authentication endpoints
- POST /auth/register - User registration
- POST /auth/login-json - User login
- POST /auth/verify-otp - OTP verification
- GET /auth/me - Current user info

**`rents.py`**
- Rent data endpoints
- GET /rents/ - List rent listings
- GET /rents/avg/{locality_id} - Average rent
- POST /rents/ - Create listing
- POST /rents/scrape/nobroker - Scrape NoBroker
- POST /rents/scrape/olx - Scrape OLX

**`groceries.py`**
- Grocery endpoints
- GET /groceries/stores - List stores
- GET /groceries/stores/{id}/items - Store items
- GET /groceries/cost/{locality_id} - Monthly cost
- POST /groceries/fetch/bigbasket - Fetch BigBasket
- POST /groceries/fetch/blinkit - Fetch Blinkit

**`transport.py`**
- Transport endpoints
- GET /transport/routes - List routes
- GET /transport/routes/{id}/fares - Route fares
- GET /transport/cost/{source}/{dest} - Calculate cost
- POST /transport/fetch/bcll - Fetch BCLL data

**`inflation.py`**
- Inflation endpoints
- GET /inflation/ - List inflation data
- GET /inflation/latest - Latest inflation
- POST /inflation/fetch/rbi - Fetch RBI data
- POST /inflation/fetch/mp-govt - Fetch MP Govt data

**`geospatial.py`**
- Geospatial endpoints
- GET /geospatial/localities - List localities
- GET /geospatial/localities/{id}/stats - Locality stats
- GET /geospatial/nearby - Find nearby
- GET /geospatial/heatmap - Heatmap data
- GET /geospatial/isochrone - Isochrone calculation
- POST /geospatial/localities/{id}/update-stats - Update stats

**`ml.py`**
- Machine learning endpoints
- POST /ml/predict-cost - Cost prediction
- POST /ml/classify-rent/{id} - Rent classification
- GET /ml/models/{name}/version - Model version info

**`recommendations.py`**
- Recommendation endpoints
- POST /recommendations/neighborhoods - Get recommendations
- POST /recommendations/aggregate/{locality_id} - Aggregate data
- POST /recommendations/refresh/{city} - Refresh city data

**`scraping.py`**
- Scraping endpoints
- POST /scraping/bhopal/all - Scrape all Bhopal data
- POST /scraping/bhopal/rent - Scrape rent data
- POST /scraping/bhopal/grocery - Scrape grocery data

### Machine Learning (`/backend/app/ml`)

**`__init__.py`**
- Package initialization

**`cost_predictor.py`**
- XGBoost cost prediction model
- Model loading and inference
- Feature preprocessing
- Prediction logic
- Model version handling

**`rent_classifier.py`**
- DistilBERT rent classification model
- NLP text processing
- Fair/overpriced classification
- Model loading and inference

---

## Frontend Directory (`/frontend`)

### Configuration Files

**`package.json`**
- Node.js dependencies
- Scripts for development and build
- Project metadata
- React, Vite, and other frontend libraries

**`vite.config.js`**
- Vite build tool configuration
- Development server settings
- Build optimizations
- Proxy configuration for API

**`index.html`**
- Main HTML entry point
- Root div for React app
- Meta tags and title

**`nginx.conf`**
- Nginx configuration for production
- Static file serving
- API proxy rules
- Caching configuration

### Docker Files

**`Dockerfile`**
- Development Docker image
- Installs Node.js dependencies
- Runs Vite dev server

**`Dockerfile.prod`**
- Production Docker image
- Builds optimized React app
- Serves static files with Nginx

### Source Code (`/frontend/src`)

**`main.jsx`**
- React application entry point
- Renders App component
- Sets up React root
- Initializes application

**`App.jsx`**
- Main React application component
- Defines routes using React Router
- Navigation structure
- Route protection logic
- Layout wrapper

**`App.css`**
- Global application styles
- Component styling
- Theme variables
- Responsive design rules

**`index.css`**
- Base CSS styles
- CSS reset
- Global typography
- Color scheme

### Components (`/frontend/src/components`)

**`MapView.jsx`**
- Interactive map component
- Uses Leaflet/Mapbox for rendering
- Displays locality markers
- Heatmap visualization
- User interaction handlers

**`InflationChart.jsx`**
- Chart component for inflation data
- Uses Chart.js for visualization
- Time series display
- Category filtering

**`RentListingCard.jsx`**
- Reusable card component for rent listings
- Displays property information
- Price formatting
- Property type badges

### Pages (`/frontend/src/pages`)

**`Landing.jsx`**
- Landing/home page
- Introduction to the platform
- Feature highlights
- Call-to-action buttons

**`Login.jsx`**
- User login page
- Login form
- Authentication handling
- Redirect logic
- Error display

**`Dashboard.jsx`**
- Main dashboard page
- Overview of user data
- Quick statistics
- Navigation to features

**`NeighborhoodRecommendations.jsx`**
- Neighborhood recommendation page
- User preference form
- Weight sliders for factors
- Recommendation results display
- Score visualization

**`LocalityComparison.jsx`**
- Locality comparison tool
- Side-by-side comparison
- Cost breakdowns
- Feature comparison tables

**`CostBurdenIndex.jsx`**
- Cost burden visualization
- Income vs expense charts
- Affordability indicators
- Percentage calculations

**`ScrapedData.jsx`**
- Display scraped data
- Raw listing viewer
- Data source information
- Filtering and sorting

**`UserProfile.jsx`**
- User profile page
- Profile information display
- Edit capabilities
- Account settings

### Services (`/frontend/src/services`)

**`api.js`**
- API client configuration
- Axios instance setup
- Request/response interceptors
- Token management
- API endpoint functions
- Organized by feature (rent, grocery, transport, etc.)

### Contexts (`/frontend/src/contexts`)

**`AuthContext.jsx`**
- React context for authentication
- Global auth state management
- Login/logout functions
- Token storage
- User information
- Protected route logic

---

## ML Worker Directory (`/ml_worker`)

**`Dockerfile`**
- Docker image for ML model training
- Python environment setup
- ML library installation

**`requirements.txt`**
- ML-specific dependencies
- XGBoost, PyTorch, scikit-learn
- Training libraries

**`train_cost_predictor.py`**
- XGBoost model training script
- Generates synthetic training data
- Trains regression model
- Saves model to shared volume
- Model versioning

**`train_rent_classifier.py`**
- DistilBERT model training script
- NLP model fine-tuning
- Text classification training
- Model serialization

**`test_model.py`**
- Model testing script
- Validates model predictions
- Performance evaluation
- Test data generation

---

## Airflow Directory (`/airflow`)

**`Dockerfile`**
- Airflow Docker image
- Airflow installation
- DAG execution environment

**`requirements.txt`**
- Airflow dependencies
- Python packages for DAGs

**`dags/__init__.py`**
- Package initialization

**`dags/scraping_dag.py`**
- Airflow DAG definition
- Scheduled scraping tasks
- Data pipeline orchestration
- Task dependencies
- Error handling

**`plugins/__init__.py`**
- Airflow plugins package

**`logs/`**
- Airflow execution logs
- Task run history
- Scheduler logs

---

## Nginx Directory (`/nginx`)

**`Dockerfile`**
- Nginx Docker image
- Production web server setup

**`nginx.conf`**
- Nginx server configuration
- Reverse proxy rules
- Static file serving
- API routing
- Security headers
- Compression settings
- Caching policies

---

## Understanding the Flow

### Application Startup

1. **Docker Compose** (`docker-compose.yml`) starts all services
2. **PostgreSQL** initializes with `init_db.sql`
3. **Backend** (`main.py`) starts FastAPI server
4. **Frontend** (`main.jsx`) renders React app
5. **Nginx** routes requests to appropriate services

### Request Flow

1. User interacts with **Frontend** (React components)
2. Frontend calls **API** (`api.js`) which sends HTTP requests
3. **Nginx** receives request and routes to **Backend**
4. **Backend** (`main.py`) receives request via **router** (`router.py`)
5. **API endpoint** (`auth.py`, `rents.py`, etc.) handles request
6. **Service layer** (`rent_service.py`, etc.) executes business logic
7. **Models** (`rent.py`, etc.) interact with **Database**
8. Response flows back through the same path

### Data Flow

1. **Scraping scripts** (`scrape_bhopal.py`) collect data
2. Data saved to **Database** via **Models**
3. **Services** aggregate and process data
4. **API endpoints** expose data
5. **Frontend** displays data to users

### Machine Learning Flow

1. **Training scripts** (`train_cost_predictor.py`) train models
2. Models saved to shared volume
3. **ML service** (`ml_service.py`) loads models
4. **API endpoints** (`ml.py`) receive prediction requests
5. Models generate predictions
6. Results returned to frontend

---

## Key Concepts

### Models vs Schemas
- **Models** (`/models`): Database table definitions (SQLAlchemy)
- **Schemas** (`/schemas`): API request/response validation (Pydantic)

### Services vs API Routes
- **Services** (`/services`): Business logic and external integrations
- **API Routes** (`/api`): HTTP endpoint handlers

### Frontend Structure
- **Pages**: Full page components (routes)
- **Components**: Reusable UI pieces
- **Services**: API communication
- **Contexts**: Global state management

This structure follows separation of concerns, making the codebase maintainable, testable, and scalable.

