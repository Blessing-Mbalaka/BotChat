#!/usr/bin/env python
"""Test API endpoints with global data"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'health_project.settings')

import django
django.setup()

from rest_framework.test import APIRequestFactory
from health_app.api_views import BusinessSchoolViewSet, ProgrammeViewSet
from django.http import QueryDict

factory = APIRequestFactory()

print("\n" + "="*70)
print("TESTING REST API ENDPOINTS - GLOBAL DATA")
print("="*70)

# Test 1: List all schools
print("\n[TEST 1] GET /api/schools/ - List all schools")
viewset = BusinessSchoolViewSet.as_view({'get': 'list'})
request = factory.get('/api/schools/')
response = viewset(request)
print(f"  Response Status: {response.status_code}")
if isinstance(response.data, list):
    print(f"  Total schools returned: {len(response.data)}")
else:
    print(f"  Total schools: {response.data.get('count', 'N/A')}")

# Test 2: Get school detail with programmes
print("\n[TEST 2] GET /api/schools/{id}/ - Detail view with programmes")
from health_app.models import BusinessSchool
first_school = BusinessSchool.objects.first()
if first_school:
    viewset_detail = BusinessSchoolViewSet.as_view({'get': 'retrieve'})
    request = factory.get(f'/api/schools/{first_school.id}/')
    response = viewset_detail(request, pk=first_school.id)
    print(f"  Response Status: {response.status_code}")
    if response.status_code == 200:
        data = response.data
        print(f"  School: {data.get('name', 'N/A')}")
        print(f"  Country: {data.get('country', 'N/A')}")
        print(f"  Continent: {data.get('continent', 'N/A')}")
        print(f"  Website: {data.get('website', 'N/A')}")
        print(f"  Programmes: {len(data.get('programmes', []))} linked")

# Test 3: Get continent stats
print("\n[TEST 3] DB Query - Schools per continent")
from django.db.models import Count
stats = BusinessSchool.objects.values('continent').annotate(count=Count('id')).order_by('-count')
for stat in stats:
    print(f"  {stat['continent']:20} - {stat['count']:3} schools")

# Test 4: Programmes endpoint
print("\n[TEST 4] GET /api/programmes/ - List programmes")
viewset_prog = ProgrammeViewSet.as_view({'get': 'list'})
request = factory.get('/api/programmes/')
response = viewset_prog(request)
print(f"  Response Status: {response.status_code}")
if isinstance(response.data, list):
    print(f"  Total programmes: {len(response.data)}")
else:
    print(f"  Total programmes: {response.data.get('count', 'N/A')}")

# Test 5: School counts by degree type
print("\n[TEST 5] Schools with degree offerings")
from django.db.models import Q
schools_with_phd = BusinessSchool.objects.filter(phd_count__gt=0).count()
schools_with_mba = BusinessSchool.objects.filter(mba_count__gt=0).count()
schools_with_bachelor = BusinessSchool.objects.filter(bachelor_count__gt=0).count()

print(f"  Schools with PhDs: {schools_with_phd}")
print(f"  Schools with MBAs: {schools_with_mba}")
print(f"  Schools with Bachelors: {schools_with_bachelor}")

# Test 6: Sample schools from each continent
print("\n[TEST 6] Sample schools from each continent")
for continent in ['Africa', 'Europe', 'Asia', 'North America', 'South America', 'Oceania']:
    sample = BusinessSchool.objects.filter(continent=continent).first()
    if sample:
        print(f"  {continent:20} - {sample.name[:50]}")

print("\n" + "="*70 + "\n")
