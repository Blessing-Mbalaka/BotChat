"""
Test BusinessSchoolResearcher with real web search and CSV/Markdown export
"""

import sys
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Add path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from health_app.services.business_school_kpi.researcher import BusinessSchoolResearcher

def test_real_web_search():
    """Test real web search for business schools"""
    print("\n" + "="*70)
    print("🔍 TESTING REAL WEB SEARCH FOR BUSINESS SCHOOLS")
    print("="*70)
    
    researcher = BusinessSchoolResearcher()
    print(f"✓ Researcher initialized")
    print(f"  Research dir: {researcher.research_dir}")
    
    # Test 1: Search all sources
    print("\n📋 Test 1: Searching all sources (AACSB, QS, Times HE, EQUIS)...")
    schools = researcher.research_schools()
    print(f"  Found {len(schools)} schools from web search")
    
    if schools:
        print("\n  Sample schools found:")
        for i, school in enumerate(schools[:5], 1):
            print(f"    {i}. {school['school_name']} ({school['location']['country']})")
            print(f"       Source: {school['source']}")
            print(f"       Accreditation: {', '.join(school['accreditation']) if school['accreditation'] else 'None'}")
            print(f"       Programmes: {len(school['programmes'])} types")
        
        # Check if CSV and MD files were created
        print("\n📁 Checking saved files...")
        md_file = os.path.join(researcher.research_dir, 'business_schools_research.md')
        csv_file = os.path.join(researcher.research_dir, 'business_schools.csv')
        programmes_csv = os.path.join(researcher.research_dir, 'programmes.csv')
        
        if os.path.exists(md_file):
            size = os.path.getsize(md_file)
            print(f"  ✓ Markdown file created: {size} bytes")
            print(f"    Location: {md_file}")
        
        if os.path.exists(csv_file):
            size = os.path.getsize(csv_file)
            print(f"  ✓ Schools CSV created: {size} bytes")
            print(f"    Location: {csv_file}")
        
        if os.path.exists(programmes_csv):
            size = os.path.getsize(programmes_csv)
            print(f"  ✓ Programmes CSV created: {size} bytes")
            print(f"    Location: {programmes_csv}")
        
        # Show CSV content sample
        if os.path.exists(csv_file):
            print("\n📊 CSV Content Preview:")
            with open(csv_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print(f"    Header: {lines[0].strip()}")
                for line in lines[1:4]:  # Show first 3 data rows
                    print(f"    {line.strip()}")
                if len(lines) > 4:
                    print(f"    ... ({len(lines)-1} total rows)")
    else:
        print("\n⚠️  No schools found in web search. WebSearchService may not be available.")
        print("   Note: This is expected if GEMINI_API_KEY or web services are not configured.")
    
    # Test 2: Extract details
    if schools:
        print(f"\n📌 Test 2: Extracting details for first school...")
        school_name = schools[0]['school_name']
        details = researcher.extract_school_details(school_name)
        if details:
            print(f"  ✓ Extracted: {details['school_name']}")
            print(f"    Programmes: {len(details['programmes'])} types offered")
            print(f"    Research centres: {len(details['research_centres'])}")
        else:
            print(f"  ✗ Failed to extract details")
    
    # Test 3: Filter schools
    if schools:
        print(f"\n🌍 Test 3: Filtering schools by location...")
        europe_schools = [s for s in schools if s['location']['region'] == 'Europe']
        na_schools = [s for s in schools if s['location']['region'] == 'North America']
        asia_schools = [s for s in schools if s['location']['region'] == 'Asia Pacific']
        
        print(f"  Europe: {len(europe_schools)} schools")
        print(f"  North America: {len(na_schools)} schools")
        print(f"  Asia Pacific: {len(asia_schools)} schools")
    
    print("\n" + "="*70)
    print("✅ TESTING COMPLETE")
    print("="*70)

if __name__ == '__main__':
    test_real_web_search()
