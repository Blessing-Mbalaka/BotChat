#!/usr/bin/env python
"""
List all African countries and their business school statistics
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'health_project.settings')
django.setup()

from health_app.models import BusinessSchool, StaffMember, ResearchCentre
from django.db.models import Count, Sum

print("\n" + "="*80)
print("🌍 AFRICAN COUNTRIES - BUSINESS SCHOOL DISCOVERY")
print("="*80 + "\n")

# Get all African countries
countries = BusinessSchool.objects.filter(
    region='Africa'
).values('country').distinct().order_by('country')

if not countries:
    print("❌ No countries found in database")
else:
    total_schools = 0
    total_staff = 0
    total_research = 0
    
    for idx, country_obj in enumerate(countries, 1):
        country = country_obj['country']
        
        # Get stats for this country
        schools = BusinessSchool.objects.filter(country=country)
        school_count = schools.count()
        
        staff_count = StaffMember.objects.filter(
            school__country=country
        ).count()
        
        research_count = ResearchCentre.objects.filter(
            school__country=country
        ).count()
        
        phd_count = schools.aggregate(Sum('phd_count'))['phd_count__sum'] or 0
        masters_count = schools.aggregate(Sum('masters_count'))['masters_count__sum'] or 0
        
        total_schools += school_count
        total_staff += staff_count
        total_research += research_count
        
        print(f"{idx}. {country.upper()}")
        print(f"   Schools:        {school_count}")
        print(f"   Staff Members:  {staff_count}")
        print(f"   Research:       {research_count}")
        print(f"   PhDs:           {phd_count}")
        print(f"   Masters:        {masters_count}")
        print()
    
    print("="*80)
    print(f"📊 TOTAL STATISTICS (Africa)")
    print("="*80)
    print(f"Total Countries:    {len(countries)}")
    print(f"Total Schools:      {total_schools}")
    print(f"Total Staff:        {total_staff}")
    print(f"Total Research:     {total_research}")
    print("="*80 + "\n")
