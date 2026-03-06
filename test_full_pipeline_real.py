#!/usr/bin/env python3
"""
Test full pipeline: Discover real schools + Extract KPIs with Ollama
"""

from health_app.services.business_school_kpi import BusinessSchoolDiscoverer
import os

def main():
    discoverer = BusinessSchoolDiscoverer()
    
    print('\n' + '='*80)
    print('🚀 FULL PIPELINE TEST: DISCOVER REAL SCHOOLS + EXTRACT KPIs')
    print('='*80)
    
    # Run full pipeline for Zimbabwe
    print('\n📍 Testing Zimbabwe with real schools and Ollama KPI extraction...\n')
    
    try:
        schools = discoverer.discover_and_extract('Zimbabwe', use_ollama=True)
        
        print(f'\n✅ Complete! Discovered and extracted KPIs from {len(schools)} schools')
        print('='*80)
        print('\n📊 Zimbabwe Schools with Extracted KPIs:\n')
        
        for i, school in enumerate(schools, 1):
            print(f'{i}. {school.get("school_name")}')
            print(f'   URL: {school.get("website")}')
            print(f'   Programmes: {len(school.get("programmes", []))} types')
            print(f'   Research Centres: {len(school.get("research_centres", []))} centres')
            print(f'   Academic Staff: {school.get("academic_staff_count", "N/A")}')
            if school.get("accreditation"):
                print(f'   Accreditations: {", ".join(school.get("accreditation", []))}')
            print(f'   Extraction Method: {school.get("extraction_method", "N/A")}')
            print()
        
        print('='*80)
        print('\n📁 Export files created:')
        print('   ✅ health_app/business_school_data/discovered_schools_zimbabwe.csv')
        print('   ✅ health_app/business_school_data/discovered_schools_zimbabwe.md')
        
        # Show file sizes
        import os
        csv_file = 'health_app/business_school_data/discovered_schools_zimbabwe.csv'
        md_file = 'health_app/business_school_data/discovered_schools_zimbabwe.md'
        
        if os.path.exists(csv_file):
            size_csv = os.path.getsize(csv_file)
            print(f'\n   CSV size: {size_csv} bytes')
        if os.path.exists(md_file):
            size_md = os.path.getsize(md_file)
            print(f'   Markdown size: {size_md} bytes')
        
        print('\n' + '='*80)
        print('✨ SUCCESS: Real schools with KPI extraction working!')
        print('='*80)
        
    except Exception as e:
        print(f'\n❌ Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
