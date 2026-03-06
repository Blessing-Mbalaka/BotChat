#!/usr/bin/env python
"""Test enhanced discovery for all African countries"""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from health_app.services.business_school_kpi import BusinessSchoolDiscoverer

def test_all_african_countries():
    print("\n" + "="*70)
    print("COMPREHENSIVE AFRICAN BUSINESS SCHOOL DISCOVERY TEST")
    print("="*70 + "\n")
    
    discoverer = BusinessSchoolDiscoverer()
    countries = ['Zimbabwe', 'South Africa', 'Nigeria', 'Kenya', 'Ethiopia', 'Ghana', 'Morocco', 'Botswana']
    
    total_schools = 0
    total_files = 0
    
    for country in countries:
        print(f"\n{country}:")
        print("-" * 50)
        
        # Run discovery for this country
        try:
            results = discoverer.discover_and_extract(country, use_ollama=False)
            print(f"   ✅ Schools discovered: {len(results)}")
            total_schools += len(results)
            
            # Check for exported files
            cache_dir = discoverer.cache_dir
            country_prefix = country.lower().replace(' ', '_')
            
            files = [
                f'discovered_schools_{country_prefix}.csv',
                f'discovered_schools_{country_prefix}.md',
                f'staff_members_{country_prefix}.csv',
                f'research_centres_{country_prefix}.csv'
            ]
            
            found_count = 0
            for filename in files:
                filepath = os.path.join(cache_dir, filename)
                if os.path.exists(filepath):
                    size = os.path.getsize(filepath)
                    print(f"   ✅ {filename} ({size:,} bytes)")
                    found_count += 1
                    total_files += 1
            
            if found_count < 4:
                print(f"   ⚠️  Only {found_count}/4 export files generated")
                for filename in files:
                    fp = os.path.join(cache_dir, filename)
                    if not os.path.exists(fp):
                        print(f"      - Missing: {filename}")
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Summary
    print(f"\n" + "="*70)
    print(f"SUMMARY")
    print("="*70)
    print(f"Total Schools Discovered: {total_schools}")
    print(f"Total Export Files Generated: {total_files}")
    print(f"Expected Files: {len(countries) * 4}")
    print(f"Completion Rate: {(total_files / (len(countries) * 4) * 100):.1f}%")
    print(f"\n✨ African Discovery Test Complete!\n")

if __name__ == '__main__':
    test_all_african_countries()
