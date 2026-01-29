# Radar de Leads - Market Intelligence Platform

## Overview

This is a Brazilian market intelligence and lead radar application that scrapes and analyzes public web mentions to identify potential leads and market opportunities. The system collects data from forums, social media, marketplaces, and other public sources, then uses AI-powered analysis to extract actionable insights about product/service demand across Brazilian cities.

The application provides a simple web interface where users can search for products or services and receive analyzed market intelligence data within a specified time range.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Framework
- **Flask** serves as the web framework, handling HTTP requests and serving the frontend
- Single-file backend architecture with `main.py` as the entry point and `engine.py` containing the core business logic
- RESTful API design pattern for frontend-backend communication

### AI Integration
- **OpenAI GPT-5** integration via Replit AI Integrations for natural language analysis
- Environment variables `AI_INTEGRATIONS_OPENAI_API_KEY` and `AI_INTEGRATIONS_OPENAI_BASE_URL` configure the OpenAI client
- The `MarketIntelligenceEngine` class encapsulates all AI-powered analysis functionality

### Data Processing Pipeline
1. **Scraping Layer** - Currently simulated with placeholder data; designed to be extended with real scrapers for Brazilian forums, social media, and marketplaces
2. **Normalization Layer** - Text cleaning using `unidecode` for accent handling, URL removal, and whitespace normalization
3. **Analysis Layer** - AI-powered mention analysis to extract intent, location, and lead quality signals

### Frontend Architecture
- Server-side rendered HTML template embedded in Python using `render_template_string`
- Bootstrap 5 for responsive UI styling
- Vanilla JavaScript for form handling and async API calls
- Portuguese (Brazilian) language interface

### Design Decisions
- **Embedded HTML templates** were chosen over separate template files for simplicity in this MVP phase
- **Simulated data scraping** allows development and testing of the analysis pipeline without requiring live data sources
- **Single engine class** consolidates all intelligence operations, making it easy to extend with additional analysis methods

## External Dependencies

### Python Packages
- `flask` - Web framework
- `openai` - AI model integration
- `beautifulsoup4` - HTML parsing for web scraping
- `requests` - HTTP client for web requests
- `pandas` - Data manipulation and analysis
- `unidecode` - Unicode text normalization (accent removal)

### External Services
- **OpenAI API** (via Replit AI Integrations) - Powers the natural language analysis of scraped mentions

### Frontend CDN
- **Bootstrap 5** - CSS framework loaded from jsdelivr CDN