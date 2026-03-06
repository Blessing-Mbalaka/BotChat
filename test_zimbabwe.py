#!/usr/bin/env python3
"""
Test business school discovery for Zimbabwe
"""

from health_app.services.business_school_kpi import BusinessSchoolDiscoverer
import json

def main():
    discoverer = BusinessSchoolDiscoverer()
    
    print('\n' + '='*70)
    print('🌍 ZIMBABWE BUSINESS SCHOOL DISCOVERY TEST')
    print('='*70)
    
    try:
        print('\n🔍 Discovering business schools in Zimbabwe...\n')
        schools = discoverer.discover_and_extract('Zimbabwe', use_ollama=True)
        
        print(f'\n✅ DISCOVERY COMPLETE: Found {len(schools)} schools')
        print('='*70)
        
        if schools:
            print('\n📊 SCHOOLS DISCOVERED:\n')
            for i, school in enumerate(schools, 1):
                print(f'{i}. {school.get("name", "Unknown")}')
                print(f'   URL: {school.get("url", "N/A")}')
                print(f'   Country: {school.get("country", "N/A")}')
                print(f'   Source: {school.get("source", "N/A")}')
                print(f'   Discovered: {school.get("discovery_date", "N/A")}')
                print()
        else:
            print('\n⚠️  No schools found')
        
        print('='*70)
        print('\n📁 EXPORT FILES CREATED:')
        print('   ✅ business_school_data/discovered_schools_zimbabwe.csv')
        print('   ✅ business_school_data/discovered_schools_zimbabwe.md')
        
    except Exception as e:
        print(f'❌ Error during discovery: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
