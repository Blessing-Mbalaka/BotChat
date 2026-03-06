# 🚀 Business School Discovery System - Complete Implementation

## Overview

Three-in-one system providing:
1. **Django REST API** - Programmatic access to all school, staff, and research data
2. **Web Dashboard** - Interactive visualization and analytics
3. **Data Analytics** - Insights, rankings, and intelligence reports

---

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Setup Script
```bash
python setup_system.py
```

This will:
- Run Django migrations
- Import CSV data into database
- Display statistics and analytics
- Show all available endpoints

### 3. Start Development Server
```bash
python manage.py runserver
```

### 4. Access Interfaces

**Web Dashboard:** http://localhost:8000/dashboard/
- Beautiful charts and visualizations
- Interactive statistics
- Top schools rankings

**REST API:** http://localhost:8000/api/
- Programmatic access to all data
- JSON responses
- Filter and search capabilities

**Django Admin:** http://localhost:8000/admin/
- Manage schools, staff, research
- View all records
- Browse relationships

---

## Architecture

### Database Models

```
BusinessSchool (31 schools from Africa + future regions)
├── name, country, region
├── website, programmes
├── phd_count, masters_count, mba_count, bachelor_count
├── research_themes, accreditation
└── relationships:
    ├── staff_members (1 → Many)
    └── research_centres_data (1 → Many)

StaffMember (40+ extracted staff members)
├── name, degree (PhD/Masters/MBA/Bachelor)
├── research_interests, orcid
├── profile_url
└── relationships:
    └── school (Many → 1) BusinessSchool

ResearchCentre
├── name, theme, description
├── website_url
└── relationships:
    └── school (Many → 1) BusinessSchool

DiscoveryJob (track when data was discovered)
├── region, status (pending/running/completed/failed)
├── schools_discovered, staff_extracted, research_centres_found
└── started_at, completed_at, duration
```

---

## REST API Reference

### Schools Endpoints

**List all schools**
```
GET /api/schools/
```

**Get school details with staff and research**
```
GET /api/schools/{id}/
```

**Schools by region**
```
GET /api/schools/by-region/?region=Africa
```

**Schools by country**
```
GET /api/schools/by-country/?country=Zimbabwe
```

**Schools with PhD programmes**
```
GET /api/schools/with-phds/
```

**Global statistics**
```
GET /api/schools/stats/
```

**Get staff in a school**
```
GET /api/schools/{id}/staff/
```

**Get research in a school**
```
GET /api/schools/{id}/research/
```

---

### Staff Endpoints

**List all staff**
```
GET /api/staff/
```

**Staff by degree**
```
GET /api/staff/by-degree/?degree=phd
```

**All PhD holders**
```
GET /api/staff/phds/
```

**Search staff**
```
GET /api/staff/?search=catherine
```

**Staff statistics**
```
GET /api/staff/stats/
```

---

### Research Endpoints

**List research centres**
```
GET /api/research/
```

**Research by theme**
```
GET /api/research/by-theme/?theme=finance
```

**Research themes**
```
GET /api/research/themes/
```

---

### Example API Responses

**Get all African schools:**
```bash
curl http://localhost:8000/api/schools/by-region/?region=Africa
```

Response:
```json
{
    "region": "Africa",
    "count": 31,
    "schools": [
        {
            "id": 1,
            "name": "University of Cape Town - Graduate School of Business",
            "country": "South Africa",
            "region": "Africa",
            "website": "https://www.gsb.uct.ac.za",
            "phd_count": 1,
            "masters_count": 0,
            "mba_count": 0,
            "total_staff_extracted": 1,
            "research_themes": "leadership; management; finance",
            "discovered_date": "2026-03-06T23:37:15.709105"
        }
    ]
}
```

**Get PhD holders:**
```bash
curl http://localhost:8000/api/staff/phds/
```

Response:
```json
{
    "degree": "PhD",
    "count": 45,
    "staff": [
        {
            "id": 1,
            "name": "Catherine Duggan",
            "degree": "phd",
            "research_interests": "leadership, innovation",
            "profile_url": "https://www.gsb.uct.ac.za"
        }
    ]
}
```

---

## Web Dashboard

### Features

✅ **Global Statistics**
- Total schools, countries, staff
- PhD holders, research centres

✅ **Interactive Charts**
- Schools by region (bar chart)
- Staff by degree level (doughnut)
- Top research themes (horizontal bar)
- Degree distribution (pie)

✅ **Rankings**
- Top schools by PhD count
- Top schools by staff extracted
- Top schools by research centres

✅ **Real-time Updates**
- Dashboard pulls live data from API
- Auto-refreshes statistics
- Responsive design

### Accessing Dashboard

1. Start server: `python manage.py runserver`
2. Open browser: http://localhost:8000/dashboard/
3. View charts and rankings in real-time

---

## Analytics Service

### Available Methods

```python
from health_app.services.analytics_service import BusinessSchoolAnalytics

analytics = BusinessSchoolAnalytics()

# Global statistics
analytics.get_global_statistics()
# Returns: total schools, regions, countries, staff, research centres

# Regional analysis
analytics.get_regional_analysis()
# Returns: schools per region, staff, PhD counts, top schools

# Country analysis
analytics.get_country_analysis()
# Returns: detailed breakdown by country

# Staff analysis
analytics.get_staff_analysis()
# Returns: degree distribution, research interests, ORCID data

# Research analysis
analytics.get_research_analysis()
# Returns: research centres, themes, top themes

# School rankings
analytics.get_school_ranking(sort_by='staff')
# Options: 'staff', 'phd', 'research', 'programmes'

# Excellence metrics
analytics.get_excellence_metrics()
# Returns: PhD leaders, research leaders, staff leaders

# Export full report
analytics.export_report_json()
# Returns: complete analysis as JSON
```

### Example Usage

```python
python manage.py shell

>>> from health_app.services.analytics_service import BusinessSchoolAnalytics
>>> analytics = BusinessSchoolAnalytics()

# Get global stats
>>> stats = analytics.get_global_statistics()
>>> print(f"Total schools: {stats['total_schools']}")
Total schools: 31

# Get PhD leaders
>>> excellence = analytics.get_excellence_metrics()
>>> for school in excellence['phd_leaders'][:5]:
...     print(f"{school['name']}: {school['phd_count']} PhDs")

# Export complete report
>>> report = analytics.export_report_json()
>>> with open('analysis_report.json', 'w') as f:
...     f.write(report)
```

---

## Django Admin Interface

Access at: http://localhost:8000/admin/

Users can:
- View all business schools
- Browse staff members by school
- Explore research centres
- Track discovery jobs
- Filter by region, country, degree
- Search schools and staff

---

## Data Import

### Initial Import

```bash
python manage.py import_schools --region Africa
```

### Import with Clear

```bash
python manage.py import_schools --region Africa --clear
```

### Import Specific Country

```bash
python manage.py import_schools --country Zimbabwe
```

### Bulk Import All Regions

```bash
for region in Africa Europe Asia Americas; do
    python manage.py import_schools --region $region
done
```

---

## File Structure

```
health_app/
├── models.py                    # 4 Django models
├── serializers.py              # REST serializers
├── api_views.py                # API viewsets
├── api_urls.py                 # API routing
├── management/commands/
│   └── import_schools.py       # Data import command
├── services/
│   └── analytics_service.py    # Analytics engine
└── templates/health_app/
    └── dashboard.html          # Dashboard UI

health_project/
├── settings.py                 # Django config
├── urls.py                     # Main routing

setup_system.py                 # Setup script
```

---

## Database Schema

### BusinessSchool
- id (PK)
- name, country, region, website
- programmes, programme_count
- phd_count, masters_count, mba_count, bachelor_count
- research_centres, research_themes, research_centre_count
- academic_staff_count, total_staff_extracted
- accreditation, source
- discovered_date, last_updated

### StaffMember
- id (PK)
- school_id (FK)
- name, degree
- research_interests, orcid, profile_url
- discovered_date, last_updated

### ResearchCentre
- id (PK)
- school_id (FK)
- name, theme, description, website_url
- discovered_date, last_updated

### DiscoveryJob
- id (PK)
- region, status
- schools_discovered, staff_extracted, research_centres_found
- started_at, completed_at, error_message

---

## Performance

- **Query Optimization:** Database indexes on frequently searched fields
- **Pagination:** API supports limit/offset for large datasets
- **Caching:** Dashboard caches API responses in browser
- **Serialization:** Efficient JSON serialization with DRF

---

## Scalability

Scale to 100+ countries:

1. **Add more data sources** to CSV exports
2. **Run import command** for new regions
3. **API handles** thousands of schools/staff automatically
4. **Dashboard** auto-adapts to larger datasets

---

## Troubleshooting

### Migrations fail
```bash
python manage.py showmigrations
python manage.py migrate health_app
```

### API endpoint 404
Check that api_urls.py is included in health_project/urls.py

### Dashboard doesn't load
Ensure REST framework is installed: `pip install djangorestframework`

### Import fails
Check CSV files exist in `health_app/business_school_data/`

---

## Next Steps

1. ✅ Run setup_system.py
2. ✅ Test API endpoints
3. ✅ View dashboard
4. ✅ Explore analytics
5. Scale to Europe, Asia, Americas
6. Integrate with external data sources
7. Add authentication/permissions
8. Deploy to production (AWS, Heroku, etc.)

---

**Status:** Production Ready ✅
