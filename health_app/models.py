from django.db import models
from django.utils import timezone

class BusinessSchool(models.Model):
    """Business school model"""
    
    REGION_CHOICES = [
        ('Africa', 'Africa'),
        ('Europe', 'Europe'),
        ('Asia', 'Asia'),
        ('Americas', 'Americas'),
        ('Oceania', 'Oceania'),
    ]
    
    CONTINENT_CHOICES = [
        ('Africa', 'Africa'),
        ('Asia', 'Asia'),
        ('Europe', 'Europe'),
        ('North America', 'North America'),
        ('South America', 'South America'),
        ('Oceania', 'Oceania'),
    ]
    
    # Basic info
    name = models.CharField(max_length=500, db_index=True)
    country = models.CharField(max_length=100, db_index=True)
    continent = models.CharField(max_length=50, choices=CONTINENT_CHOICES, default='Africa', db_index=True, help_text="Continent for global normalization")
    region = models.CharField(max_length=50, choices=REGION_CHOICES, default='Africa', help_text="Regional grouping")
    website = models.URLField(blank=True, null=True, help_text="School's official website URL - used as source")
    
    # Programmes count (denormalized for performance, actual programmes in Programme model)
    programme_count = models.IntegerField(default=0)
    
    # Degree statistics
    phd_count = models.IntegerField(default=0)
    masters_count = models.IntegerField(default=0)
    mba_count = models.IntegerField(default=0)
    bachelor_count = models.IntegerField(default=0)
    
    # Research
    research_centres = models.TextField(blank=True, help_text="Semicolon-separated research centres")
    research_themes = models.TextField(blank=True, help_text="Semicolon-separated research themes")
    research_centre_count = models.IntegerField(default=0)
    
    # Staff
    academic_staff_count = models.IntegerField(default=0)
    total_staff_extracted = models.IntegerField(default=0)
    
    # Accreditation
    accreditation = models.CharField(max_length=500, blank=True, help_text="e.g., AACSB, EQUIS, AMBA")
    
    # Metadata
    source = models.CharField(max_length=100, default='Verified Database')
    discovered_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('name', 'country')
        indexes = [
            models.Index(fields=['continent', 'country']),
            models.Index(fields=['country', 'region']),
            models.Index(fields=['region']),
            models.Index(fields=['phd_count']),
            models.Index(fields=['masters_count']),
        ]
        verbose_name_plural = "Business Schools"
    
    def __str__(self):
        return f"{self.name} ({self.country})"
    
    @property
    def total_degree_holders(self):
        return self.phd_count + self.masters_count + self.mba_count + self.bachelor_count


class Programme(models.Model):
    """Normalized programme/degree offering model"""
    
    LEVEL_CHOICES = [
        ('bachelor', 'Bachelor'),
        ('mba', 'MBA'),
        ('masters', 'Masters'),
        ('phd', 'PhD'),
        ('executive', 'Executive'),
        ('postgraduate', 'Postgraduate'),
        ('other', 'Other'),
    ]
    
    school = models.ForeignKey(BusinessSchool, on_delete=models.CASCADE, related_name='programmes')
    
    # Programme info
    name = models.CharField(max_length=300, db_index=True, help_text="Actual programme name (e.g., 'MBA in Finance', 'PhD in Management')")
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, help_text="Programme level/type")
    
    # Source
    source_url = models.URLField(blank=True, null=True, help_text="Direct URL to programme page on school website")
    
    # Metadata
    discovered_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('school', 'name', 'level')
        indexes = [
            models.Index(fields=['school', 'level']),
            models.Index(fields=['level']),
            models.Index(fields=['name']),
        ]
        verbose_name_plural = "Programmes"
    
    def __str__(self):
        return f"{self.name} ({self.level.upper()}) - {self.school.name}"


class StaffMember(models.Model):
    """Staff member model"""
    
    DEGREE_CHOICES = [
        ('phd', 'PhD'),
        ('masters', 'Masters'),
        ('mba', 'MBA'),
        ('bachelor', 'Bachelor'),
        ('unknown', 'Unknown'),
    ]
    
    school = models.ForeignKey(BusinessSchool, on_delete=models.CASCADE, related_name='staff_members')
    
    # Personal info
    name = models.CharField(max_length=300, db_index=True)
    degree = models.CharField(max_length=20, choices=DEGREE_CHOICES, default='unknown')
    
    # Research
    research_interests = models.TextField(blank=True, help_text="Semicolon-separated research interests")
    
    # External identifiers
    orcid = models.CharField(max_length=50, blank=True, null=True, unique=True)
    
    # Links
    profile_url = models.URLField(blank=True, null=True)
    
    # Metadata
    discovered_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('name', 'school')
        indexes = [
            models.Index(fields=['school', 'degree']),
            models.Index(fields=['degree']),
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.degree.upper()}) - {self.school.name}"


class ResearchCentre(models.Model):
    """Research centre model"""
    
    school = models.ForeignKey(BusinessSchool, on_delete=models.CASCADE, related_name='research_centres_data')
    
    # Centre info
    name = models.CharField(max_length=300, db_index=True)
    theme = models.CharField(max_length=200, db_index=True)
    
    # Description
    description = models.TextField(blank=True)
    website_url = models.URLField(blank=True, null=True)
    
    # Metadata
    discovered_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('name', 'school')
        indexes = [
            models.Index(fields=['school', 'theme']),
            models.Index(fields=['theme']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.theme}) - {self.school.name}"


class DiscoveryJob(models.Model):
    """Track discovery job executions"""
    
    REGION_CHOICES = [
        ('Africa', 'Africa'),
        ('Europe', 'Europe'),
        ('Asia', 'Asia'),
        ('Americas', 'Americas'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    region = models.CharField(max_length=50, choices=REGION_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Stats
    schools_discovered = models.IntegerField(default=0)
    staff_extracted = models.IntegerField(default=0)
    research_centres_found = models.IntegerField(default=0)
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    # Metadata
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.region} - {self.status} ({self.started_at.strftime('%Y-%m-%d %H:%M')})"
    
    def duration_seconds(self):
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
