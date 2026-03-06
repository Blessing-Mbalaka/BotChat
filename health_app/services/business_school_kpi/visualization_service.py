"""
BusinessSchoolVisualizationService - Renders stratified business school KPI visualizations

Provides 5 visualization types:
1. KPI Overview bar chart (schools vs total programmes)
2. Expandable detail table (click school → see programmes and centres)
3. Filter controls (region, accreditation, research focus)
4. Cascading selection (school → programme type → specific names)
5. Stats cards (aggregate counts and metrics)
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from .kpi_service import BusinessSchoolKPIService
from .constants import PROGRAMME_TYPES, ACCREDITATIONS, VIZ_TYPES

logger = logging.getLogger(__name__)


class BusinessSchoolVisualizationService:
    """Generate stratified visualizations for business school KPI data"""
    
    def __init__(self):
        """Initialize visualization service with KPI service"""
        self.kpi_service = BusinessSchoolKPIService()
    
    def render_kpi_overview_chart(self, schools: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Render KPI overview bar chart showing schools and total programmes
        
        Args:
            schools: List of school names. If None, uses all schools.
            
        Returns:
            Visualization object for bar chart
        """
        logger.info("📊 Rendering KPI overview chart")
        
        if not schools:
            all_schools = self.kpi_service.researcher.research_schools()
            schools = [s['school_name'] for s in all_schools]
        
        # Prepare chart data
        chart_data = []
        for school_name in schools:
            kpi = self.kpi_service.get_school_kpis(school_name)
            if kpi.get('success'):
                chart_data.append({
                    'school': school_name,
                    'total_programmes': kpi['kpis']['total_programmes'],
                    'research_centres': kpi['kpis']['total_research_centres'],
                    'accreditations': ', '.join(kpi['accreditation']),
                    'staff_count': kpi['kpis']['total_academic_staff']
                })
        
        return {
            'type': VIZ_TYPES['BAR'],
            'title': 'Business School KPI Overview',
            'description': 'Total programmes offered by each business school',
            'xaxis': 'School Name',
            'yaxis': 'Total Programmes',
            'data': chart_data,
            'rows': [
                {'label': 'School', 'field': 'school', 'type': 'string'},
                {'label': 'Total Programmes', 'field': 'total_programmes', 'type': 'number'},
                {'label': 'Research Centres', 'field': 'research_centres', 'type': 'number'},
                {'label': 'Accreditations', 'field': 'accreditations', 'type': 'string'},
                {'label': 'Academic Staff', 'field': 'staff_count', 'type': 'number'}
            ],
            'hover_template': '{school}<br>Programmes: {total_programmes}<br>Research Centres: {research_centres}<br>Staff: {staff_count}',
            'config': {'limit': 10, 'sortBy': 'total_programmes', 'sortOrder': 'desc'},
            'source': 'Business School Researcher',
            'timestamp': datetime.now().isoformat()
        }
    
    def render_expandable_detail_table(self, schools: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Render expandable detail table with drill-down capability
        
        Click school row to expand and see:
        - Individual programme names by type
        - Research centre themes
        - Staff discipline breakdown
        
        Args:
            schools: List of school names. If None, uses all schools.
            
        Returns:
            Visualization object for expandable table
        """
        logger.info("📋 Rendering expandable detail table")
        
        if not schools:
            all_schools = self.kpi_service.researcher.research_schools()
            schools = [s['school_name'] for s in all_schools]
        
        # Prepare table data with nested expandable rows
        table_rows = []
        for school_name in schools:
            kpi = self.kpi_service.get_school_kpis(school_name)
            if kpi.get('success'):
                # Main row
                row = {
                    'school_name': school_name,
                    'total_programmes': kpi['kpis']['total_programmes'],
                    'ma_count': kpi['kpis']['programmes_by_type'].get('MA', 0),
                    'mba_count': kpi['kpis']['programmes_by_type'].get('MBA', 0),
                    'bachelor_count': kpi['kpis']['programmes_by_type'].get('BACHELOR', 0),
                    'postgrad_count': kpi['kpis']['programmes_by_type'].get('POSTGRADUATE', 0),
                    'pdh_count': kpi['kpis']['programmes_by_type'].get('PDH', 0),
                    'certificate_count': kpi['kpis']['programmes_by_type'].get('CERTIFICATE', 0),
                    'research_centres': kpi['kpis']['total_research_centres'],
                    'accreditation': ', '.join(kpi['accreditation']),
                    # Expandable content
                    'expand': True,
                    'expanded_content': {
                        'programmes_by_type': kpi['kpis']['programmes_by_type'],
                        'research_centres': kpi['kpis']['research_centres'],
                        'academic_staff_disciplines': kpi['kpis']['academic_staff_disciplines']
                    }
                }
                table_rows.append(row)
        
        return {
            'type': VIZ_TYPES['EXPANDABLE_TABLE'],
            'title': 'Business School Details - Expandable View',
            'description': 'Click to expand each school and see detailed KPI breakdown',
            'rows': table_rows,
            'columns': [
                {'label': 'School Name', 'field': 'school_name', 'type': 'string', 'width': '25%'},
                {'label': 'Total Programmes', 'field': 'total_programmes', 'type': 'number', 'width': '10%'},
                {'label': 'MA', 'field': 'ma_count', 'type': 'number', 'width': '8%'},
                {'label': 'MBA', 'field': 'mba_count', 'type': 'number', 'width': '8%'},
                {'label': 'Bachelor', 'field': 'bachelor_count', 'type': 'number', 'width': '8%'},
                {'label': 'Postgrad', 'field': 'postgrad_count', 'type': 'number', 'width': '8%'},
                {'label': 'PDH', 'field': 'pdh_count', 'type': 'number', 'width': '8%'},
                {'label': 'Certificates', 'field': 'certificate_count', 'type': 'number', 'width': '8%'},
                {'label': 'Research Centres', 'field': 'research_centres', 'type': 'number', 'width': '8%'},
                {'label': 'Accreditation', 'field': 'accreditation', 'type': 'string', 'width': '10%'}
            ],
            'expand_template': {
                'programmes_section': {
                    'title': 'Programmes by Type',
                    'type': 'list',
                    'field': 'expanded_content.programmes_by_type'
                },
                'research_centres_section': {
                    'title': 'Research Centres & Themes',
                    'type': 'list',
                    'field': 'expanded_content.research_centres'
                },
                'staff_section': {
                    'title': 'Academic Staff by Discipline',
                    'type': 'list',
                    'field': 'expanded_content.academic_staff_disciplines'
                }
            },
            'config': {'expandable': True, 'striped': True, 'hoverable': True},
            'source': 'Business School KPI Service',
            'timestamp': datetime.now().isoformat()
        }
    
    def render_filter_controls(self) -> Dict[str, Any]:
        """
        Render filter control panel for region, accreditation, research focus
        
        Returns:
            Visualization object for filter panel
        """
        logger.info("🔍 Rendering filter controls")
        
        # Get available options from all schools
        all_schools = self.kpi_service.researcher.research_schools()
        regions = sorted(list(set(s.get('location', {}).get('region') for s in all_schools if s.get('location', {}).get('region'))))
        
        # Get all accreditations
        accreditation_dist = self.kpi_service.get_accreditation_distribution()
        
        return {
            'type': VIZ_TYPES['FILTER_PANEL'],
            'title': 'Business School Filters',
            'description': 'Filter results by region, accreditation, and research focus',
            'filters': [
                {
                    'name': 'region',
                    'label': 'Geographic Region',
                    'type': 'dropdown',
                    'options': regions,
                    'placeholder': 'Select region...',
                    'multi': False
                },
                {
                    'name': 'accreditation',
                    'label': 'Accreditation Standard',
                    'type': 'dropdown',
                    'options': list(accreditation_dist.keys()),
                    'placeholder': 'Select accreditation...',
                    'multi': True
                },
                {
                    'name': 'research_focus',
                    'label': 'Research Focus',
                    'type': 'text',
                    'placeholder': 'e.g., Finance, Entrepreneurship, Sustainability',
                    'multi': False
                }
            ],
            'config': {
                'apply_button': 'Apply Filters',
                'reset_button': 'Reset',
                'live_update': True
            },
            'source': 'Business School Research Database',
            'timestamp': datetime.now().isoformat()
        }
    
    def render_cascading_selection(self) -> Dict[str, Any]:
        """
        Render cascading selection panel: School → Programme Type → Specific Programmes
        
        Returns:
            Visualization object for cascading select
        """
        logger.info("🎓 Rendering cascading selection")
        
        # Get all schools
        all_schools = self.kpi_service.researcher.research_schools()
        school_names = sorted([s['school_name'] for s in all_schools])
        
        # Prepare cascading data structure
        cascading_data = {}
        for school_name in school_names:
            # Get programme types for this school
            programme_counts = self.kpi_service.researcher.count_programmes_by_type(school_name)
            programme_types = list(programme_counts.keys())
            
            cascading_data[school_name] = {
                'programme_types': programme_types,
                'programmes_by_type': {}
            }
            
            # Get specific programme names for each type
            for prog_type in programme_types:
                programmes = self.kpi_service.get_programme_names(school_name, prog_type)
                cascading_data[school_name]['programmes_by_type'][prog_type] = programmes
        
        return {
            'type': VIZ_TYPES['CASCADING_SELECT'],
            'title': 'Business School Programme Explorer',
            'description': 'Select a school, then programme type, then view specific programmes',
            'stages': [
                {
                    'name': 'school',
                    'label': 'Step 1: Select School',
                    'type': 'dropdown',
                    'options': school_names,
                    'placeholder': 'Choose a business school...'
                },
                {
                    'name': 'programme_type',
                    'label': 'Step 2: Select Programme Type',
                    'type': 'dropdown',
                    'depends_on': 'school',
                    'placeholder': 'Choose programme type...'
                },
                {
                    'name': 'specific_programme',
                    'label': 'Step 3: View Specific Programmes',
                    'type': 'list',
                    'depends_on': 'programme_type',
                    'display_fields': ['name', 'duration_months']
                }
            ],
            'cascading_data': cascading_data,
            'config': {
                'step_by_step': True,
                'show_count': True
            },
            'source': 'Business School Research Database',
            'timestamp': datetime.now().isoformat()
        }
    
    def render_stats_cards(self, schools: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Render statistics cards with aggregate counts
        
        Shows:
        - Total schools researched
        - Total programmes
        - Average programmes per school
        - Unique disciplines
        - Total research centres
        
        Args:
            schools: List of school names. If None, uses all schools.
            
        Returns:
            Visualization object for stats cards
        """
        logger.info("📈 Rendering stats cards")
        
        # Get aggregated KPIs
        aggregated = self.kpi_service.aggregate_kpis(schools)
        agg_kpis = aggregated['aggregated_kpis']
        
        # Aggregate programme distribution
        programme_dist = self.kpi_service.get_programme_distribution(schools)
        discipline_dist = self.kpi_service.get_discipline_distribution(schools)
        accreditation_dist = self.kpi_service.get_accreditation_distribution(schools)
        
        return {
            'type': VIZ_TYPES['STATS_CARD'],
            'title': 'Business School Analytics Dashboard',
            'description': 'Key metrics and aggregate statistics',
            'cards': [
                {
                    'title': 'Total Schools Researched',
                    'value': agg_kpis['total_schools'],
                    'unit': 'schools',
                    'icon': '🏫',
                    'color': 'primary'
                },
                {
                    'title': 'Total Programmes',
                    'value': agg_kpis['total_programmes'],
                    'unit': 'programmes',
                    'icon': '🎓',
                    'color': 'success'
                },
                {
                    'title': 'Avg Programmes per School',
                    'value': round(agg_kpis['avg_programmes_per_school'], 1),
                    'unit': 'programmes',
                    'icon': '📊',
                    'color': 'info'
                },
                {
                    'title': 'Total Academic Staff',
                    'value': agg_kpis['total_academic_staff'],
                    'unit': 'staff',
                    'icon': '👥',
                    'color': 'warning'
                },
                {
                    'title': 'Unique Disciplines',
                    'value': len(discipline_dist),
                    'unit': 'disciplines',
                    'icon': '🎯',
                    'color': 'danger'
                },
                {
                    'title': 'Research Centres',
                    'value': agg_kpis['total_research_centres'],
                    'unit': 'centres',
                    'icon': '🔬',
                    'color': 'secondary'
                }
            ],
            'detailed_distributions': {
                'programmes_by_type': self._prepare_distribution_viz(programme_dist, 'Programme Type'),
                'disciplines': self._prepare_distribution_viz(discipline_dist, 'Academic Discipline'),
                'accreditations': self._prepare_distribution_viz(accreditation_dist, 'Accreditation')
            },
            'config': {
                'layout': 'grid',
                'columns': 3,
                'responsive': True
            },
            'source': 'Business School KPI Service',
            'timestamp': datetime.now().isoformat()
        }
    
    def render_all_visualizations(self, schools: Optional[List[str]] = None, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Render all 5 visualization types together for comprehensive analysis
        
        Args:
            schools: List of school names. If None, uses all schools.
            filters: Optional filters (region, accreditation, etc.)
            
        Returns:
            List of all visualization objects
        """
        logger.info("🎨 Rendering all visualizations")
        
        visualizations = [
            self.render_kpi_overview_chart(schools),
            self.render_expandable_detail_table(schools),
            self.render_filter_controls(),
            self.render_cascading_selection(),
            self.render_stats_cards(schools)
        ]
        
        return visualizations
    
    # ==================== PRIVATE METHODS ====================
    
    def _prepare_distribution_viz(self, distribution: Dict[str, int], label: str) -> Dict[str, Any]:
        """Prepare a distribution dictionary as a visualization-ready object"""
        return {
            'type': 'pie',
            'title': f'{label} Distribution',
            'data': [{'name': k, 'value': v} for k, v in distribution.items()],
            'total': sum(distribution.values())
        }
