from django.urls import path, include
from rest_framework.routers import DefaultRouter
from health_app.api_views import (
    BusinessSchoolViewSet, StaffMemberViewSet,
    ResearchCentreViewSet, DiscoveryJobViewSet, ProgrammeViewSet
)

router = DefaultRouter()
router.register(r'schools', BusinessSchoolViewSet, basename='school')
router.register(r'staff', StaffMemberViewSet, basename='staff')
router.register(r'research', ResearchCentreViewSet, basename='research')
router.register(r'jobs', DiscoveryJobViewSet, basename='job')
router.register(r'programmes', ProgrammeViewSet, basename='programme')

urlpatterns = [
    path('', include(router.urls)),
]
