import os
import csv
from django.core.management.base import BaseCommand
from django.utils import timezone
from pathlib import Path
from health_app.models import BusinessSchool, StaffMember, ResearchCentre, DiscoveryJob


class Command(BaseCommand):
    help = 'Import business school data from CSV files'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--continent',
            type=str,
            default='Africa',
            help='Continent to import (Africa, Europe, Asia, North America, South America, Oceania)'
        )
        parser.add_argument(
            '--country',
            type=str,
            default=None,
            help='Specific country to import (optional)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before import'
        )
    
    def handle(self, *args, **options):
        continent = options['continent']
        country = options['country']
        clear_data = options['clear']
        
        self.stdout.write(f"\n{'='*80}")
        self.stdout.write(f"IMPORTING BUSINESS SCHOOL DATA".center(80))
        self.stdout.write(f"{'='*80}\n")
        
        # Get data directory
        data_dir = Path(__file__).parent.parent.parent.parent / 'health_app' / 'business_school_data'
        self.stdout.write(f"[DATA] Data directory: {data_dir}\n")
        
        if not data_dir.exists():
            self.stdout.write(self.style.ERROR(f"[ERROR] Data directory not found: {data_dir}"))
            return
        
        # Clear existing data if requested
        if clear_data:
            self.stdout.write("[CLEAR] Clearing existing data...")
            BusinessSchool.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("[OK] Data cleared\n"))
        
        # Find CSV files
        if country:
            pattern = f"discovered_schools_{country.lower().replace(' ', '_')}.csv"
            csv_files = list(data_dir.glob(pattern))
            staff_files = list(data_dir.glob(f"staff_members_{country.lower().replace(' ', '_')}.csv"))
        else:
            csv_files = sorted(data_dir.glob("discovered_schools_*.csv"))
            staff_files = sorted(data_dir.glob("staff_members_*.csv"))
        
        if not csv_files:
            self.stdout.write(self.style.WARNING(f"[WARN] No CSV files found"))
            return
        
        self.stdout.write(f"[INFO] Found {len(csv_files)} school CSV files\n")
        
        # Import schools
        schools_imported = 0
        for csv_file in csv_files:
            if self._import_schools(csv_file, continent):
                schools_imported += 1
        
        self.stdout.write(f"\n[OK] Imported {schools_imported} school files")
        
        # Import staff members
        staff_imported = 0
        for staff_file in staff_files:
            if self._import_staff(staff_file):
                staff_imported += 1
        
        if staff_files:
            self.stdout.write(f"[OK] Imported {staff_imported} staff files\n")
        
        # Summary
        total_schools = BusinessSchool.objects.count()
        total_staff = StaffMember.objects.count()
        
        self.stdout.write(f"{'='*80}")
        self.stdout.write(f"IMPORT SUMMARY".center(80))
        self.stdout.write(f"{'='*80}\n")
        self.stdout.write(f"  [OK] Total Schools in Database: {total_schools}")
        self.stdout.write(f"  [OK] Total Staff Members: {total_staff}")
        self.stdout.write(f"\n")
    
    def _import_schools(self, csv_file, continent):
        """Import schools from CSV file"""
        try:
            self.stdout.write(f"  Importing {csv_file.name}...")
            
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                imported = 0
                
                for row in reader:
                    if not row.get('School Name'):
                        continue
                    
                    # Create or update school
                    school, created = BusinessSchool.objects.update_or_create(
                        name=row.get('School Name').strip(),
                        country=row.get('Country', '').strip(),
                        defaults={
                            'continent': row.get('Continent', continent).strip(),
                            'region': row.get('Continent', continent).strip(),
                            'website': row.get('Website', '').strip() or None,
                            'programme_count': int(row.get('Programme Count', 0) or 0),
                            'phd_count': int(row.get('PhDs Count', 0) or 0),
                            'masters_count': int(row.get('Masters Count', 0) or 0),
                            'mba_count': int(row.get('MBAs Count', 0) or 0),
                            'bachelor_count': int(row.get('Bachelor Count', 0) or 0),
                            'research_centres': row.get('Research Centres', '').strip(),
                            'research_themes': row.get('Research Themes', '').strip(),
                            'total_staff_extracted': int(row.get('Total Staff Extracted', 0) or 0),
                            'accreditation': row.get('Accreditation', '').strip(),
                        }
                    )
                    
                    if created:
                        imported += 1
            
            self.stdout.write(self.style.SUCCESS(f"    [OK] {imported} schools imported"))
            return True
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"    [ERR] Error: {e}"))
            return False
    
    def _import_staff(self, staff_file):
        """Import staff members from CSV file"""
        try:
            self.stdout.write(f"  Importing {staff_file.name}...")
            
            with open(staff_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                imported = 0
                
                for row in reader:
                    if not row.get('Staff Name') or not row.get('School Name'):
                        continue
                    
                    # Find school
                    try:
                        school = BusinessSchool.objects.get(
                            name=row.get('School Name').strip()
                        )
                    except BusinessSchool.DoesNotExist:
                        continue
                    
                    # Create or update staff member
                    staff, created = StaffMember.objects.update_or_create(
                        name=row.get('Staff Name').strip(),
                        school=school,
                        defaults={
                            'degree': row.get('Degree', 'unknown').lower(),
                            'research_interests': row.get('Research Interests', '').strip(),
                            'orcid': row.get('ORCID', '').strip() or None,
                            'profile_url': row.get('URL', '').strip() or None,
                        }
                    )
                    
                    if created:
                        imported += 1
            
            self.stdout.write(self.style.SUCCESS(f"    [OK] {imported} staff members imported"))
            return True
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"    [ERR] Error: {e}"))
            return False
