# Business School Discoverer - Cloud Deployment Guide

## 🎯 System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    DISCOVERY & KPI EXTRACTION                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. WEB SEARCH (Discover Schools)                               │
│     └─ BusinessSchoolDiscoverer.discover_schools_by_country()   │
│        └─ Input: "South Africa"                                 │
│        └─ Output: [School URLs, Names, Locations]               │
│                                                                  │
│  2. FETCH WEBSITE CONTENT                                       │
│     └─ BeautifulSoup + Requests (5000 char limit)               │
│        └─ Strip HTML, extract text                              │
│        └─ Cache to avoid re-fetching                            │
│                                                                  │
│  3. EXTRACT KPIs WITH OLLAMA (or Pattern Matching)              │
│     └─ OllamaKPIExtractor.extract_kpis_from_content()           │
│        └─ Ask local Ollama LLM: "What are KPIs in this text?"  │
│        └─ Response: JSON with programmes, research, staff, etc. │
│        └─ Fallback: Use regex patterns (always works)           │
│                                                                  │
│  4. EXPORT RESULTS                                              │
│     ├─ CSV: business_school_data/discovered_schools_SA.csv      │
│     └─ MD:  business_school_data/discovered_schools_SA.md       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 📦 Local Setup (Testing Before Cloud)

### Prerequisites
```bash
# Python 3.8+
python --version

# Virtual environment
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start Ollama (download from ollama.ai)
ollama serve

# In another terminal, pull models
ollama pull mistral  # Primary (7B parameters, ~5GB)
ollama pull neural-chat  # Smaller (7B, ~4GB)
```

### Run Tests Locally
```bash
# Test 1: Check Ollama connection
.\venv\Scripts\python.exe test_discoverer.py

# Test 2: Real business schools
.\venv\Scripts\python.exe test_business_school_discovery.py

# Test 3: Manual discovery
python -c "
from health_app.services.business_school_kpi import BusinessSchoolDiscoverer
discoverer = BusinessSchoolDiscoverer()
schools = discoverer.discover_and_extract('South Africa', use_ollama=True)
print(f'Discovered {len(schools)} schools')
"
```

### Output Files
```
business_school_data/
├── discovered_schools.json          # Cache (24h TTL)
├── discovered_schools_south_africa.csv
├── discovered_schools_south_africa.md
├── discovered_schools_nigeria.csv
├── discovered_schools_nigeria.md
└── ...
```

## ☁️ Cloud Deployment Options

### Option 1: Azure Container Instances (Recommended)

#### Architecture
```
┌──────────────────────────────────────────────┐
│      Azure Container Instance                │
├──────────────────────────────────────────────┤
│                                              │
│  ┌──────────────────────────────────────┐   │
│  │  Django App (Port 8000)              │   │
│  │  - REST API endpoints                │   │
│  │  - Discoverer service                │   │
│  └──────────────────────────────────────┘   │
│               ↓ (localhost:11434)            │
│  ┌──────────────────────────────────────┐   │
│  │  Ollama (Port 11434)                 │   │
│  │  - mistral or neural-chat model      │   │
│  └──────────────────────────────────────┘   │
│               ↓                               │
│  ┌──────────────────────────────────────┐   │
│  │  Mounted File Share (Storage)        │   │
│  │  - CSV exports                       │   │
│  │  - MD reports                        │   │
│  │  - Cache files                       │   │
│  └──────────────────────────────────────┘   │
└──────────────────────────────────────────────┘
```

#### Steps
```bash
# 1. Create Dockerfile
# See DOCKERFILE section below

# 2. Build image
docker build -t business-school-discoverer .

# 3. Create Azure Container Instance
az container create \
  --resource-group myResourceGroup \
  --name business-school-discoverer \
  --image business-school-discoverer:latest \
  --cpu 2 --memory 4 \
  --ports 8000 \
  --environment-variables \
    DJANGO_SECRET_KEY="your-secret-key" \
    OLLAMA_PORT="11434" \
  --azure-file-volume-mount-path /app/business_school_data \
  --azure-file-volume-share-name schools-data \
  --azure-file-volume-account-name mystorageaccount \
  --azure-file-volume-account-key "your-storage-key"
```

### Option 2: Docker Compose (Local or VM)

```yaml
# docker-compose.yml
version: '3.8'

services:
  django:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OLLAMA_HOST=http://ollama:11434
      - DEBUG=False
    depends_on:
      - ollama
    volumes:
      - ./business_school_data:/app/business_school_data
    command: gunicorn health_project.wsgi:application --bind 0.0.0.0:8000

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    command: serve

volumes:
  ollama_data:
```

```bash
# Deploy
docker-compose up -d

# Check status
docker-compose logs -f

# Manually trigger discovery
docker exec django-container python manage.py shell << 'EOF'
from health_app.services.business_school_kpi import BusinessSchoolDiscoverer
discoverer = BusinessSchoolDiscoverer()
schools = discoverer.discover_and_extract('South Africa', use_ollama=True)
print(f'Discovered {len(schools)} schools')
EOF
```

### Option 3: Google Cloud Run

```bash
# 1. Build image for Cloud Run
docker build -t gcr.io/PROJECT_ID/business-school-discoverer .

# 2. Push to registry
docker push gcr.io/PROJECT_ID/business-school-discoverer

# 3. Deploy to Cloud Run
gcloud run deploy business-school-discoverer \
  --image gcr.io/PROJECT_ID/business-school-discoverer \
  --platform managed \
  --region us-central1 \
  --memory 4Gi \
  --cpu 2 \
  --timeout 3600 \
  --set-env-vars OLLAMA_HOST=http://localhost:11434
```

## 🤖 Scheduling Discovery Runs

### Option A: APScheduler (Built-in)

```python
# health_app/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from health_app.services.business_school_kpi import BusinessSchoolDiscoverer
import logging

logger = logging.getLogger(__name__)

def run_discovery_job():
    """Run discovery for all target countries monthly"""
    countries = ['South Africa', 'Nigeria', 'Kenya', 'Ethiopia']
    discoverer = BusinessSchoolDiscoverer()
    
    for country in countries:
        logger.info(f"Discovering schools in {country}...")
        try:
            schools = discoverer.discover_and_extract(country, use_ollama=True)
            logger.info(f"✅ Found {len(schools)} schools in {country}")
        except Exception as e:
            logger.error(f"❌ Error discovering {country}: {e}")

def start_scheduler():
    """Start background scheduler"""
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        run_discovery_job,
        'cron',
        day_of_month=1,  # Run on 1st of every month
        hour=2,          # At 2 AM UTC
        minute=0
    )
    scheduler.start()
    logger.info("✅ Discovery scheduler started")

# In settings.py, add to INSTALLED_APPS ready() method
# apps.py: default_app_config = 'health_app.apps.HealthAppConfig'
# apps.py HealthAppConfig.ready(): start_scheduler()
```

### Option B: Cloud Scheduler (Google Cloud)

```bash
# Create scheduler job
gcloud scheduler jobs create http monthly-discovery \
  --schedule="0 2 1 * *" \
  --http-method=POST \
  --uri="https://your-app.run.app/api/discover/trigger/" \
  --headers="Authorization: Bearer YOUR_TOKEN"
```

### Option C: Azure Automation

```bash
# Use Azure Automation Account with Runbook
# Runbook triggers: az container restart --resource-group myGroup --name business-school-discoverer
```

## 🐳 Dockerfile Example

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Create data directory
RUN mkdir -p business_school_data

# Download Ollama model (optional, otherwise pull at runtime)
# RUN ollama pull mistral

# Expose ports
EXPOSE 8000 11434

# Run Ollama in background + Django in foreground
CMD ["sh", "-c", "ollama serve & sleep 10 && python manage.py runserver 0.0.0.0:8000"]
```

## 📊 Monitoring & Analytics

### Check Discovery Progress
```bash
# View CSV exports
ls -la business_school_data/*.csv

# Count discovered schools per country
for file in business_school_data/*.csv; do
  echo "$(basename $file): $(wc -l < $file) schools"
done

# Analyze with pandas
python -c "
import pandas as pd
import glob

for file in glob.glob('business_school_data/*.csv'):
    df = pd.read_csv(file)
    print(f'{file}:')
    print(f'  - Total schools: {len(df)}')
    print(f'  - Avg programmes: {df[\"Programmes\"].mean():.1f}')
    print(f'  - Avg research centres: {df[\"Research_Centres\"].mean():.1f}')
"
```

### View Logs
```bash
# Azure Container Instances
az container logs --resource-group myGroup --name discoverer

# Docker Compose
docker-compose logs -f django

# Google Cloud Run
gcloud run logs read business-school-discoverer --limit 50
```

## 🔍 API Endpoints (Optional)

```python
# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('api/schools/<country>/', views.get_schools),
    path('api/discover/<country>/', views.trigger_discovery),
    path('api/status/', views.discovery_status),
]

# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def get_schools(request, country):
    """Get discovered schools for country"""
    discoverer = BusinessSchoolDiscoverer()
    schools = discoverer.get_cached_schools(country)
    return Response({'country': country, 'schools': schools, 'count': len(schools)})

@api_view(['POST'])
def trigger_discovery(request, country):
    """Trigger discovery for country (async)"""
    # Use Celery for async: tasks.discover_schools.delay(country)
    return Response({'status': 'discovery_started', 'country': country})

@api_view(['GET'])
def discovery_status(request):
    """Get status of all discoveries"""
    # Return cache metadata, last run times, etc.
    pass
```

## 📈 Success Metrics (1-Month Test)

Track these during your cloud deployment:

1. **Discovery Metrics**
   - Total schools discovered: Target 1000+
   - Countries covered: Target 20+
   - Discovery time per country: Target <5 min
   - Cache hit rate: Target >90%

2. **KPI Extraction Metrics**
   - Ollama extraction success rate: Target >85%
   - Fallback pattern match rate: <15%
   - Average KPIs per school: 4+ fields
   - Data quality score: Validate programmes/research centres

3. **System Metrics**
   - Monthly uptime: Target 99%
   - Average response time: <500ms
   - Storage used: Monitor CSV/MD growth
   - API errors: Target <0.1%

4. **Cost Metrics**
   - Container instance cost (Azure): ~$10-20/month
   - Storage cost: <$5/month
   - Ollama compute: Included in instance

## ❓ Troubleshooting

| Issue | Solution |
|-------|----------|
| Ollama 404 errors | Check localhost:11434 is reachable, model pulled |
| Discovery hangs | Increase timeout, check network access |
| Cache stale | Set `force_refresh=True` or delete JSON cache |
| Slow extraction | Use smaller model (neural-chat instead of mistral) |
| Storage full | Archive old CSV/MD files to cloud storage |

## 🎬 Quick Start (tldr)

```bash
# Local test (5 min)
ollama serve &
python test_business_school_discovery.py

# Cloud deployment (30 min)
docker build -t business-school .
docker-compose up -d

# Schedule monthly (5 min)
# Edit health_app/apps.py to call start_scheduler()

# Monitor (ongoing)
docker-compose logs -f
# or
az container logs --follow --name discoverer
```

---

**Questions?** Check the code comments in `discoverer.py` and `ollama_kpi_extractor.py` for detailed implementation notes.
