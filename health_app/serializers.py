from rest_framework import serializers
from health_app.models import BusinessSchool, StaffMember, ResearchCentre, DiscoveryJob, Programme


class ProgrammeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Programme
        fields = ('id', 'name', 'level', 'source_url', 'discovered_date')


class StaffMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffMember
        fields = ('id', 'name', 'degree', 'research_interests', 'orcid', 'profile_url', 'discovered_date')


class ResearchCentreSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResearchCentre
        fields = ('id', 'name', 'theme', 'description', 'website_url', 'discovered_date')


class BusinessSchoolDetailSerializer(serializers.ModelSerializer):
    staff_members = StaffMemberSerializer(many=True, read_only=True)
    research_centres_data = ResearchCentreSerializer(many=True, read_only=True)
    programmes = ProgrammeSerializer(many=True, read_only=True)
    total_degree_holders = serializers.ReadOnlyField()
    
    class Meta:
        model = BusinessSchool
        fields = (
            'id', 'name', 'country', 'continent', 'region', 'website',
            'programme_count',
            'phd_count', 'masters_count', 'mba_count', 'bachelor_count',
            'total_degree_holders',
            'research_centres', 'research_themes', 'research_centre_count',
            'academic_staff_count', 'total_staff_extracted',
            'accreditation', 'source', 'discovered_date', 'last_updated',
            'staff_members', 'research_centres_data', 'programmes'
        )


class BusinessSchoolSerializer(serializers.ModelSerializer):
    total_degree_holders = serializers.ReadOnlyField()
    staff_count = serializers.SerializerMethodField()
    
    class Meta:
        model = BusinessSchool
        fields = (
            'id', 'name', 'country', 'continent', 'region', 'website',
            'programme_count',
            'phd_count', 'masters_count', 'mba_count', 'bachelor_count',
            'total_degree_holders',
            'research_themes', 'research_centre_count',
            'total_staff_extracted', 'staff_count',
            'accreditation', 'discovered_date'
        )
        ordering = ['-total_staff_extracted']
    
    def get_staff_count(self, obj):
        return obj.staff_members.count()


class DiscoveryJobSerializer(serializers.ModelSerializer):
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = DiscoveryJob
        fields = (
            'id', 'region', 'status',
            'schools_discovered', 'staff_extracted', 'research_centres_found',
            'started_at', 'completed_at', 'duration',
            'error_message'
        )
    
    def get_duration(self, obj):
        return obj.duration_seconds()
