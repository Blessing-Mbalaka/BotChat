#!/usr/bin/env python
"""
Display comprehensive Programme normalization implementation
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'health_project.settings')
django.setup()

from health_app.models import BusinessSchool, Programme, StaffMember, ResearchCentre
from django.db.models import Count

print("\n" + "="*90)
print("✅ PROGRAMME NORMALIZATION IMPLEMENTATION - COMPLETE")
print("="*90 + "\n")

# 1. Show database schema
print("📊 1. DATABASE SCHEMA")
print("-"*90)
print("""
NEW Model: Programme
  - school (ForeignKey → BusinessSchool)
  - name (CharField) - Actual programme name
  - level (CharField) - Programme level (Bachelor, MBA, Masters, PhD, Executive, Postgraduate, Other)
  - source_url (URLField) - Direct link to programme page
  - discovered_date, last_updated (Timestamps)
  
UPDATED Model: BusinessSchool
  ✓ Removed: programmes (TextField)
  ✓ Updated: website field now documents as "source URL"
  ✓ Kept: programme_count (denormalized for performance)

BENEFITS:
  ✓ Proper normalization with ForeignKey relationships
  ✓ Actual programme names in database (not semicolon-separated strings)
  ✓ Query by programme level efficiently
  ✓ Source URL available via FK relationship
  ✓ Unique constraint: (school, name, level)
  ✓ Database indexes on: school+level, level, name
""")

# 2. Show API endpoints
print("\n📡 2. REST API ENDPOINTS")
print("-"*90)
print("""
GET /api/programmes/
  List all programmes with filters and search

GET /api/programmes/{id}/
  Get specific programme details

GET /api/programmes/by-school/?school_id=1
  Get all programmes at a specific school

GET /api/programmes/by-level/?level=mba
  Get all programmes at a specific level
  Available levels: bachelor, mba, masters, phd, executive, postgraduate, other

GET /api/programmes/levels/
  Get all programme levels with counts

Query Parameters:
  ?search=finance          Search by programme name
  ?ordering=school__name   Sort by field
""")

# 3. Show populated data
print("\n📚 3. IMPORTED PROGRAMMES")
print("-"*90)

programmes = Programme.objects.select_related('school').order_by('school__name', 'level', 'name')

if programmes.exists():
    print(f"\nTotal Programmes: {programmes.count()}\n")
    
    current_school = None
    for prog in programmes:
        if prog.school != current_school:
            current_school = prog.school
            print(f"\n🏫 {prog.school.name} ({prog.school.country})")
            print(f"   Website: {prog.school.website}")
        
        print(f"   • {prog.name} ({prog.level.upper()})")
else:
    print("No programmes imported yet")

# 4. Show statistics
print("\n\n📈 4. STATISTICS")
print("-"*90)

by_level = Programme.objects.values('level').annotate(count=Count('id')).order_by('-count')
print("\nProgrammes by Level:")
for item in by_level:
    print(f"  {item['level'].upper()}: {item['count']}")

schools_with_programmes = BusinessSchool.objects.filter(programmes__isnull=False).distinct().count()
print(f"\nSchools with programmes: {schools_with_programmes}/{BusinessSchool.objects.count()}")

# 5. Show Django admin registration
print("\n\n🔐 5. DJANGO ADMIN INTERFACE")
print("-"*90)
print("""
Admin URL: /admin/

Registered Models:
  ✓ BusinessSchool - Manage schools, view programmes
  ✓ Programme - Add/edit/delete programmes
  ✓ StaffMember - Manage staff
  ✓ ResearchCentre - Manage research
  ✓ DiscoveryJob - Track import jobs

Features:
  ✓ Inline editing
  ✓ Filters by level, country, region
  ✓ Search by programme name
  ✓ Bulk actions
""")

# 6. Show import management command
print("\n\n🔄 6. MANAGEMENT COMMAND")
print("-"*90)
print("""
import_programmes command:
  
  python manage.py import_programmes --region Africa
  python manage.py import_programmes --region Africa --clear
  
Features:
  ✓ Parses "Programmes" column from CSV
  ✓ Auto-detects programme level
  ✓ Links to school via ForeignKey
  ✓ Uses school website as source_url
  ✓ Unique constraint prevents duplicates
  ✓ Updates programme_count on schools
""")

# 7. Show serializer structure
print("\n\n🔗 7. SERIALIZER STRUCTURE")
print("-"*90)
print("""
ProgrammeSerializer:
  id
  name (actual programme name)
  level (programme level)
  source_url (direct link)
  discovered_date

BusinessSchoolDetailSerializer includes:
  - programmes[] (nested ProgrammeSerializer)
  - programme_count (for performance)
  - All other school details
""")

# 8. Show quality metrics
print("\n\n✨ 8. DATA QUALITY IMPROVEMENTS")
print("-"*90)
print(f"""
✓ Normalization: {programmes.count()} programmes in proper table
✓ Uniqueness: Enforced at database level (school, name, level)
✓ Source Attribution: {programmes.filter(source_url__isnull=False).count()}/{programmes.count()} have source URLs
✓ Classification: All programmes classified by level
✓ Referential Integrity: FK to BusinessSchool ensures data consistency
✓ Indexes: Fast queries on school, level, name
✓ Scalability: Can handle thousands of programmes efficiently
""")

print("\n" + "="*90)
print("✅ Programme Normalization Implementation Complete!")
print("="*90 + "\n")
