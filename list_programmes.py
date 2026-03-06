#!/usr/bin/env python
"""
Display all imported programmes
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'health_project.settings')
django.setup()

from health_app.models import Programme

programmes = Programme.objects.select_related('school').all()
print('\n' + '='*80)
print('📚 PROGRAMMES DISCOVERED')
print('='*80 + '\n')

for idx, prog in enumerate(programmes, 1):
    url_display = prog.source_url if prog.source_url else "N/A"
    print(f'{idx}. {prog.name}')
    print(f'   Level:  {prog.level.upper()}')
    print(f'   School: {prog.school.name} ({prog.school.country})')
    print(f'   URL:    {url_display}')
    print()

print('='*80)
print(f'Total programmes: {programmes.count()}')
print('='*80 + '\n')

# Also show by level
print('📊 PROGRAMMES BY LEVEL:')
print('='*80)
from django.db.models import Count
by_level = Programme.objects.values('level').annotate(count=Count('id')).order_by('level')
for item in by_level:
    print(f"  {item['level'].upper()}: {item['count']}")
print('='*80 + '\n')
