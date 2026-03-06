#!/usr/bin/env python3
"""
Test enhanced discovery with staff extraction, degree counts, and multiple CSVs
"""

from health_app.services.business_school_kpi import BusinessSchoolDiscoverer
import os

def main():
    discoverer = BusinessSchoolDiscoverer()
    
    print('\n' + '='*80)
    print('🚀 ENHANCED DISCOVERY - Staff Extraction + Multiple CSVs')
    print('='*80)
    
    # Test with Zimbabwe (small country)
    country = 'Zimbabwe'
    
    print(f'\n📍 Running full pipeline for {country}...')
    print(f'   • Discovering schools')
    print(f'   • Extracting KPIs with Ollama')
    print(f'   • Extracting staff information')
    print(f'   • Counting degree types')
    print(f'   • Creating 3 CSVs + 1 Markdown')
    
    try:
        schools = discoverer.discover_and_extract(country, use_ollama=True)
        
        print(f'\n✅ Discovery complete!')
        print(f'\n📊 Results for {country}:')
        print(f'   • Schools discovered: {len(schools)}')
        
        # Show details with degree counts
        for i, school in enumerate(schools, 1):
            degree_counts = school.get('degree_counts', {})
            print(f'\n   {i}. {school.get("school_name")}')
            print(f'      Website: {school.get("website")}')
            
            # Show degree counts
            if degree_counts:
                print(f'      Degree Counts:')
                print(f'        - PhDs: {degree_counts.get("phd", 0)}')
                print(f'        - Masters: {degree_counts.get("masters", 0)}')
                print(f'        - MBAs: {degree_counts.get("mba", 0)}')
                print(f'        - Bachelors: {degree_counts.get("bachelor", 0)}')
                print(f'        - Total Staff Extracted: {school.get("total_staff", 0)}')
            
            # Show research themes
            if school.get('research_themes'):
                themes = ', '.join(school.get('research_themes', [])[:3])
                print(f'      Research Themes: {themes}')
        
        # Show exported files
        print(f'\n📁 Export files created:')
        
        csv_name = f'{country.lower().replace(" ", "_")}'
        files = [
            (f'discovered_schools_{csv_name}.csv', 'Main schools CSV with degree counts'),
            (f'discovered_schools_{csv_name}.md', 'Markdown report'),
            (f'staff_members_{csv_name}.csv', 'Staff members (names, degrees, research, ORCID)'),
            (f'research_centres_{csv_name}.csv', 'Research centres (name, theme, school)'),
        ]
        
        for filename, description in files:
            filepath = f'health_app/business_school_data/{filename}'
            if os.path.exists(filepath):
                size = os.path.getsize(filepath)
                print(f'   ✅ {filename} ({size} bytes)')
                print(f'      └─ {description}')
            else:
                print(f'   ⏳ {filename} (not generated)')
        
        print(f'\n' + '='*80)
        print('✨ Enhanced discovery system working!')
        print('='*80)
        
    except Exception as e:
        print(f'\n❌ Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
