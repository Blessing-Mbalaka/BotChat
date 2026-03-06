"""
Management command to list all African countries and statistics
"""
from django.core.management.base import BaseCommand
from django.db.models import Count, Sum
from health_app.models import BusinessSchool, StaffMember, ResearchCentre


class Command(BaseCommand):
    help = 'List all African countries with business school statistics'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n' + '='*80))
        self.stdout.write(self.style.WARNING('🌍 AFRICAN COUNTRIES - BUSINESS SCHOOL DISCOVERY'))
        self.stdout.write(self.style.SUCCESS('='*80 + '\n'))

        # Get all African countries
        countries = BusinessSchool.objects.filter(
            region='Africa'
        ).values('country').distinct().order_by('country')

        if not countries:
            self.stdout.write(self.style.ERROR('❌ No countries found in database'))
            return

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
            mba_count = schools.aggregate(Sum('mba_count'))['mba_count__sum'] or 0
            bachelor_count = schools.aggregate(Sum('bachelor_count'))['bachelor_count__sum'] or 0

            total_schools += school_count
            total_staff += staff_count
            total_research += research_count

            self.stdout.write(f"{idx}. {country.upper()}")
            self.stdout.write(f"   Schools:        {school_count}")
            self.stdout.write(f"   Staff Members:  {staff_count}")
            self.stdout.write(f"   Research:       {research_count}")
            self.stdout.write(f"   PhDs:           {phd_count}")
            self.stdout.write(f"   Masters:        {masters_count}")
            self.stdout.write(f"   MBAs:           {mba_count}")
            self.stdout.write(f"   Bachelors:      {bachelor_count}")
            self.stdout.write('')

        self.stdout.write(self.style.SUCCESS('='*80))
        self.stdout.write(self.style.WARNING('📊 TOTAL STATISTICS (Africa)'))
        self.stdout.write(self.style.SUCCESS('='*80))
        self.stdout.write(f'Total Countries:    {len(countries)}')
        self.stdout.write(f'Total Schools:      {total_schools}')
        self.stdout.write(f'Total Staff:        {total_staff}')
        self.stdout.write(f'Total Research:     {total_research}')
        self.stdout.write(self.style.SUCCESS('='*80 + '\n'))
