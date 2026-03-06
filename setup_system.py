#!/usr/bin/env python
"""
Setup and test script for Business School Discovery System
Demonstrates all three implementations: API, Dashboard, and Analytics
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'health_project.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.core.management import call_command
from health_app.models import BusinessSchool, StaffMember, ResearchCentre
from health_app.services.analytics_service import BusinessSchoolAnalytics


def print_header(text):
    print(f"\n{'='*80}")
    print(f"{text.center(80)}")
    print(f"{'='*80}\n")


def print_success(text):
    print(f"✅ {text}")


def print_info(text):
    print(f"ℹ️  {text}")


def print_warning(text):
    print(f"⚠️  {text}")


def main():
    print_header("🚀 BUSINESS SCHOOL DISCOVERY SYSTEM - SETUP & TEST")
    
    # Step 1: Run migrations
    print_info("Step 1: Running Django migrations...")
    try:
        call_command('migrate', verbosity=0)
        print_success("Migrations completed")
    except Exception as e:
        print_warning(f"Migration warning: {e}")
    
    # Step 2: Import CSV data
    print_info("Step 2: Importing business school data from CSVs...")
    try:
        call_command('import_schools', region='Africa', verbosity=0)
        print_success("Data imported successfully")
    except Exception as e:
        print_warning(f"Import error: {e}")
    
    # Display statistics
    print_header("📊 DATABASE STATISTICS")
    
    schools_count = BusinessSchool.objects.count()
    staff_count = StaffMember.objects.count()
    research_count = ResearchCentre.objects.count()
    
    print(f"Business Schools: {schools_count}")
    print(f"Staff Members: {staff_count}")
    print(f"Research Centres: {research_count}")
    
    # Show analytics
    print_header("📈 ANALYTICS INSIGHTS")
    
    analytics = BusinessSchoolAnalytics()
    
    # Global statistics
    stats = analytics.get_global_statistics()
    print(f"Total Schools: {stats['total_schools']}")
    print(f"Total Countries: {stats['total_countries']}")
    print(f"Total Staff: {stats['total_staff']}")
    print(f"PhD Leaders: {stats['schools_with_phds']}")
    
    # Staff analysis
    print_header("👥 STAFF ANALYSIS")
    staff_analysis = analytics.get_staff_analysis()
    print(f"Total Staff: {staff_analysis['total_staff']}")
    print(f"  - PhD holders: {staff_analysis['by_degree']['phd']}")
    print(f"  - Masters holders: {staff_analysis['by_degree']['masters']}")
    print(f"  - MBA holders: {staff_analysis['by_degree']['mba']}")
    
    # Top schools
    print_header("🏆 TOP SCHOOLS")
    ranking = analytics.get_school_ranking(sort_by='staff')
    for item in ranking['ranking'][:5]:
        print(f"{item['rank']}. {item['name']} ({item['country']}) - {item['staff_extracted']} staff")
    
    # API Endpoints
    print_header("📡 REST API ENDPOINTS")
    endpoints = [
        ("GET", "/api/schools/", "List all schools"),
        ("GET", "/api/schools/stats/", "Global statistics"),
        ("GET", "/api/schools/by-region/?region=Africa", "Schools by region"),
        ("GET", "/api/schools/with-phds/", "Schools with PhDs"),
        ("GET", "/api/staff/", "List all staff"),
        ("GET", "/api/staff/phds/", "PhD holders"),
        ("GET", "/api/staff/stats/", "Staff statistics"),
        ("GET", "/api/research/", "Research centres"),
        ("GET", "/api/research/themes/", "Research themes"),
    ]
    
    for method, path, description in endpoints:
        print(f"{method:6} {path:40} - {description}")
    
    # Dashboard
    print_header("🌐 WEB DASHBOARD")
    print("Access the interactive dashboard at:")
    print("  http://localhost:8000/dashboard/")
    print("\nFeatures:")
    print("  ✓ Global statistics cards")
    print("  ✓ Regional distribution charts")
    print("  ✓ Staff degree level analysis")
    print("  ✓ Research themes visualization")
    print("  ✓ Top schools rankings")
    
    # Next steps
    print_header("🚀 NEXT STEPS")
    print("1. Start Django server:")
    print("   python manage.py runserver")
    print("")
    print("2. Access the dashboard:")
    print("   http://localhost:8000/dashboard/")
    print("")
    print("3. Explore the API:")
    print("   http://localhost:8000/api/schools/")
    print("")
    print("4. Access Django admin:")
    print("   http://localhost:8000/admin/")
    print("")
    print("5. Generate analytics reports:")
    print("   python manage.py shell")
    print("   >>> from health_app.services.analytics_service import BusinessSchoolAnalytics")
    print("   >>> analytics = BusinessSchoolAnalytics()")
    print("   >>> print(analytics.export_report_json())")
    
    print_header("✨ SETUP COMPLETE!")


if __name__ == '__main__':
    main()
