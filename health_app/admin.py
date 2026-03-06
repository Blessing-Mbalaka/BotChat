from django.contrib import admin
from health_app.models import BusinessSchool, Programme, StaffMember, ResearchCentre, DiscoveryJob


@admin.register(BusinessSchool)
class BusinessSchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'region', 'programme_count', 'phd_count', 'total_staff_extracted')
    list_filter = ('region', 'country', 'accreditation')
    search_fields = ('name', 'country')
    readonly_fields = ('discovered_date', 'last_updated', 'total_degree_holders')
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'country', 'region', 'website', 'source')
        }),
        ('Programmes', {
            'fields': ('programme_count',)
        }),
        ('Degrees Offered', {
            'fields': ('phd_count', 'masters_count', 'mba_count', 'bachelor_count', 'total_degree_holders')
        }),
        ('Research', {
            'fields': ('research_centres', 'research_themes', 'research_centre_count')
        }),
        ('Staff', {
            'fields': ('academic_staff_count', 'total_staff_extracted')
        }),
        ('Accreditation', {
            'fields': ('accreditation',)
        }),
        ('Metadata', {
            'fields': ('discovered_date', 'last_updated'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Programme)
class ProgrammeAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'school', 'source_url')
    list_filter = ('level', 'school__country', 'school__region')
    search_fields = ('name', 'school__name')
    readonly_fields = ('discovered_date', 'last_updated')
    fieldsets = (
        ('Programme Info', {
            'fields': ('school', 'name', 'level')
        }),
        ('Source', {
            'fields': ('source_url',)
        }),
        ('Metadata', {
            'fields': ('discovered_date', 'last_updated'),
            'classes': ('collapse',)
        }),
    )


@admin.register(StaffMember)
class StaffMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'degree', 'school', 'orcid')
    list_filter = ('degree', 'school__country', 'school__region')
    search_fields = ('name', 'school__name', 'orcid')
    readonly_fields = ('discovered_date', 'last_updated')


@admin.register(ResearchCentre)
class ResearchCentreAdmin(admin.ModelAdmin):
    list_display = ('name', 'theme', 'school')
    list_filter = ('theme', 'school__country', 'school__region')
    search_fields = ('name', 'theme', 'school__name')
    readonly_fields = ('discovered_date', 'last_updated')


@admin.register(DiscoveryJob)
class DiscoveryJobAdmin(admin.ModelAdmin):
    list_display = ('region', 'status', 'schools_discovered', 'staff_extracted', 'started_at')
    list_filter = ('status', 'region', 'started_at')
    readonly_fields = ('started_at', 'completed_at')
    fieldsets = (
        ('Job Info', {
            'fields': ('region', 'status')
        }),
        ('Results', {
            'fields': ('schools_discovered', 'staff_extracted', 'research_centres_found')
        }),
        ('Timeline', {
            'fields': ('started_at', 'completed_at')
        }),
        ('Error Details', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
    )
