from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from health_app.models import BusinessSchool, StaffMember, ResearchCentre, DiscoveryJob, Programme
from health_app.serializers import (
    BusinessSchoolSerializer, BusinessSchoolDetailSerializer,
    StaffMemberSerializer, ResearchCentreSerializer, DiscoveryJobSerializer, ProgrammeSerializer
)


class BusinessSchoolViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for business schools
    
    Endpoints:
        GET /api/schools/ - List all schools
        GET /api/schools/{id}/ - Get school details with staff and research
        GET /api/schools/by-region/{region}/ - Schools in a region
        GET /api/schools/by-country/{country}/ - Schools in a country
        GET /api/schools/with-phds/ - Schools with PhDs
        GET /api/schools/stats/ - Global statistics
    """
    
    queryset = BusinessSchool.objects.all()
    serializer_class = BusinessSchoolSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'country', 'region']
    ordering_fields = ['total_staff_extracted', 'phd_count', 'name']
    ordering = ['-total_staff_extracted']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BusinessSchoolDetailSerializer
        return BusinessSchoolSerializer
    
    @action(detail=False, methods=['get'])
    def by_region(self, request):
        """Get schools by region"""
        region = request.query_params.get('region')
        if not region:
            return Response({'error': 'Region parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
        schools = self.queryset.filter(region=region)
        serializer = self.get_serializer(schools, many=True)
        
        return Response({
            'region': region,
            'count': schools.count(),
            'schools': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def by_country(self, request):
        """Get schools by country"""
        country = request.query_params.get('country')
        if not country:
            return Response({'error': 'Country parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
        schools = self.queryset.filter(country=country)
        serializer = self.get_serializer(schools, many=True)
        
        return Response({
            'country': country,
            'count': schools.count(),
            'schools': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def with_phds(self, request):
        """Get schools with PhD programmes"""
        schools = self.queryset.filter(phd_count__gt=0).order_by('-phd_count')
        serializer = self.get_serializer(schools, many=True)
        
        return Response({
            'count': schools.count(),
            'schools': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get global statistics"""
        total_schools = self.queryset.count()
        total_staff = StaffMember.objects.count()
        total_phds = StaffMember.objects.filter(degree='phd').count()
        total_masters = StaffMember.objects.filter(degree='masters').count()
        total_mbas = StaffMember.objects.filter(degree='mba').count()
        
        by_region = self.queryset.values('region').annotate(
            count=Count('id'),
            total_phds=Count('phd_count'),
            total_staff=Count('total_staff_extracted')
        )
        
        return Response({
            'global': {
                'total_schools': total_schools,
                'total_staff': total_staff,
                'total_phds': total_phds,
                'total_masters': total_masters,
                'total_mbas': total_mbas,
            },
            'by_region': list(by_region)
        })
    
    @action(detail=True, methods=['get'])
    def staff(self, request, pk=None):
        """Get all staff members for a school"""
        school = self.get_object()
        staff = school.staff_members.all()
        serializer = StaffMemberSerializer(staff, many=True)
        
        return Response({
            'school': school.name,
            'total_staff': staff.count(),
            'staff': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def research(self, request, pk=None):
        """Get all research centres for a school"""
        school = self.get_object()
        centres = school.research_centres_data.all()
        serializer = ResearchCentreSerializer(centres, many=True)
        
        return Response({
            'school': school.name,
            'total_centres': centres.count(),
            'centres': serializer.data
        })


class StaffMemberViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for staff members
    
    Endpoints:
        GET /api/staff/ - List all staff
        GET /api/staff/{id}/ - Get staff details
        GET /api/staff/by-degree/{degree}/ - Staff by degree level
        GET /api/staff/by-school/{school_id}/ - Staff in a school
        GET /api/staff/search/ - Search staff by name or research interests
    """
    
    queryset = StaffMember.objects.select_related('school').all()
    serializer_class = StaffMemberSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'research_interests', 'school__name']
    ordering_fields = ['name', 'degree', 'discovered_date']
    ordering = ['name']
    
    @action(detail=False, methods=['get'])
    def by_degree(self, request):
        """Get staff by degree level"""
        degree = request.query_params.get('degree')
        if not degree:
            return Response({'error': 'Degree parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
        staff = self.queryset.filter(degree=degree)
        serializer = self.get_serializer(staff, many=True)
        
        return Response({
            'degree': degree,
            'count': staff.count(),
            'staff': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def phds(self, request):
        """Get all PhD holders"""
        staff = self.queryset.filter(degree='phd').order_by('name')
        serializer = self.get_serializer(staff, many=True)
        
        return Response({
            'degree': 'PhD',
            'count': staff.count(),
            'staff': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get staff statistics"""
        return Response({
            'total_staff': self.queryset.count(),
            'phd_holders': self.queryset.filter(degree='phd').count(),
            'masters_holders': self.queryset.filter(degree='masters').count(),
            'mba_holders': self.queryset.filter(degree='mba').count(),
            'bachelors': self.queryset.filter(degree='bachelor').count(),
        })


class ResearchCentreViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for research centres
    
    Endpoints:
        GET /api/research/ - List all research centres
        GET /api/research/{id}/ - Get centre details
        GET /api/research/by-theme/{theme}/ - Research by theme
        GET /api/research/by-school/{school_id}/ - Research in a school
    """
    
    queryset = ResearchCentre.objects.select_related('school').all()
    serializer_class = ResearchCentreSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'theme', 'school__name']
    ordering_fields = ['name', 'theme']
    ordering = ['name']
    
    @action(detail=False, methods=['get'])
    def by_theme(self, request):
        """Get research centres by theme"""
        theme = request.query_params.get('theme')
        if not theme:
            return Response({'error': 'Theme parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
        centres = self.queryset.filter(theme=theme)
        serializer = self.get_serializer(centres, many=True)
        
        return Response({
            'theme': theme,
            'count': centres.count(),
            'centres': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def themes(self, request):
        """Get all research themes"""
        themes = self.queryset.values('theme').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return Response({
            'total_themes': themes.count(),
            'themes': list(themes)
        })


class DiscoveryJobViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for discovery jobs
    
    Endpoints:
        GET /api/jobs/ - List all discovery jobs
        GET /api/jobs/{id}/ - Get job details
        GET /api/jobs/latest/ - Latest discovery job
    """
    
    queryset = DiscoveryJob.objects.all().order_by('-started_at')
    serializer_class = DiscoveryJobSerializer
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get latest discovery job"""
        job = self.queryset.first()
        if not job:
            return Response({'error': 'No jobs found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(job)
        return Response(serializer.data)


class ProgrammeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for programmes/degrees offered
    
    Endpoints:
        GET /api/programmes/ - List all programmes
        GET /api/programmes/{id}/ - Get programme details
        GET /api/programmes/by-school/{school_id}/ - Programmes at a school
        GET /api/programmes/by-level/ - Programmes by level (bachelor, mba, masters, phd)
        GET /api/programmes/levels/ - All programme levels
    """
    
    queryset = Programme.objects.select_related('school').all()
    serializer_class = ProgrammeSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'school__name', 'level']
    ordering_fields = ['name', 'level', 'school__name']
    ordering = ['school__name', 'level', 'name']
    
    @action(detail=False, methods=['get'])
    def by_school(self, request):
        """Get programmes at a specific school"""
        school_id = request.query_params.get('school_id')
        if not school_id:
            return Response({'error': 'School ID parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
        programmes = self.queryset.filter(school_id=school_id)
        serializer = self.get_serializer(programmes, many=True)
        
        return Response({
            'school_id': school_id,
            'count': programmes.count(),
            'programmes': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def by_level(self, request):
        """Get programmes by level"""
        level = request.query_params.get('level')
        if not level:
            return Response({'error': 'Level parameter required (bachelor, mba, masters, phd, executive, postgraduate, other)'}, status=status.HTTP_400_BAD_REQUEST)
        
        programmes = self.queryset.filter(level=level)
        serializer = self.get_serializer(programmes, many=True)
        
        return Response({
            'level': level,
            'count': programmes.count(),
            'programmes': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def levels(self, request):
        """Get all programme levels"""
        levels = self.queryset.values('level').annotate(
            count=Count('id')
        ).order_by('level')
        
        return Response({
            'total_levels': levels.count(),
            'levels': list(levels)
        })
