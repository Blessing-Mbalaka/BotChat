"""
Constants for Business School KPI Service

Defines programme types, accreditation levels, academic disciplines, and regions.
"""

# Programme Types
PROGRAMME_TYPES = {
    'MBA': 'Master of Business Administration',
    'MA': 'Master of Arts',
    'MSC': 'Master of Science',
    'BACHELOR': 'Bachelor Degree',
    'POSTGRADUATE': 'Postgraduate Certificate/Diploma',
    'PDH': 'Professional Development & Higher Education',
    'CERTIFICATE': 'Certificate Program',
    'EXECUTIVE': 'Executive Education',
    'MA_MBA': 'MA/MBA Combined'
}

# Accreditation Standards
ACCREDITATIONS = {
    'AACSB': 'AACSB International - The Association to Advance Collegiate Schools of Business',
    'EQUIS': 'EQUIS - European Quality Improvement System',
    'AMBA': 'AMBA - Association of MBAs',
    'ACBSP': 'ACBSP - Accreditation Council for Business Schools and Programs',
    'FIBAA': 'FIBAA - Foundation for International Business Administration Accreditation',
    'QS': 'QS Ranked',
    'TIMES_HE': 'Times Higher Education Ranked',
    'SHANGHAI': 'Shanghai Ranking',
    'UNACCREDITED': 'Not Currently Accredited'
}

# Academic Disciplines
ACADEMIC_DISCIPLINES = {
    'FINANCE': 'Finance & Accounting',
    'MARKETING': 'Marketing & Brand Management',
    'STRATEGY': 'Strategic Management',
    'OPERATIONS': 'Operations & Supply Chain',
    'ENTREPRENEURSHIP': 'Entrepreneurship & Innovation',
    'ORGANIZATIONAL': 'Organizational Behavior & HR',
    'ECONOMICS': 'Economics',
    'BUSINESS_LAW': 'Business Law & Ethics',
    'MANAGEMENT': 'General Management',
    'TECHNOLOGY': 'Business Technology & Digital',
    'SUSTAINABILITY': 'Sustainability & CSR',
    'LEADERSHIP': 'Leadership Development',
    'INTERNATIONAL_BUSINESS': 'International Business',
    'REAL_ESTATE': 'Real Estate & Property',
    'HOSPITALITY': 'Hospitality & Tourism Management',
    'LUXURY': 'Luxury Management'
}

# Regions
REGIONS = {
    'EUROPE': 'Europe',
    'NORTH_AMERICA': 'North America',
    'SOUTH_AMERICA': 'South America',
    'ASIA_PACIFIC': 'Asia Pacific',
    'MIDDLE_EAST_AFRICA': 'Middle East & Africa',
    'AFRICA': 'Africa',
    'SOUTH_AFRICA': 'South Africa',
    'UK': 'United Kingdom',
    'US': 'United States',
    'CANADA': 'Canada',
    'AUSTRALIA': 'Australia'
}

# Research Centre Themes
RESEARCH_THEMES = [
    'Finance & Risk Management',
    'Digital Transformation',
    'Sustainable Business',
    'Entrepreneurship & Innovation',
    'Leadership & Governance',
    'Consumer Behavior',
    'International Trade',
    'Supply Chain Excellence',
    'Healthcare Management',
    'Financial Services',
    'Emerging Markets',
    'Corporate Social Responsibility'
]

# Data Quality Levels
DATA_QUALITY = {
    'HIGH': 'High confidence (directly from official source)',
    'MEDIUM': 'Medium confidence (aggregated/inferred)',
    'LOW': 'Low confidence (limited sources)',
    'SYNTHETIC': 'Synthetic/estimated data'
}

# Visualization Types
VIZ_TYPES = {
    'BAR': 'bar',
    'PIE': 'pie',
    'TABLE': 'table',
    'EXPANDABLE_TABLE': 'expandable_table',
    'STATS_CARD': 'stats_card',
    'FILTER_PANEL': 'filter_panel',
    'CASCADING_SELECT': 'cascading_select',
    'NETWORK': 'network'
}
