# MP Cost Pulse

A production-ready, market-grade full-stack SaaS platform for analyzing cost of living data in Madhya Pradesh, India. The platform provides AI-powered insights into rent prices, grocery costs, transport fares, inflation trends, and geospatial analysis with machine learning predictions.

## Features

- **AI-Powered Cost Prediction**: XGBoost regression model for personalized monthly cost predictions
- **Smart Rent Classification**: PyTorch DistilBERT NLP model to classify listings as "fair" or "overpriced"
- **Rent Analysis**: Scrape and analyze rental listings from NoBroker and OLX
- **Grocery Pricing**: Integrate with BigBasket and Blinkit APIs for grocery cost analysis
- **Transport Costs**: Fetch BCLL transport fares and calculate monthly commute costs
- **Inflation Tracking**: Load and visualize RBI and MP Government inflation data
- **Geospatial Analysis**: PostGIS-powered locality heatmaps, isochrone calculations, and nearby locality search
- **Cost Burden Index**: Calculate and visualize cost burden as percentage of income
- **Locality Comparison**: Compare costs across different localities
- **User Profiling**: Form-based user profile for personalized predictions
- **Interactive Dashboards**: Real-time visualizations with Chart.js and interactive maps with Leaflet
- **Production-Ready**: Nginx reverse proxy, optimized builds, security headers, scalable deployment

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework with async support
- **PostgreSQL + PostGIS**: Geospatial database
- **SQLAlchemy**: ORM for database operations
- **Scrapy/BeautifulSoup**: Web scraping
- **Airflow**: Scheduled data scraping and updates
- **XGBoost**: Gradient boosting for cost prediction
- **PyTorch + Transformers**: DistilBERT for NLP classification
- **Scikit-learn**: Machine learning utilities

### Frontend
- **React**: UI framework
- **Vite**: Build tool
- **Leaflet/Mapbox GL**: Interactive maps
- **Chart.js**: Data visualizations
- **React Router**: Navigation

### Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **Nginx**: Reverse proxy and load balancing
- **ML Worker**: Separate service for model training
- **Production Builds**: Optimized frontend and backend builds

## Project Structure

```
mp-cost-pulse/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── rents.py
│   │   │       ├── groceries.py
│   │   │       ├── transport.py
│   │   │       ├── inflation.py
│   │   │       ├── geospatial.py
│   │   │       └── router.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── database.py
│   │   ├── models/
│   │   │   ├── rent.py
│   │   │   ├── grocery.py
│   │   │   ├── transport.py
│   │   │   ├── inflation.py
│   │   │   └── geospatial.py
│   │   ├── schemas/
│   │   │   ├── rent.py
│   │   │   ├── grocery.py
│   │   │   ├── transport.py
│   │   │   ├── inflation.py
│   │   │   └── geospatial.py
│   │   └── services/
│   │       ├── rent_service.py
│   │       ├── grocery_service.py
│   │       ├── transport_service.py
│   │       ├── inflation_service.py
│   │       └── geospatial_service.py
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── MapView.jsx
│   │   │   └── InflationChart.jsx
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── LocalityComparison.jsx
│   │   │   └── CostBurdenIndex.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
├── airflow/
│   ├── dags/
│   │   └── scraping_dag.py
│   ├── plugins/
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Getting Started

### Prerequisites

- Docker and Docker Compose installed
- Minimum 8GB RAM recommended (for ML models)
- API keys for:
  - Mapbox (optional, for enhanced maps)
  - Isochrone API (optional)
  - BigBasket API (optional)
  - Blinkit API (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd heatmap
   ```

2. **Create environment file**
   Create a `.env` file in the root directory:
   ```env
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=mpcostpulse
   SECRET_KEY=your-secret-key-change-in-production
   MAPBOX_ACCESS_TOKEN=your_token_here
   ISOCRONE_API_KEY=your_key_here
   BIGBASKET_API_KEY=your_key_here
   BLINKIT_API_KEY=your_key_here
   CORS_ORIGINS=["http://localhost:3000","http://localhost:5173","http://localhost"]
   ```

3. **Start the services**
   ```bash
   docker-compose up -d
   ```

4. **Initialize the database**
   The database will be automatically initialized with PostGIS extension and all tables on first startup.

5. **Train ML models (optional)**
   ```bash
   docker-compose exec ml-worker python train_cost_predictor.py
   docker-compose exec ml-worker python train_rent_classifier.py
   ```

6. **Access the services**
   - **Production (via Nginx)**: http://localhost
   - **Frontend (direct)**: http://localhost:3000
   - **Backend API (direct)**: http://localhost:8000
   - **API Docs**: http://localhost:8000/docs
   - **Airflow**: http://localhost:8080 (default credentials: airflow/airflow)

### Development

#### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

#### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

### Rents
- `GET /api/v1/rents/` - Get rent listings
- `GET /api/v1/rents/avg/{locality_id}` - Get average rent
- `POST /api/v1/rents/` - Create rent listing
- `POST /api/v1/rents/scrape/nobroker` - Scrape NoBroker
- `POST /api/v1/rents/scrape/olx` - Scrape OLX

### Groceries
- `GET /api/v1/groceries/stores` - Get grocery stores
- `GET /api/v1/groceries/stores/{store_id}/items` - Get store items
- `GET /api/v1/groceries/cost/{locality_id}` - Calculate monthly cost
- `POST /api/v1/groceries/fetch/bigbasket` - Fetch BigBasket data
- `POST /api/v1/groceries/fetch/blinkit` - Fetch Blinkit data

### Transport
- `GET /api/v1/transport/routes` - Get transport routes
- `GET /api/v1/transport/routes/{route_id}/fares` - Get route fares
- `GET /api/v1/transport/cost/{source_id}/{dest_id}` - Calculate monthly cost
- `POST /api/v1/transport/fetch/bcll` - Fetch BCLL fares

### Inflation
- `GET /api/v1/inflation/` - Get inflation data
- `GET /api/v1/inflation/latest` - Get latest inflation
- `POST /api/v1/inflation/fetch/rbi` - Fetch RBI data
- `POST /api/v1/inflation/fetch/mp-govt` - Fetch MP Govt data

### Geospatial
- `GET /api/v1/geospatial/localities` - Get localities
- `GET /api/v1/geospatial/localities/{locality_id}/stats` - Get locality stats
- `GET /api/v1/geospatial/nearby` - Find nearby localities
- `GET /api/v1/geospatial/heatmap` - Get heatmap data
- `GET /api/v1/geospatial/isochrone` - Calculate isochrone
- `POST /api/v1/geospatial/localities/{locality_id}/update-stats` - Update stats

## Airflow DAGs

The project includes an Airflow DAG (`scraping_dag`) that runs daily to:
1. Scrape rent listings from NoBroker and OLX
2. Fetch grocery data from BigBasket and Blinkit
3. Fetch transport fares from BCLL
4. Fetch inflation data from RBI and MP Government
5. Update locality statistics

## Database Schema

The database includes the following main tables:
- `users` - User accounts and authentication
- `localities` - Geographic localities with PostGIS geometry
- `locality_stats` - Aggregated statistics per locality
- `rent_listings` - Rental property listings
- `grocery_stores` - Grocery store information
- `grocery_items` - Grocery item pricing
- `transport_routes` - Public transport routes
- `transport_fares` - Transport fare information
- `inflation_data` - Inflation time series data
- `ml_model_versions` - ML model versioning and metadata
- `predictions` - User predictions history

## Machine Learning Models

### Cost Predictor (XGBoost)
- **Purpose**: Predict personalized monthly cost of living
- **Features**: Income, family size, property preference, commute patterns, amenities priority
- **Output**: Monthly cost breakdown (rent, groceries, transport)
- **Training**: Run `train_cost_predictor.py` in ML worker

### Rent Classifier (DistilBERT)
- **Purpose**: Classify rent listings as "fair" or "overpriced"
- **Input**: Listing title, description, property features
- **Output**: Classification with confidence score
- **Training**: Run `train_rent_classifier.py` in ML worker (fine-tune with real data)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[Your License Here]

## Production Deployment

### Using Nginx Reverse Proxy

The production setup includes Nginx as a reverse proxy:
- All traffic goes through port 80
- Frontend and backend are served through Nginx
- Security headers enabled
- Gzip compression enabled
- Static asset caching

### Scaling

To scale the application:
```bash
docker-compose up -d --scale backend=3  # Scale backend workers
```

### Model Training

Train models periodically:
```bash
# Cost predictor
docker-compose exec ml-worker python train_cost_predictor.py

# Rent classifier
docker-compose exec ml-worker python train_rent_classifier.py
```

### Security

- Change `SECRET_KEY` in production
- Use strong database passwords
- Configure CORS origins properly
- Enable HTTPS in production (add SSL certificates to Nginx)
- Regularly update dependencies

## Support

For issues and questions, please open an issue on GitHub.

