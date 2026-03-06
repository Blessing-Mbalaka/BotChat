#!/usr/bin/env python3
"""
QUICK START GUIDE - Business School Discoverer

Copy-paste commands below to test and deploy the system.
"""

# ============================================================================
# STEP 1: START OLLAMA (Required - handles KPI extraction)
# ============================================================================

# Command 1: Start Ollama server
"""
ollama serve

# OR if you don't have Ollama installed:
1. Download from https://ollama.ai
2. Install and run: ollama serve
3. In another terminal, pull a model:
   ollama pull mistral        # Recommended (7B, 5GB)
   # OR for faster on low RAM:
   ollama pull neural-chat    # Smaller (7B, 4GB)
"""

# ============================================================================
# STEP 2: VERIFY INSTALLATION (Local Testing)
# ============================================================================

# Command 2: Test Ollama connection
"""
python -c "
from health_app.services.business_school_kpi import OllamaKPIExtractor
extractor = OllamaKPIExtractor()
status = extractor.test_connection()
print(f'Ollama Status: {status}')
"

# Expected output:
# Ollama Status: {'available': True, 'url': 'http://localhost:11434', 'models': [...]}
"""

# ============================================================================
# STEP 3: RUN BASIC DISCOVERY TEST (5 min)
# ============================================================================

# Command 3: Test discovery functionality
"""
python -c "
from health_app.services.business_school_kpi import BusinessSchoolDiscoverer
import json

discoverer = BusinessSchoolDiscoverer()

# Discover schools in South Africa
print('🔍 Discovering schools in South Africa...')
schools = discoverer.discover_schools_by_country('South Africa')
print(f'✅ Found {len(schools)} schools')
print(json.dumps(schools[:1], indent=2))  # Show first result
"
"""

# ============================================================================
# STEP 4: FULL PIPELINE TEST (10 min)
# ============================================================================

# Command 4: Run complete discovery + KPI extraction + export
"""
python -c "
from health_app.services.business_school_kpi import BusinessSchoolDiscoverer

discoverer = BusinessSchoolDiscoverer()

# Full pipeline: discover, extract KPIs, export CSV/MD
print('🚀 Running full discovery pipeline...')
schools = discoverer.discover_and_extract(
    country='South Africa',
    use_ollama=True
)
print(f'✅ Discovered {len(schools)} schools')
print('📁 Output files created:')
print('   - business_school_data/discovered_schools_south_africa.csv')
print('   - business_school_data/discovered_schools_south_africa.md')
"
"""

# ============================================================================
# STEP 5: RUN PROVIDED TEST SUITE (15 min)
# ============================================================================

# Command 5: Execute comprehensive tests
"""
# Option A: Original test suite (basic validation)
python test_discoverer.py

# Option B: Business school specific tests (real universities)
python test_business_school_discovery.py
"""

# ============================================================================
# STEP 6: VIEW RESULTS
# ============================================================================

# Command 6: Check generated files
"""
# View discovered schools (CSV format)
cat business_school_data/discovered_schools_south_africa.csv

# View generated report (Markdown)
cat business_school_data/discovered_schools_south_africa.md

# Check cache
cat health_app/business_school_data/discovered_schools.json | python -m json.tool
"""

# ============================================================================
# STEP 7: SCALE TO MULTIPLE COUNTRIES
# ============================================================================

# Command 7: Discover schools across Africa
"""
python -c "
from health_app.services.business_school_kpi import BusinessSchoolDiscoverer

discoverer = BusinessSchoolDiscoverer()

# Discover across entire Africa region
countries = [
    'South Africa', 'Nigeria', 'Kenya', 'Ethiopia',
    'Ghana', 'Morocco', 'Botswana', 'Zimbabwe'
]

print('🌍 Discovering schools across Africa...')
for country in countries:
    try:
        schools = discoverer.discover_and_extract(country, use_ollama=True)
        print(f'✅ {country}: {len(schools)} schools')
    except Exception as e:
        print(f'⚠️  {country}: {str(e)[:50]}')

print('📊 All discovery results saved to:')
print('   business_school_data/discovered_schools_*.csv')
print('   business_school_data/discovered_schools_*.md')
"
"""

# ============================================================================
# STEP 8: CLOUD DEPLOYMENT
# ============================================================================

# Command 8a: Deploy with Docker (Recommended)
"""
# Option 1: Docker Compose (Easiest for local/VM)
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f django

# Option 2: Azure Container Instances
az container create \\
  --resource-group myResourceGroup \\
  --name business-school-discoverer \\
  --image business-school-discoverer:latest \\
  --cpu 2 --memory 4 \\
  --ports 8000

# Option 3: Google Cloud Run
gcloud run deploy business-school-discoverer \\
  --image gcr.io/PROJECT_ID/business-school-discoverer \\
  --memory 4Gi --cpu 2
"""

# Command 8b: Package for cloud (5 min)
"""
# 1. Build Docker image
docker build -t business-school-discoverer .

# 2. Test locally
docker run -p 8000:8000 -p 11434:11434 business-school-discoverer

# 3. Push to cloud registry
docker tag business-school-discoverer gcr.io/PROJECT_ID/business-school-discoverer
docker push gcr.io/PROJECT_ID/business-school-discoverer
"""

# ============================================================================
# STEP 9: SCHEDULE FOR MONTHLY RUNS (Cloud)
# ============================================================================

# Command 9a: APScheduler (Built into Django)
"""
# Edit health_app/apps.py:

from apscheduler.schedulers.background import BackgroundScheduler

def ready(self):
    from health_app.services.business_school_kpi import BusinessSchoolDiscoverer
    
    def run_monthly_discovery():
        discoverer = BusinessSchoolDiscoverer()
        countries = ['South Africa', 'Nigeria', 'Kenya']
        for country in countries:
            discoverer.discover_and_extract(country, use_ollama=True)
    
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        run_monthly_discovery,
        'cron',
        day_of_month=1,
        hour=2,
        minute=0
    )
    scheduler.start()
"""

# Command 9b: Cloud Scheduler (GCP)
"""
gcloud scheduler jobs create http monthly-discovery \\
  --schedule="0 2 1 * *" \\
  --http-method=POST \\
  --uri="https://your-app.run.app/api/discover/" \\
  --headers="Authorization: Bearer TOKEN"
"""

# Command 9c: Azure Automation (Azure)
"""
# Create Automation Account runbook that calls:
az container restart \\
  --resource-group myGroup \\
  --name business-school-discoverer
"""

# ============================================================================
# STEP 10: MONITOR & ANALYZE
# ============================================================================

# Command 10a: Check discovery status
"""
python -c "
import json
from pathlib import Path

# Count schools discovered per country
data_dir = Path('business_school_data')
for csv_file in data_dir.glob('*.csv'):
    with open(csv_file) as f:
        line_count = sum(1 for _ in f) - 1  # Exclude header
    country = csv_file.stem.replace('discovered_schools_', '')
    print(f'{country}: {line_count} schools')
"
"""

# Command 10b: Analyze with Pandas
"""
python -c "
import pandas as pd
import glob

print('📊 Business School KPI Analysis')
print('='*60)

for file in glob.glob('business_school_data/*.csv'):
    df = pd.read_csv(file)
    if len(df) > 0:
        country = file.split('_')[-1].replace('.csv', '')
        print(f'\\n🌍 {country.upper()}:')
        print(f'   Schools: {len(df)}')
        print(f'   Avg Programmes: {df[\"Programmes\"].mean():.1f}')
        print(f'   Avg Research Centres: {df[\"Research_Centres\"].mean():.1f}')
"
"""

# Command 10c: View logs (Cloud)
"""
# Azure Container Instances
az container logs --resource-group myGroup --name discoverer --follow

# Google Cloud Run
gcloud run logs read business-school-discoverer --limit 50

# Docker Compose
docker-compose logs -f django
"""

# ============================================================================
# STEP 11: TROUBLESHOOTING
# ============================================================================

# Command 11a: Check if Ollama is running
"""
curl http://localhost:11434/api/tags
# Expected: JSON list of available models
"""

# Command 11b: Test KPI extraction without Ollama
"""
python -c "
from health_app.services.business_school_kpi import OllamaKPIExtractor

extractor = OllamaKPIExtractor()

# This will use pattern matching if Ollama unavailable
content = 'MBA programme AACSB accredited university'
kpis = extractor.extract_kpis_from_content(content, 'Test University')
print(f'KPIs extracted (pattern matching): {kpis}')
"
"""

# Command 11c: Refresh cache
"""
python -c "
from health_app.services.business_school_kpi import BusinessSchoolDiscoverer

discoverer = BusinessSchoolDiscoverer()

# Force refresh (ignore cache, re-discover)
schools = discoverer.discover_schools_by_country('South Africa', force_refresh=True)
print(f'Refreshed: {len(schools)} schools')
"
"""

# Command 11d: Clear cache
"""
rm health_app/business_school_data/discovered_schools.json
# Next discovery will create new cache
"""

# ============================================================================
# PRODUCTION CHECKLIST
# ============================================================================

"""
✅ BEFORE DEPLOYING TO CLOUD:

[ ] Ollama model downloaded (mistral or neural-chat)
[ ] Python modules tested locally (python test_discoverer.py)
[ ] Docker image built successfully (docker build -t ...)
[ ] Discovered schools validation (check CSV files)
[ ] Cloud credentials configured (az login / gcloud auth)
[ ] File storage mounted (Azure Storage / Cloud Storage)
[ ] Scheduler configured (APScheduler / Cloud Scheduler)
[ ] Monitoring alerts set up (check logs for errors)
[ ] Cost estimates reviewed (should be <$50/month)

✅ AFTER DEPLOYING TO CLOUD:

[ ] Container running (docker ps / az container list)
[ ] Ollama responding (curl localhost:11434)
[ ] Discovery logs visible (docker logs / az logs)
[ ] Output files generated (check storage)
[ ] Monthly job scheduled (check scheduler logs)
[ ] Performance monitoring enabled

✅ MONTHLY REVIEWS (During 1-month test):

[ ] Total schools discovered per country
[ ] KPI extraction success rate (Ollama vs patterns)
[ ] Data quality review (sample CSV/MD files)
[ ] Cost analysis (storage + compute)
[ ] System uptime (check logs for errors)
[ ] Recommendations for final deployment
"""

# ============================================================================
# USEFUL LINKS
# ============================================================================

"""
📚 DOCUMENTATION:
- DEPLOYMENT_GUIDE.md - Detailed cloud setup
- IMPLEMENTATION_SUMMARY.md - Features & architecture
- VERIFICATION_REPORT.md - Test results
- discoverer.py - Main discovery code
- ollama_kpi_extractor.py - KPI extraction code

🔗 EXTERNAL RESOURCES:
- Ollama Download: https://ollama.ai
- Azure Container Instances: https://azure.microsoft.com/services/container-instances/
- Google Cloud Run: https://cloud.google.com/run
- Docker Documentation: https://docs.docker.com/
- APScheduler: https://apscheduler.readthedocs.io/

💬 SUPPORT:
- Check logs: docker logs <container_id>
- Test Ollama: curl http://localhost:11434/api/tags
- View cache: cat health_app/business_school_data/discovered_schools.json
- Check exports: ls -la business_school_data/discovered_schools_*.csv
"""

# ============================================================================
# QUICK REFERENCE
# ============================================================================

"""
TYPICAL WORKFLOW:

1. Start Ollama:
   ollama serve

2. Test locally (5 min):
   python test_discoverer.py

3. Run discovery (10 min):
   python -c "from health_app.services.business_school_kpi import BusinessSchoolDiscoverer; print(BusinessSchoolDiscoverer().discover_and_extract('South Africa', use_ollama=True))"

4. Check results (2 min):
   ls -la business_school_data/discovered_schools_south_africa.*

5. Deploy to cloud (30 min):
   docker build -t discoverer .
   docker push gcr.io/PROJECT_ID/discoverer

6. Schedule monthly runs:
   # Edit apps.py + add APScheduler, OR
   # Create Cloud Scheduler job

7. Monitor monthly:
   docker logs <container>
   # or
   gcloud run logs read <service>
"""

print("""
╔════════════════════════════════════════════════════════════════╗
║     BUSINESS SCHOOL DISCOVERER - QUICK START GUIDE LOADED     ║
║                                                                ║
║  Run the commands above to test and deploy the system.        ║
║                                                                ║
║  See DEPLOYMENT_GUIDE.md for detailed cloud setup.           ║
╚════════════════════════════════════════════════════════════════╝
""")
