"""
Business School KPI Service Module

A comprehensive system for researching, analyzing, and visualizing business school KPIs.
Including programme offerings (MA, Bachelors, PDH, Certificates), academic staff disciplines,
and research centre information with stratified visualization capabilities.

Components:
- researcher.py: BusinessSchoolResearcher (finds and extracts school data from pre-built database)
- discoverer.py: BusinessSchoolDiscoverer (auto-discovers schools by region/country via web search + Ollama)
- ollama_kpi_extractor.py: OllamaKPIExtractor (uses local Ollama LLM to extract KPIs from websites)
- kpi_service.py: BusinessSchoolKPIService (aggregates and filters KPIs)
- visualization_service.py: BusinessSchoolVisualizationService (renders stratified visualizations)
- constants.py: Programme types, accreditation levels, disciplines
- config.yaml: Search sources, search patterns, schemas
"""

from .researcher import BusinessSchoolResearcher
from .discoverer import BusinessSchoolDiscoverer
from .ollama_kpi_extractor import OllamaKPIExtractor
from .staff_extractor import StaffAndResearchExtractor
from .kpi_service import BusinessSchoolKPIService
from .visualization_service import BusinessSchoolVisualizationService

__all__ = [
    'BusinessSchoolResearcher',
    'BusinessSchoolDiscoverer',
    'OllamaKPIExtractor',
    'StaffAndResearchExtractor',
    'BusinessSchoolKPIService',
    'BusinessSchoolVisualizationService',
]
