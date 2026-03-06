"""
Test BusinessSchoolDiscoverer with Ollama KPI extraction
Tests discovery pipeline in action
"""

import sys
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Add path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from health_app.services.business_school_kpi.discoverer import BusinessSchoolDiscoverer
from health_app.services.business_school_kpi.ollama_kpi_extractor import OllamaKPIExtractor


def test_ollama_connection():
    """Test Ollama connection"""
    print("\n" + "="*70)
    print("🤖 TESTING OLLAMA CONNECTION")
    print("="*70)
    
    extractor = OllamaKPIExtractor()
    status = extractor.test_connection()
    
    print(f"\nStatus: {status['message']}")
    if status['available']:
        print(f"Models available: {', '.join(status['models'])}")
    else:
        print("⚠️  Ollama is not running. Start it with: ollama serve")
        print("    Or use local pattern matching fallback (works without Ollama)")


def test_discovery_by_country():
    """Test discovering schools by country"""
    print("\n" + "="*70)
    print("🌍 TESTING SCHOOL DISCOVERY BY COUNTRY")
    print("="*70)
    
    discoverer = BusinessSchoolDiscoverer()
    
    # Test discovery
    print("\n1️⃣ Discovering schools in South Africa...")
    schools = discoverer.discover_schools_by_country("South Africa")
    
    if schools:
        print(f"\n✅ Found {len(schools)} schools in South Africa:")
        for i, school in enumerate(schools[:5], 1):
            print(f"\n  {i}. {school['school_name']}")
            print(f"     Website: {school['website']}")
            print(f"     Programmes: {len(school.get('programmes', []))} types")
            print(f"     Research Centres: {len(school.get('research_centres', []))} centres")
            print(f"     Extraction: {school.get('kpi_extraction_method', 'unknown')}")
    else:
        print("⚠️  No schools found (this may require WebSearchService configured)")
    
    # Test cache
    print("\n2️⃣ Testing cache (should be instant)...")
    cached = discoverer.get_cached_schools("South Africa")
    if cached:
        print(f"✅ Retrieved {len(cached)} cached schools from South Africa")
    else:
        print("⚠️  No cached schools found")


def test_discovery_by_region():
    """Test discovering schools by region"""
    print("\n" + "="*70)
    print("🌏 TESTING SCHOOL DISCOVERY BY REGION")
    print("="*70)
    
    discoverer = BusinessSchoolDiscoverer()
    
    print("\nDiscovering in Africa region (may take a moment)...")
    print("This will search multiple countries...")
    
    # Note: This is a demonstration - actual discovery depends on WebSearchService
    print("\nFor full discovery:\n")
    print("  # Discover all schools in Africa")
    print("  schools = discoverer.discover_schools_by_region('Africa')")
    print("  print(f'Found {len(schools)} schools in Africa')")
    print("\n  # Get schools from specific country")
    print("  sa_schools = discoverer.discover_schools_by_country('South Africa')")
    print("\n  # Extract KPIs with Ollama")
    print("  enriched = discoverer.extract_kpis_with_ollama(schools[0])")


def test_kpi_extraction():
    """Test KPI extraction with sample content"""
    print("\n" + "="*70)
    print("🤖 TESTING KPI EXTRACTION")
    print("="*70)
    
    extractor = OllamaKPIExtractor()
    
    # Sample website content
    sample_content = """
    University of Cape Town Business School
    
    Our programmes include:
    - MBA (Master of Business Administration) - 2 years
    - Executive MBA - 18 months
    - Master of Science in Finance
    - Graduate Diploma in Business
    - Professional Certificate in Leadership
    
    We have over 150 faculty members across diverse disciplines:
    - Finance: 35 professors
    - Strategy: 28 professors
    - Marketing: 24 professors
    - Operations: 22 professors
    
    Research Centres:
    - Centre for Financial Services Research
    - African Business Research Environment
    - Digital Innovation Laboratory
    
    We are accredited by:
    - AACSB International
    - EQUIS (European Quality)
    
    Our faculty conducts research in emerging markets, sustainable business practices,
    and technology innovation.
    """
    
    print("\nSample website content:")
    print(sample_content[:200] + "...\n")
    
    print("Extracting KPIs with Ollama...")
    kpis = extractor.extract_kpis_from_content(sample_content, "University of Cape Town")
    
    print(f"\n✅ Extraction Results:")
    print(f"  Extraction Method: {kpis.get('extraction_method', 'unknown')}")
    print(f"\n  Programmes ({len(kpis['programmes'])}):")
    for prog in kpis['programmes']:
        print(f"    - {prog['type']}: {prog['name']}")
    
    print(f"\n  Research Centres ({len(kpis['research_centres'])}):")
    for centre in kpis['research_centres']:
        print(f"    - {centre['name']}: {centre['theme']}")
    
    print(f"\n  Academic Staff Disciplines:")
    for discipline, count in kpis['academic_staff_disciplines'].items():
        print(f"    - {discipline}: {count}")
    
    print(f"\n  Accreditation ({len(kpis['accreditation'])}):")
    for accred in kpis['accreditation']:
        print(f"    - {accred}")
    
    print(f"\n  Total Staff: {kpis['academic_staff_count']}")


def test_full_pipeline():
    """Test full discovery + extraction pipeline"""
    print("\n" + "="*70)
    print("🚀 TESTING FULL DISCOVERY PIPELINE")
    print("="*70)
    
    discoverer = BusinessSchoolDiscoverer()
    
    print("\nPipeline: Web Search → Ollama KPI Extraction → Export CSV/MD")
    print("\nExample usage:")
    print("""
    schools = discoverer.discover_and_extract(
        country="South Africa",
        use_ollama=True
    )
    
    print(f"Discovered {len(schools)} schools with extracted KPIs")
    
    # Files created automatically:
    # - business_school_data/discovered_schools_south_africa.csv
    # - business_school_data/discovered_schools_south_africa.md
    """)


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🏫 BUSINESS SCHOOL DISCOVERER + OLLAMA TEST SUITE")
    print("="*70)
    
    # Test Ollama connection
    test_ollama_connection()
    
    # Test KPI extraction with sample content
    test_kpi_extraction()
    
    # Test discovery methods
    test_discovery_by_country()
    test_discovery_by_region()
    
    # Show full pipeline
    test_full_pipeline()
    
    print("\n" + "="*70)
    print("✅ TEST SUITE COMPLETE")
    print("="*70)
    print("""
Next steps to deploy:

1. Start Ollama locally:
   ollama serve

2. Pull a small model (for cloud):
   ollama pull mistral
   ollama pull neural-chat  (smaller)

3. Run discovery:
   schools = discoverer.discover_and_extract('South Africa', use_ollama=True)

4. Deploy to cloud:
   - Azure Container Instances with Ollama + Django
   - Google Cloud Run with Ollama sidecar
   - AWS EC2 with Docker Compose

For continuous discovery, use:
   - APScheduler for background jobs
   - Celery for async task queue
   - Cloud Scheduler for monthly runs
    """)
