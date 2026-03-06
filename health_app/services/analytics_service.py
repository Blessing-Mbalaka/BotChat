"""
Data Analysis Service - Generate insights and reports from business school data
"""

from django.db.models import Count, Q, Avg
from health_app.models import BusinessSchool, StaffMember, ResearchCentre
import json


class BusinessSchoolAnalytics:
    """Generate analytics and insights from business school data"""
    
    @staticmethod
    def get_global_statistics():
        """Get global statistics across all schools"""
        return {
            'total_schools': BusinessSchool.objects.count(),
            'total_regions': BusinessSchool.objects.values('region').distinct().count(),
            'total_countries': BusinessSchool.objects.values('country').distinct().count(),
            'total_staff': StaffMember.objects.count(),
            'total_research_centres': ResearchCentre.objects.count(),
            'schools_with_phds': BusinessSchool.objects.filter(phd_count__gt=0).count(),
            'schools_with_research': BusinessSchool.objects.filter(research_centres__isnull=False).distinct().count(),
        }
    
    @staticmethod
    def get_regional_analysis():
        """Analyze schools by region"""
        regions = BusinessSchool.objects.values('region').annotate(
            school_count=Count('id'),
            total_staff=Count('staff_members'),
            avg_phds_per_school=Avg('phd_count'),
            avg_masters_per_school=Avg('masters_count'),
        ).order_by('-school_count')
        
        analysis = {}
        for region_data in regions:
            region = region_data['region']
            schools = BusinessSchool.objects.filter(region=region)
            
            analysis[region] = {
                'school_count': region_data['school_count'],
                'total_staff': StaffMember.objects.filter(school__region=region).count(),
                'phd_holders': StaffMember.objects.filter(
                    degree='phd',
                    school__region=region
                ).count(),
                'avg_phds_per_school': round(region_data['avg_phds_per_school'] or 0, 2),
                'avg_masters_per_school': round(region_data['avg_masters_per_school'] or 0, 2),
                'top_schools': [
                    {
                        'name': s.name,
                        'country': s.country,
                        'phd_count': s.phd_count,
                        'staff_count': s.staff_members.count()
                    }
                    for s in schools.order_by('-total_staff_extracted')[:5]
                ]
            }
        
        return analysis
    
    @staticmethod
    def get_country_analysis():
        """Analyze schools by country"""
        countries = BusinessSchool.objects.values('country', 'region').annotate(
            school_count=Count('id'),
            total_staff=Count('staff_members'),
            total_phds=Count('phd_count'),
        ).order_by('-school_count')
        
        analysis = {}
        for country_data in countries:
            country = country_data['country']
            schools = BusinessSchool.objects.filter(country=country)
            
            analysis[country] = {
                'region': country_data['region'],
                'school_count': country_data['school_count'],
                'total_staff': StaffMember.objects.filter(school__country=country).count(),
                'phd_holders': StaffMember.objects.filter(
                    degree='phd',
                    school__country=country
                ).count(),
                'schools': [
                    {
                        'name': s.name,
                        'phd_count': s.phd_count,
                        'masters_count': s.masters_count,
                        'mba_count': s.mba_count,
                        'staff_count': s.staff_members.count()
                    }
                    for s in schools
                ]
            }
        
        return analysis
    
    @staticmethod
    def get_staff_analysis():
        """Analyze staff distribution"""
        total_staff = StaffMember.objects.count()
        
        return {
            'total_staff': total_staff,
            'by_degree': {
                'phd': StaffMember.objects.filter(degree='phd').count(),
                'masters': StaffMember.objects.filter(degree='masters').count(),
                'mba': StaffMember.objects.filter(degree='mba').count(),
                'bachelor': StaffMember.objects.filter(degree='bachelor').count(),
                'unknown': StaffMember.objects.filter(degree='unknown').count(),
            },
            'with_research_interests': StaffMember.objects.exclude(
                research_interests=''
            ).count(),
            'with_orcid': StaffMember.objects.exclude(orcid__isnull=True).count(),
            'phd_holders_by_region': {
                region: StaffMember.objects.filter(
                    degree='phd',
                    school__region=region
                ).count()
                for region in ['Africa', 'Europe', 'Asia', 'Americas']
            }
        }
    
    @staticmethod
    def get_research_analysis():
        """Analyze research centres and themes"""
        all_themes = ResearchCentre.objects.values('theme').annotate(
            count=Count('id')
        ).order_by('-count')
        
        schools_with_research = BusinessSchool.objects.filter(
            research_centres_data__isnull=False
        ).distinct().count()
        
        return {
            'total_centres': ResearchCentre.objects.count(),
            'schools_with_research': schools_with_research,
            'top_themes': [
                {
                    'theme': item['theme'],
                    'count': item['count'],
                    'percentage': round((item['count'] / ResearchCentre.objects.count() * 100), 2)
                }
                for item in all_themes[:10]
            ]
        }
    
    @staticmethod
    def get_school_ranking(sort_by='staff'):
        """Get ranked schools by various metrics"""
        schools = BusinessSchool.objects.all()
        
        if sort_by == 'staff':
            schools = schools.order_by('-total_staff_extracted')
        elif sort_by == 'phd':
            schools = schools.order_by('-phd_count')
        elif sort_by == 'research':
            schools = schools.order_by('-research_centre_count')
        elif sort_by == 'programmes':
            schools = schools.order_by('-programme_count')
        
        ranking = []
        for idx, school in enumerate(schools[:50], 1):
            ranking.append({
                'rank': idx,
                'name': school.name,
                'country': school.country,
                'region': school.region,
                'staff_extracted': school.total_staff_extracted,
                'phd_count': school.phd_count,
                'masters_count': school.masters_count,
                'mba_count': school.mba_count,
                'programme_count': school.programme_count,
                'research_themes': school.research_themes
            })
        
        return {
            'sort_by': sort_by,
            'ranking': ranking
        }
    
    @staticmethod
    def get_excellence_metrics():
        """Identify schools of excellence"""
        phd_leaders = BusinessSchool.objects.filter(
            phd_count__gt=0
        ).order_by('-phd_count')[:10]
        
        research_leaders = BusinessSchool.objects.filter(
            research_centre_count__gt=0
        ).order_by('-research_centre_count')[:10]
        
        staff_leaders = BusinessSchool.objects.filter(
            total_staff_extracted__gt=0
        ).order_by('-total_staff_extracted')[:10]
        
        return {
            'phd_leaders': [
                {'name': s.name, 'country': s.country, 'phd_count': s.phd_count}
                for s in phd_leaders
            ],
            'research_leaders': [
                {'name': s.name, 'country': s.country, 'centres': s.research_centre_count}
                for s in research_leaders
            ],
            'staff_leaders': [
                {'name': s.name, 'country': s.country, 'staff': s.total_staff_extracted}
                for s in staff_leaders
            ]
        }
    
    @staticmethod
    def export_report_json():
        """Export complete analysis as JSON"""
        report = {
            'generated_at': str(__import__('datetime').datetime.now()),
            'global_statistics': BusinessSchoolAnalytics.get_global_statistics(),
            'regional_analysis': BusinessSchoolAnalytics.get_regional_analysis(),
            'staff_analysis': BusinessSchoolAnalytics.get_staff_analysis(),
            'research_analysis': BusinessSchoolAnalytics.get_research_analysis(),
            'excellence_metrics': BusinessSchoolAnalytics.get_excellence_metrics(),
        }
        
        return json.dumps(report, indent=2)
