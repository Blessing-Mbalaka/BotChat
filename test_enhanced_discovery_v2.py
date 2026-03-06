#!/usr/bin/env python
"""Test enhanced discovery with proper CSV export"""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from health_app.services.business_school_kpi import BusinessSchoolDiscoverer

def test_zimbabwe():
    print("\n" + "="*60)
    print("Testing Enhanced Discovery for Zimbabwe")
    print("="*60 + "\n")
    
    discoverer = BusinessSchoolDiscoverer()
    
    # Run discovery for Zimbabwe
    results = discoverer.discover_and_extract('Zimbabwe', use_ollama=False)
    
    print(f"\n✅ Discovery Results:")
    print(f"   - Schools found: {len(results)}")
    
    for i, school in enumerate(results, 1):
        print(f"\n   {i}. {school.get('name', 'Unknown')}")
        
        # Show degree counts
        degree_counts = school.get('degree_counts', {})
        if degree_counts:
            print(f"      Degree Counts:")
            print(f"        - PhDs: {degree_counts.get('phd', 0)}")
            print(f"        - Masters: {degree_counts.get('masters', 0)}")
            print(f"        - MBAs: {degree_counts.get('mba', 0)}")
            print(f"        - Bachelors: {degree_counts.get('bachelor', 0)}")
        
        # Show research themes
        themes = school.get('research_themes', [])
        if themes:
            print(f"      Research Themes: {', '.join(themes[:3])}")
        
        # Show staff count
        total_staff = school.get('total_staff', 0)
        if total_staff:
            print(f"      Total Staff Extracted: {total_staff}")
    
    # Check exported files
    print(f"\n📁 Checking Exported Files:")
    cache_dir = discoverer.cache_dir
    
    files_to_check = [
        'discovered_schools_zimbabwe.csv',
        'discovered_schools_zimbabwe.md',
        'staff_members_zimbabwe.csv',
        'research_centres_zimbabwe.csv'
    ]
    
    for filename in files_to_check:
        filepath = os.path.join(cache_dir, filename)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"   ✅ {filename} ({size} bytes)")
            
            # For CSV files, show first few lines
            if filename.endswith('.csv'):
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        print(f"      Header: {lines[0].strip()[:70]}...")
                        if len(lines) > 1:
                            print(f"      Rows: {len(lines) - 1}")
        else:
            print(f"   ⚠️  {filename} (NOT FOUND)")
    
    print(f"\n✨ Enhanced discovery test complete!")

if __name__ == '__main__':
    test_zimbabwe()
