#!/usr/bin/env python
"""Verify continent field assignment after global import"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'health_project.settings')

import django
django.setup()

from health_app.models import BusinessSchool
from django.db.models import Count

# Count schools by continent
print("\n" + "="*70)
print("SCHOOLS BY CONTINENT - GLOBAL DATABASE")
print("="*70)

continents_stats = BusinessSchool.objects.values('continent').annotate(count=Count('id')).order_by('-count')
total = 0
for stat in continents_stats:
    print(f"  {stat['continent']:25} - {stat['count']:3} schools")
    total += stat['count']

print(f"\n  {'TOTAL':25} - {total:3} schools")

# Show country distribution for each continent
print("\n" + "="*70)
print("TOP COUNTRIES BY CONTINENT")
print("="*70)

for continent in ['Africa', 'Europe', 'Asia', 'North America', 'South America', 'Oceania']:
    print(f"\n  {continent}:")
    countries = BusinessSchool.objects.filter(
        continent=continent
    ).values('country').annotate(count=Count('id')).order_by('-count')[:5]
    
    for country in countries:
        print(f"    - {country['country']:30} {country['count']:2} schools")

# Show sample schools
print("\n" + "="*70)
print("SAMPLE SCHOOLS FROM EACH CONTINENT")
print("="*70)

for continent in ['Africa', 'Europe', 'Asia', 'North America', 'South America', 'Oceania']:
    sample = BusinessSchool.objects.filter(continent=continent).first()
    if sample:
        print(f"  {continent:25} - {sample.name}")
        print(f"    {'':25}   {sample.country} | Website: {sample.website or 'N/A'}")

print("\n" + "="*70 + "\n")
