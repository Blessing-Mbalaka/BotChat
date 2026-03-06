"""
BusinessSchoolKPIService - Extracts, aggregates, and calculates business school KPIs

Provides methods to calculate KPIs like programme counts, staff discipline distribution,
research centre counts, and supports filtering/stratification.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from .researcher import BusinessSchoolResearcher
from .constants import PROGRAMME_TYPES, ACCREDITATIONS, ACADEMIC_DISCIPLINES

logger = logging.getLogger(__name__)


class BusinessSchoolKPIService:
    """Calculate and aggregate business school KPIs"""
    
    def __init__(self):
        """Initialize KPI service with researcher"""
        self.researcher = BusinessSchoolResearcher()
        self.kpi_cache: Dict[str, Any] = {}
    
    def get_school_kpis(self, school_name: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get detailed KPIs for a specific school
        
        Args:
            school_name: Name of the business school
            filters: Optional filters (programme_type, accreditation, etc.)
            
        Returns:
            Dictionary with all KPIs for the school
        """
        logger.info(f"📊 Computing KPIs for: {school_name}")
        
        school = self.researcher.extract_school_details(school_name)
        if not school:
            return {
                'error': f'School not found: {school_name}',
                'school_name': school_name,
                'success': False
            }
        
        # Count programmes by type
        programme_counts = self.researcher.count_programmes_by_type(school_name)
        
        # Apply filters if specified
        if filters:
            programme_counts = self._apply_programme_filters(programme_counts, filters)
        
        # Get staff disciplines
        staff_disciplines = self.researcher.get_academic_staff_disciplines(school_name)
        
        # Count research centres
        research_centres = self.researcher.get_research_centres(school_name)
        
        # Build KPI object
        kpis = {
            'school_name': school_name,
            'location': school.get('location', {}),
            'accreditation': school.get('accreditation', []),
            'founded_year': school.get('founded_year'),
            'website': school.get('website'),
            'success': True,
            'kpis': {
                'total_programmes': sum(programme_counts.values()),
                'programmes_by_type': programme_counts,
                'total_research_centres': len(research_centres),
                'research_centres': research_centres,
                'academic_staff_disciplines': staff_disciplines,
                'total_academic_staff': sum(staff_disciplines.values()),
                'unique_disciplines': len(staff_disciplines),
                'accreditations_count': len(school.get('accreditation', []))
            },
            'source': school.get('source'),
            'data_quality': school.get('data_quality'),
            'computed_at': datetime.now().isoformat()
        }
        
        return kpis
    
    def aggregate_kpis(self, schools: Optional[List[str]] = None, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Aggregate KPIs across multiple schools
        
        Args:
            schools: List of school names to aggregate. If None, uses all found schools.
            filters: Filters to apply (region, accreditation, programme_type)
            
        Returns:
            Aggregated KPI metrics and analysis
        """
        logger.info(f"📈 Aggregating KPIs for {len(schools) if schools else 'all'} schools")
        
        # Get schools to analyze
        if not schools:
            all_schools = self.researcher.research_schools()
            schools = [s['school_name'] for s in all_schools]
        
        # Collect individual school KPIs
        school_kpis_list = []
        for school_name in schools:
            kpi = self.get_school_kpis(school_name, filters)
            if kpi.get('success'):
                school_kpis_list.append(kpi)
        
        # Aggregate metrics
        aggregated = self._aggregate_metrics(school_kpis_list)
        
        return {
            'success': len(school_kpis_list) > 0,
            'schools_analyzed': len(school_kpis_list),
            'total_schools': len(schools),
            'aggregated_kpis': aggregated,
            'school_details': school_kpis_list,
            'computed_at': datetime.now().isoformat()
        }
    
    def get_programme_names(self, school_name: str, programme_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get specific programme names from a school
        
        Args:
            school_name: Name of the business school
            programme_type: Filter by programme type
            
        Returns:
            List of programmes with names and details
        """
        programmes = self.researcher.find_programmes(school_name, programme_type)
        return [
            {
                'name': p.get('name'),
                'type': p.get('type'),
                'duration_months': p.get('duration_months'),
                'enrollment': p.get('enrollment')
            }
            for p in programmes
        ]
    
    def get_kpis_by_filter(self, filter_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get KPIs filtered by specific criteria
        
        Args:
            filter_dict: Dictionary with filter criteria:
                - region: Geographic region
                - accreditation: Accreditation standard
                - programme_type: Specific programme type
                - min_staff: Minimum academic staff
                
        Returns:
            Filtered KPI results
        """
        logger.info(f"🔍 Filtering KPIs by: {filter_dict}")
        
        # Get all schools
        all_schools = self.researcher.research_schools()
        
        # Apply geography filter
        region = filter_dict.get('region')
        if region:
            all_schools = [s for s in all_schools if s.get('location', {}).get('region') == region]
        
        # Apply accreditation filter
        accreditation = filter_dict.get('accreditation')
        if accreditation:
            all_schools = [s for s in all_schools if accreditation in s.get('accreditation', [])]
        
        # Get school names and aggregate KPIs
        school_names = [s['school_name'] for s in all_schools]
        return self.aggregate_kpis(school_names, filter_dict)
    
    def get_discipline_distribution(self, schools: Optional[List[str]] = None) -> Dict[str, int]:
        """
        Get distribution of academic disciplines across schools
        
        Args:
            schools: List of school names. If None, uses all schools.
            
        Returns:
            Dictionary mapping discipline to total staff count
        """
        if not schools:
            all_schools = self.researcher.research_schools()
            schools = [s['school_name'] for s in all_schools]
        
        discipline_totals = {}
        
        for school_name in schools:
            disciplines = self.researcher.get_academic_staff_disciplines(school_name)
            for disc, count in disciplines.items():
                discipline_totals[disc] = discipline_totals.get(disc, 0) + count
        
        # Sort by count descending
        return dict(sorted(discipline_totals.items(), key=lambda x: x[1], reverse=True))
    
    def get_programme_distribution(self, schools: Optional[List[str]] = None) -> Dict[str, int]:
        """
        Get distribution of programme types across schools
        
        Args:
            schools: List of school names. If None, uses all schools.
            
        Returns:
            Dictionary mapping programme type to total count
        """
        if not schools:
            all_schools = self.researcher.research_schools()
            schools = [s['school_name'] for s in all_schools]
        
        programme_totals = {}
        
        for school_name in schools:
            counts = self.researcher.count_programmes_by_type(school_name)
            for prog_type, count in counts.items():
                programme_totals[prog_type] = programme_totals.get(prog_type, 0) + count
        
        # Sort by count descending
        return dict(sorted(programme_totals.items(), key=lambda x: x[1], reverse=True))
    
    def get_accreditation_distribution(self, schools: Optional[List[str]] = None) -> Dict[str, int]:
        """
        Get distribution of accreditation standards across schools
        
        Args:
            schools: List of school names. If None, uses all schools.
            
        Returns:
            Dictionary mapping accreditation to school count
        """
        if not schools:
            all_schools = self.researcher.research_schools()
            schools = [s['school_name'] for s in all_schools]
        
        accreditation_counts = {}
        
        for school_name in schools:
            school = self.researcher.extract_school_details(school_name)
            if school:
                for accred in school.get('accreditation', []):
                    accreditation_counts[accred] = accreditation_counts.get(accred, 0) + 1
        
        # Sort by count descending
        return dict(sorted(accreditation_counts.items(), key=lambda x: x[1], reverse=True))
    
    # ==================== PRIVATE METHODS ====================
    
    def _apply_programme_filters(self, counts: Dict[str, int], filters: Dict[str, Any]) -> Dict[str, int]:
        """Apply filters to programme counts"""
        if 'programme_type' in filters:
            prog_type = filters['programme_type'].upper()
            return {k: v for k, v in counts.items() if k.upper() == prog_type}
        return counts
    
    def _aggregate_metrics(self, kpi_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate individual school KPIs into summary metrics"""
        if not kpi_list:
            return {
                'total_schools': 0,
                'total_programmes': 0,
                'avg_programmes_per_school': 0,
                'total_research_centres': 0,
                'total_academic_staff': 0,
                'programme_type_distribution': {},
                'discipline_distribution': {},
                'accreditation_distribution': {}
            }
        
        # Calculate totals and averages
        total_programmes = sum(kpi['kpis']['total_programmes'] for kpi in kpi_list)
        total_research_centres = sum(kpi['kpis']['total_research_centres'] for kpi in kpi_list)
        total_staff = sum(kpi['kpis']['total_academic_staff'] for kpi in kpi_list)
        
        # Aggregate programme types
        programme_dist = {}
        for kpi in kpi_list:
            for prog_type, count in kpi['kpis']['programmes_by_type'].items():
                programme_dist[prog_type] = programme_dist.get(prog_type, 0) + count
        
        # Aggregate disciplines
        discipline_dist = {}
        for kpi in kpi_list:
            for disc, count in kpi['kpis']['academic_staff_disciplines'].items():
                discipline_dist[disc] = discipline_dist.get(disc, 0) + count
        
        # Aggregate accreditations
        accreditation_dist = {}
        for kpi in kpi_list:
            for accred in kpi['accreditation']:
                accreditation_dist[accred] = accreditation_dist.get(accred, 0) + 1
        
        return {
            'total_schools': len(kpi_list),
            'total_programmes': total_programmes,
            'avg_programmes_per_school': total_programmes / len(kpi_list) if kpi_list else 0,
            'total_research_centres': total_research_centres,
            'avg_research_centres_per_school': total_research_centres / len(kpi_list) if kpi_list else 0,
            'total_academic_staff': total_staff,
            'avg_staff_per_school': total_staff / len(kpi_list) if kpi_list else 0,
            'programme_type_distribution': dict(sorted(programme_dist.items(), key=lambda x: x[1], reverse=True)),
            'discipline_distribution': dict(sorted(discipline_dist.items(), key=lambda x: x[1], reverse=True)),
            'accreditation_distribution': dict(sorted(accreditation_dist.items(), key=lambda x: x[1], reverse=True))
        }
    
    def clear_cache(self):
        """Clear KPI cache"""
        self.kpi_cache.clear()
        self.researcher.clear_cache()
        logger.info("Cleared KPI and researcher caches")
