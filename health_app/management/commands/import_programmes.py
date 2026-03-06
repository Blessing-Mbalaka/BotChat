"""
Management command to parse and import programmes from business school CSV data
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from health_app.models import BusinessSchool, Programme
from pathlib import Path
import csv


class Command(BaseCommand):
    help = 'Parse and import programmes from business school discovery CSV files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--region',
            type=str,
            default='Africa',
            help='Region to import programmes for (default: Africa)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing programmes before import',
        )

    def handle(self, *args, **options):
        region = options['region']
        clear_existing = options['clear']
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*80))
        self.stdout.write(self.style.WARNING('📚 IMPORTING PROGRAMMES FROM DISCOVERY DATA'))
        self.stdout.write(self.style.SUCCESS('='*80 + '\n'))

        # Get data directory
        data_dir = Path(__file__).parent.parent.parent / 'business_school_data'
        
        if clear_existing:
            Programme.objects.all().delete()
            self.stdout.write(self.style.WARNING('Cleared existing programmes'))
        
        total_programmes = 0
        
        # Find school CSV files
        csv_files = sorted(data_dir.glob(f'discovered_schools_*.csv'))
        
        if not csv_files:
            self.stdout.write(self.style.ERROR(f'❌ No CSV files found in {data_dir}'))
            return
        
        self.stdout.write(f'📁 Found {len(csv_files)} school CSV files\n')
        
        for csv_file in csv_files:
            try:
                with open(csv_file, encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    
                    for row in reader:
                        school_name = row.get('School Name', '').strip()
                        country = row.get('Country', '').strip()
                        programmes_str = row.get('Programmes', '').strip()
                        website = row.get('Website', '').strip()
                        
                        if not school_name or not country:
                            continue
                        
                        # Find school
                        try:
                            school = BusinessSchool.objects.get(name=school_name, country=country)
                        except BusinessSchool.DoesNotExist:
                            self.stdout.write(self.style.WARNING(f'⚠️  School not found: {school_name} ({country})'))
                            continue
                        
                        # Parse programmes
                        if programmes_str:
                            programme_list = [p.strip() for p in programmes_str.split(';') if p.strip()]
                            
                            for prog_name in programme_list:
                                # Try to infer level from programme name
                                level = self._infer_level(prog_name)
                                
                                # Get source URL
                                source_url = website if website else None
                                
                                try:
                                    programme, created = Programme.objects.get_or_create(
                                        school=school,
                                        name=prog_name,
                                        level=level,
                                        defaults={
                                            'source_url': source_url
                                        }
                                    )
                                    
                                    if created:
                                        total_programmes += 1
                                
                                except Exception as e:
                                    self.stdout.write(
                                        self.style.ERROR(f'❌ Error creating programme "{prog_name}": {str(e)}')
                                    )
            
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Error reading {csv_file.name}: {str(e)}'))
        
        # Update programme_count on schools
        for school in BusinessSchool.objects.all():
            school.programme_count = school.programmes.count()
            school.save(update_fields=['programme_count'])
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*80))
        self.stdout.write(f'✅ Imported {total_programmes} programmes')
        self.stdout.write('='*80 + '\n')
    
    def _infer_level(self, programme_name):
        """Infer programme level from name"""
        prog_lower = programme_name.lower()
        
        if 'phd' in prog_lower or 'doctoral' in prog_lower:
            return 'phd'
        elif 'mba' in prog_lower:
            return 'mba'
        elif 'master' in prog_lower or 'masters' in prog_lower:
            return 'masters'
        elif 'bachelor' in prog_lower or 'bsc' in prog_lower or 'ba' in prog_lower:
            return 'bachelor'
        elif 'executive' in prog_lower:
            return 'executive'
        elif 'postgraduate' in prog_lower:
            return 'postgraduate'
        else:
            return 'other'
