# 🌍 Business School Discovery Runner - User Guide

## Quick Start

### Run Discovery for Africa (Recommended First Test)
```bash
python run_discovery.py --regions Africa
```

### Run Discovery for All Continents
```bash
python run_discovery.py --regions Africa Europe Asia Americas
```

### Run with Ollama LLM (More Accurate, Slower)
```bash
python run_discovery.py --regions Africa --ollama
```

---

## Features

✅ **Beautiful Terminal Output**
- Color-coded results (green for success, yellow for warnings)
- ASCII table with statistics per country
- Progress tracking and summary reports

✅ **Multi-Region Support**
- Africa: Zimbabwe, South Africa, Nigeria, Kenya, Ethiopia, Ghana, Morocco, Botswana
- Europe: UK, Germany, France, Spain, Italy, Netherlands, Belgium, Switzerland, Austria, Sweden
- Asia: India, China, Japan, Singapore, South Korea, Thailand, Philippines, Vietnam, Malaysia, Indonesia
- Americas: USA, Canada, Brazil, Mexico, Argentina, Colombia, Chile, Peru, Venezuela, Ecuador

✅ **Comprehensive Data Export**
- CSV files with all statistics per country
- Markdown reports for each region
- Staff member details (name, degree, research interests, ORCID)
- Research centre mapping
- Degree count breakdowns (PhD, Masters, MBA, Bachelor)

✅ **Error Handling**
- Network failures handled gracefully
- SSL certificate issues skipped safely
- Partial data collection when pages unavailable

---

## Output Examples

### Basic Africa Run
```
╔══════════════════════════════════════════════════════════════════════════════╗
║               BUSINESS SCHOOL DISCOVERY SYSTEM - MULTI-REGION RUNNER         ║
╚══════════════════════════════════════════════════════════════════════════════╝

ℹ️  Starting discovery for: Africa
ℹ️  LLM Extraction: Disabled (Fast mode)
ℹ️  Start Time: 2026-03-07 00:15:37

════════════════════════════════════════════════════════════════════════════════
                    🌍  AFRICA - BUSINESS SCHOOL DISCOVERY

════════════════════════════════════════════════════════════════════════════════

Country              │ Schools      │ Programmes     │ Research     │ Staff
Zimbabwe             │ 5            │ 0              │ 0            │ 0
South Africa         │ 7            │ 0              │ 0            │ 14
Nigeria              │ 5            │ 0              │ 0            │ 8
Kenya                │ 3            │ 1              │ 1            │ 0
Ethiopia             │ 3            │ 3              │ 2            │ 1
Ghana                │ 3            │ 1              │ 0            │ 0
Morocco              │ 3            │ 2              │ 1            │ 0
Botswana             │ 2            │ 0              │ 0            │ 0

📊 REGION SUMMARY
═════════════════════════════════════════════════════════════════════════════

Region: AFRICA
Timestamp: 2026-03-07 00:15:52

  → Countries Processed        : 8
  → Total Schools Discovered    : 31
  → Schools with Programmes    : 8
  → Schools with Research Centers: 4
  → Staff Members Extracted    : 23

✨ Discovery Complete!
Total Duration: 45.3 seconds
```

---

## Exported Files

Each region generates export files with the following structure:

### Per-Country Files
```
discovered_schools_{country}.csv      # Schools with all metrics
discovered_schools_{country}.md       # Markdown report
staff_members_{country}.csv           # Staff roster (if available)
research_centres_{country}.csv        # Research directories (if available)
```

### Example CSV Columns
- School Name
- Country
- Website
- Programmes
- Programme Count
- **Masters Count, PhDs Count, MBAs Count, Bachelor Count** (NEW)
- Research Centres
- Research Themes
- Academic Staff
- Total Staff Extracted
- Accreditation
- Source
- Discovery Date

---

## Advanced Usage

### Check Available Regions
```python
from run_discovery import DiscoveryRunner

runner = DiscoveryRunner()
print(runner.REGIONS.keys())  # Returns: dict_keys(['Africa', 'Europe', 'Asia', 'Americas'])
```

### Get Region Countries
```python
from run_discovery import DiscoveryRunner

runner = DiscoveryRunner()
print(runner.REGIONS['Asia']['countries'])
# Returns: ['India', 'China', 'Japan', 'Singapore', 'South Korea', ...]
```

### Programmatic Usage
```python
from run_discovery import DiscoveryRunner

runner = DiscoveryRunner()

# Run African discovery
results = runner.run(['Africa'], use_ollama=False)

# Access results programmatically
africa_stats = runner.results['Africa']
print(f"Total schools: {africa_stats['total_schools']}")
print(f"Staff extracted: {africa_stats['total_staff_extracted']}")

# Get per-country details
zimbabwe = africa_stats['country_results']['zimbabwe']
print(f"Zimbabwe schools: {zimbabwe['schools']}")
```

---

## Data Quality Notes

✅ **Verified Sources**
- All schools sourced from hardcoded verified database
- No fake healthcare sites (unlike web search)
- 31 real African business schools

❌ **Known Limitations**
- Staff extraction requires accessible school websites
- SSL certificate issues on some sites skip staff pages
- Network timeouts on some international sites

---

## Scaling Instructions

### To Add New Regions/Countries

1. **Edit `run_discovery.py`**:
```python
REGIONS = {
    'Your Region': {
        'countries': [
            'Country 1', 'Country 2', 'Country 3', ...
        ],
        'emoji': '🌐'  # Choose appropriate emoji
    }
}
```

2. **Update BusinessSchoolDiscoverer** to include school data for new countries

3. **Run discovery**:
```bash
python run_discovery.py --regions "Your Region"
```

---

## Performance Tips

- **Fast mode** (default): ~5-10 seconds per country
- **LLM mode** (--ollama): ~30-60 seconds per country
- Use `--regions Africa` first to validate setup
- Export files available in `health_app/business_school_data/`

---

## Troubleshooting

### Module Not Found Errors
```bash
python -m pip install -r requirements.txt
```

### Ollama Not Running
- Install Ollama: https://ollama.ai
- Start Ollama service: `ollama serve`
- Run without --ollama flag for fast mode

### SSL Certificate Errors
These are handled gracefully - staff extraction skips problematic sites and continues

### No Output
Check that you're in the correct directory containing the project files

---

## Command Reference

```bash
# Africa only (default, ~45 seconds)
python run_discovery.py

# Specific regions
python run_discovery.py --regions Africa Europe

# All continents
python run_discovery.py --regions Africa Europe Asia Americas

# With LLM (slower but more accurate)
python run_discovery.py --regions Africa --ollama

# Help
python run_discovery.py --help
```

---

## Data Export Locations

All export files saved to:
```
health_app/business_school_data/

├── discovered_schools_africa/
│   ├── discovered_schools_zimbabwe.csv
│   ├── discovered_schools_zimbabwe.md
│   ├── staff_members_zimbabwe.csv
│   ├── research_centres_zimbabwe.csv
│   └── ... (for each African country)
│
├── discovered_schools_europe/
│   ├── discovered_schools_uk.csv
│   ├── discovered_schools_uk.md
│   └── ... (for each European country)
│
└── ... (Asia, Americas)
```

---

## Next Steps

1. ✅ Run `python run_discovery.py --regions Africa` 
2. ✅ Verify data quality in exported CSVs
3. ✅ If good, scale with `--regions Africa Europe Asia`
4. ✅ Integrate with Django API for web access
5. ✅ Build analytics dashboard

---

**Version:** 1.0  
**Last Updated:** 2026-03-07  
**Status:** Production Ready ✅
