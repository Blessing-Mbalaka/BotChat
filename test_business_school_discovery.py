#!/usr/bin/env python3
"""
Test business school discovery with realistic school names
Demonstrates the discoverer working with known universities
"""

import os
import sys
import json
from pathlib import Path

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from health_app.services.business_school_kpi import (
    BusinessSchoolDiscoverer,
    OllamaKPIExtractor
)

def test_manual_discovery():
    """Test with manually specified business school URLs"""
    print("\n" + "="*70)
    print("🏫 MANUAL BUSINESS SCHOOL DISCOVERY TEST")
    print("="*70)
    
    # Real business schools in South Africa
    schools = [
        {
            "name": "University of Cape Town (UCT) Graduate School of Business",
            "url": "https://www.gsb.uct.ac.za",
            "country": "South Africa"
        },
        {
            "name": "University of Pretoria Gordon Institute of Business Science",
            "url": "https://www.gibs.co.za",
            "country": "South Africa"
        },
        {
            "name": "Wits Business School",
            "url": "https://www.wits.ac.za/bbs/",
            "country": "South Africa"
        },
        {
            "name": "Stellenbosch University Business School",
            "url": "https://www.usb.ac.za",
            "country": "South Africa"
        }
    ]
    
    discoverer = BusinessSchoolDiscoverer()
    extractor = OllamaKPIExtractor()
    
    print(f"\n📍 Testing with {len(schools)} known South African business schools\n")
    
    for i, school in enumerate(schools, 1):
        print(f"\n{i}️⃣  {school['name']}")
        print(f"   URL: {school['url']}")
        print(f"   Country: {school['country']}")
        
        # Try to fetch content
        try:
            content = discoverer._fetch_website_content(school['url'], max_chars=5000)
            if content and len(content) > 100:
                print(f"   ✅ Retrieved {len(content)} chars of content")
                
                # Extract KPIs
                print(f"   🤖 Extracting KPIs with Ollama...")
                kpis = extractor.extract_kpis_from_content(content, school['name'])
                
                print(f"   📊 KPIs Found:")
                print(f"      - Programmes: {len(kpis.get('programmes', []))} types")
                print(f"      - Research Centres: {len(kpis.get('research_centres', []))}")
                print(f"      - Academic Staff: {kpis.get('academic_staff_count', 'N/A')}")
                print(f"      - Accreditation: {', '.join(kpis.get('accreditation', ['None']))}")
                
            else:
                print(f"   ⚠️  Content fetch returned < 100 chars (network issue)")
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:100]}")
    
    return schools

def test_cached_schools():
    """Show previously discovered schools from cache"""
    print("\n" + "="*70)
    print("💾 CACHED SCHOOLS FROM PREVIOUS DISCOVERY")
    print("="*70)
    
    discoverer = BusinessSchoolDiscoverer()
    
    # Load cache file if exists
    cache_file = Path("health_app/business_school_data/discovered_schools.json")
    if cache_file.exists():
        try:
            with open(cache_file, 'r') as f:
                cache = json.load(f)
            
            print(f"\n📦 Cache file found: {cache_file}")
            print(f"📊 Countries in cache: {list(cache.keys())}")
            
            for country, data in cache.items():
                if isinstance(data, dict) and 'schools' in data:
                    schools = data['schools']
                    print(f"\n🌍 {country}: {len(schools)} schools")
                    for school in schools[:3]:
                        print(f"   - {school.get('name', 'Unknown')}")
                    if len(schools) > 3:
                        print(f"   ... and {len(schools) - 3} more")
        except Exception as e:
            print(f"⚠️  Could not read cache: {e}")
    else:
        print(f"\n📭 No cache file found yet at {cache_file}")
        print("   Run discovery to create cache: discoverer.discover_and_extract('South Africa')")

def test_ollama_modes():
    """Test both Ollama and fallback pattern matching modes"""
    print("\n" + "="*70)
    print("🤖 OLLAMA VS PATTERN MATCHING COMPARISON")
    print("="*70)
    
    extractor = OllamaKPIExtractor()
    
    # Check Ollama connection
    status = extractor.test_connection()
    print(f"\n🔌 Ollama Connection Status: {status}")
    
    sample_content = """
    University of Johannesburg Business School
    
    Our MBA programs:
    - Full-time MBA (2 years)
    - Executive MBA (18 months)
    - Master of Science in Business Analytics
    
    SAICA accredited accounting programme
    AACSB International accreditation
    
    Research Institutes:
    - Centre for Entrepreneurship
    - Institute for Research and Development
    
    Faculty: 120 academic staff members
    Guest lecturers from EQUIS accredited schools
    """
    
    print(f"\nSample Content: {len(sample_content)} chars")
    print(f"- MBA programmes mentioned")
    print(f"- AACSB and EQUIS accreditations")
    print(f"- 120 staff members")
    print(f"- Research institutes listed")
    
    print(f"\n📍 Extracting with Ollama (if available)...")
    kpis_ollama = extractor.extract_kpis_from_content(sample_content, "University of Johannesburg")
    
    print(f"✅ Extraction Results:")
    print(f"   Programmes: {len(kpis_ollama.get('programmes', []))} found")
    print(f"   Accreditations: {kpis_ollama.get('accreditation', [])}")
    print(f"   Research Centres: {len(kpis_ollama.get('research_centres', []))} found")
    print(f"   Academic Staff: {kpis_ollama.get('academic_staff_count', 'N/A')}")

def test_export_format():
    """Show what export files look like"""
    print("\n" + "="*70)
    print("📄 EXPORT FORMAT SAMPLES")
    print("="*70)
    
    print("\n📊 CSV Export Format:")
    print("""
    Name,URL,Country,Programmes,Research_Centres,Academic_Staff,Accreditation,Last_Updated
    "University of Cape Town GSB","https://www.gsb.uct.ac.za","South Africa",5,3,150,"AACSB;EQUIS","2024-01-15"
    """)
    
    print("\n📝 Markdown Export Format:")
    print("""
    # Discovered Business Schools - South Africa
    
    ## University of Cape Town Graduate School of Business
    - **URL:** https://www.gsb.uct.ac.za
    - **Programmes:** MBA, Executive MBA, Master of Finance, ... (5 total)
    - **Accreditation:** AACSB, EQUIS
    - **Research Centres:** 3 institutes
    - **Academic Staff:** ~150 faculty
    - **Discovered:** 2024-01-15
    """)

def main():
    """Run all tests"""
    print("\n╔" + "="*68 + "╗")
    print("║" + " "*15 + "BUSINESS SCHOOL DISCOVERY DEMONSTRATION" + " "*13 + "║")
    print("╚" + "="*68 + "╝")
    
    # Test 1: Manual discovery with real schools
    test_manual_discovery()
    
    # Test 2: Show cached schools
    test_cached_schools()
    
    # Test 3: Ollama modes
    test_ollama_modes()
    
    # Test 4: Export formats
    test_export_format()
    
    print("\n" + "="*70)
    print("✅ DEMONSTRATION COMPLETE")
    print("="*70)
    print("""
Next Steps:

1. ✅ Manual Test: Fetch real UCT/GIBS/Wits sites and extract KPIs

2. 🚀 Auto-Discovery: Run full discovery pipeline
   ```python
   discoverer = BusinessSchoolDiscoverer()
   schools = discoverer.discover_and_extract('South Africa', use_ollama=True)
   print(f"Found {len(schools)} schools with extracted KPIs")
   # Auto-creates CSV and Markdown exports
   ```

3. ☁️  Cloud Deployment:
   - Package with Docker + Ollama
   - Deploy to Azure Container Instances
   - Run monthly via Cloud Scheduler
   - Monitor via logs and exports

4. 📊 Analytics: Read CSV exports into Pandas for analysis
   ```python
   import pandas as pd
   df = pd.read_csv('business_school_data/discovered_schools_South Africa.csv')
   print(df.describe())
   ```
    """)

if __name__ == '__main__':
    main()
