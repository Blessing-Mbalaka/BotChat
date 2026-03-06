#!/usr/bin/env python3
"""
Test discovery and KPI extraction for ALL African countries
"""

from health_app.services.business_school_kpi import BusinessSchoolDiscoverer
import os
import json
from datetime import datetime

def main():
    discoverer = BusinessSchoolDiscoverer()
    
    print('\n' + '='*80)
    print('🌍 DISCOVERING BUSINESS SCHOOLS ACROSS ALL AFRICAN COUNTRIES')
    print('='*80)
    
    # Get African countries from the discoverer
    african_countries = discoverer.REAL_BUSINESS_SCHOOLS.keys()
    
    print(f'\n📍 Found {len(african_countries)} African countries in database:')
    for country in sorted(african_countries):
        count = len(discoverer.REAL_BUSINESS_SCHOOLS[country])
        print(f'   • {country}: {count} verified schools')
    
    results_summary = {}
    
    # Discover and extract KPIs for each country
    for country in sorted(african_countries):
        print(f'\n{"="*80}')
        print(f'🔍 Discovering {country}...')
        print(f'{"="*80}')
        
        try:
            schools = discoverer.discover_and_extract(country, use_ollama=True)
            
            # Collect statistics
            total_schools = len(schools)
            with_programmes = sum(1 for s in schools if s.get('programmes'))
            with_research = sum(1 for s in schools if s.get('research_centres'))
            with_accreditation = sum(1 for s in schools if s.get('accreditation'))
            
            results_summary[country] = {
                'total': total_schools,
                'with_programmes': with_programmes,
                'with_research': with_research,
                'with_accreditation': with_accreditation,
                'status': '✅'
            }
            
            print(f'\n✅ {country}: {total_schools} schools discovered')
            print(f'   • Schools with programmes: {with_programmes}')
            print(f'   • Schools with research centres: {with_research}')
            print(f'   • Schools with accreditations: {with_accreditation}')
            
            for i, school in enumerate(schools, 1):
                prog_count = len(school.get('programmes', []))
                research_count = len(school.get('research_centres', []))
                print(f'\n   {i}. {school.get("school_name")}')
                if prog_count > 0:
                    programmes = [f'{p["name"]}' for p in school.get('programmes', [])]
                    print(f'      Programmes: {", ".join(programmes)}')
                if research_count > 0:
                    research = [f'{r["name"]}' for r in school.get('research_centres', [])]
                    print(f'      Research: {", ".join(research)}')
                if school.get('accreditation'):
                    print(f'      Accreditation: {", ".join(school.get("accreditation", []))}')
                    
        except Exception as e:
            print(f'\n❌ Error discovering {country}: {str(e)[:100]}')
            results_summary[country] = {
                'status': '❌',
                'error': str(e)[:50]
            }
    
    # Print comprehensive summary
    print(f'\n\n{"="*80}')
    print('📊 COMPREHENSIVE SUMMARY - ALL AFRICAN COUNTRIES')
    print('='*80)
    
    total_all_schools = 0
    successful_countries = 0
    
    print('\n')
    for country in sorted(results_summary.keys()):
        result = results_summary[country]
        status = result.get('status', '?')
        
        if status == '✅':
            total = result.get('total', 0)
            progs = result.get('with_programmes', 0)
            research = result.get('with_research', 0)
            accred = result.get('with_accreditation', 0)
            
            print(f'{status} {country:20} | Schools: {total:2} | Programmes: {progs:2} | Research: {research:2} | Accreditation: {accred:2}')
            total_all_schools += total
            successful_countries += 1
        else:
            error = result.get('error', 'Unknown error')
            print(f'{status} {country:20} | Error: {error}')
    
    print(f'\n{"="*80}')
    print(f'✨ DISCOVERY COMPLETE')
    print(f'{"="*80}')
    print(f'\n📈 Statistics:')
    print(f'   • Total countries: {len(results_summary)}')
    print(f'   • Successful: {successful_countries}')
    print(f'   • Total schools discovered: {total_all_schools}')
    print(f'   • Average schools per country: {total_all_schools / successful_countries:.1f}')
    
    print(f'\n📁 Export files created:')
    for country in sorted(african_countries):
        csv_file = f'health_app/business_school_data/discovered_schools_{country.lower().replace(" ", "_")}.csv'
        md_file = f'health_app/business_school_data/discovered_schools_{country.lower().replace(" ", "_")}.md'
        
        if os.path.exists(csv_file):
            print(f'   ✅ {country}: CSV + Markdown')
        else:
            print(f'   ⏳ {country}: Processing...')
    
    print(f'\n{"="*80}')

if __name__ == '__main__':
    main()
