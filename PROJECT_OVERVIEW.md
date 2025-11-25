# MP Cost Pulse - Project Overview

## Introduction

MP Cost Pulse is a comprehensive cost-of-living analysis platform designed specifically for Madhya Pradesh, India. The platform empowers residents, prospective movers, and policymakers with data-driven insights into housing costs, grocery prices, transportation expenses, and overall affordability across different localities in the state.

## Problem Statement

Finding affordable housing and understanding the true cost of living in a new area is challenging. People often struggle to compare neighborhoods, estimate monthly expenses, or determine if a rental listing is fairly priced. MP Cost Pulse addresses these pain points by aggregating real-time data from multiple sources and providing intelligent recommendations based on individual preferences and budgets.

## Core Functionality

The platform operates as a full-stack web application that collects, processes, and presents cost-of-living data through multiple integrated systems. At its heart, the system scrapes rental listings from property websites like NoBroker and OLX, fetches grocery pricing from e-commerce platforms such as BigBasket and Blinkit, and aggregates public transport fare information. This raw data is then processed through machine learning models to generate personalized cost predictions and neighborhood recommendations.

## Key Features

**Intelligent Recommendations**: The system uses advanced algorithms to recommend neighborhoods based on user preferences including budget, family size, property type, and lifestyle priorities. Each recommendation includes a comprehensive score that factors in rent affordability, grocery costs, air quality, amenities availability, and connectivity.

**Cost Prediction**: Machine learning models analyze user profiles to predict personalized monthly expenses. The system considers income levels, family composition, commuting patterns, and lifestyle choices to provide accurate cost breakdowns across rent, groceries, and transportation.

**Rent Analysis**: The platform continuously monitors rental listings across multiple sources, classifying properties as fairly priced or overpriced using natural language processing. Users can view average rental prices by property type and locality, enabling informed decision-making.

**Geospatial Analysis**: Interactive maps display cost heatmaps, allowing users to visualize affordability patterns across the city. The system calculates travel time isochrones and identifies nearby amenities, helping users understand connectivity and accessibility.

**Data Aggregation**: Automated scraping jobs run daily to keep the database current with the latest market prices. The system aggregates data from multiple sources, calculates locality-level statistics, and maintains historical trends for inflation tracking.

## Technology Architecture

The platform is built using modern, scalable technologies. The backend leverages FastAPI for high-performance API endpoints, PostgreSQL with PostGIS extension for geospatial data management, and machine learning frameworks including XGBoost and PyTorch for predictive analytics. The frontend is a responsive React application with interactive visualizations and real-time data updates.

The entire system is containerized using Docker, ensuring consistent deployment across environments. An Nginx reverse proxy handles load balancing and serves as the entry point for all requests. Apache Airflow orchestrates scheduled data collection tasks, ensuring the database remains current with market conditions.

## Data Sources and Integration

The platform integrates with multiple external data sources. Rental information comes from property listing websites, grocery prices from online marketplaces, and transport data from public transit authorities. Additionally, the system incorporates air quality indices, restaurant ratings, and amenity information from various APIs to provide a holistic view of neighborhood quality.

## User Experience

Users begin by creating a profile that captures their budget, family size, and preferences. The system then presents personalized neighborhood recommendations ranked by suitability score. Each recommendation includes detailed breakdowns of monthly costs, nearby amenities, air quality metrics, and delivery service availability. Interactive maps and charts help users visualize and compare different options.

## Impact and Use Cases

The platform serves multiple user segments. Families relocating to Madhya Pradesh can identify affordable neighborhoods that match their lifestyle needs. Students can find budget-friendly areas near educational institutions. Real estate professionals can access market trends and pricing insights. Policymakers can analyze affordability patterns to inform urban planning decisions.

## Continuous Improvement

The system is designed for continuous learning and improvement. Machine learning models are retrained periodically with new data to enhance prediction accuracy. User feedback mechanisms allow the platform to refine recommendation algorithms. Regular data updates ensure information remains relevant and actionable.

## Conclusion

MP Cost Pulse transforms the complex task of finding affordable housing into a streamlined, data-driven experience. By combining real-time market data with intelligent analytics, the platform empowers users to make informed decisions about where to live, ultimately improving quality of life and financial well-being for residents of Madhya Pradesh.

