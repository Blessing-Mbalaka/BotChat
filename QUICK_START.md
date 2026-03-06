# 🚀 Quick Start Guide - Business School Discovery

## 3-Second Start: Africa Only

### Option 1: PowerShell (Recommended)
```powershell
.\run_africa.ps1
```

### Option 2: Command Prompt (CMD)
```cmd
run_africa.bat
```

### Option 3: Python (Direct)
```python
python run_discovery.py --regions Africa
```

---

## 🌐 Scale to Global (All Continents)

### Option 1: PowerShell
```powershell
python run_discovery.py --regions Africa Europe Asia Americas
```

### Option 2: Command Prompt
```cmd
python run_discovery.py --regions Africa Europe Asia Americas
```

---

## 📊 What You'll Get

Running `run_africa.ps1` or `python run_discovery.py --regions Africa` will:

1. **Discover 31 real business schools** across 8 African countries
2. **Extract staff members** (PhDs, Masters, MBAs, Bachelors)
3. **Identify research themes** (management, finance, entrepreneurship, etc.)
4. **Generate 4 export files per country:**
   - `discovered_schools_{country}.csv` - All metrics with degree counts
   - `discovered_schools_{country}.md` - Markdown report
   - `staff_members_{country}.csv` - Staff roster with credentials
   - `research_centres_{country}.csv` - Research directory

5. **Print beautiful terminal output** showing:
   - Table of all countries with statistics
   - Schools discovered per country
   - Staff members extracted
   - Research centres identified
   - Global summary if running multiple regions

---

## 📍 Countries Covered

### Africa (8 Countries, 31 Schools)
- Zimbabwe (5)
- South Africa (7)
- Nigeria (5)
- Kenya (3)
- Ethiopia (3)
- Ghana (3)
- Morocco (3)
- Botswana (2)

### Europe (10 Countries)
- United Kingdom
- Germany
- France
- Spain
- Italy
- Netherlands
- Belgium
- Switzerland
- Austria
- Sweden

### Asia (10 Countries)
- India
- China
- Japan
- Singapore
- South Korea
- Thailand
- Philippines
- Vietnam
- Malaysia
- Indonesia

### Americas (10 Countries)
- United States
- Canada
- Brazil
- Mexico
- Argentina
- Colombia
- Chile
- Peru
- Venezuela
- Ecuador

---

## 🎯 Expected Output

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                   BUSINESS SCHOOL DISCOVERY RUNNER - QUICK START             ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Country              │ Schools      │ Programmes     │ Research     │ Staff
─────────────────────┼──────────────┼────────────────┼──────────────┼─────────
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

  → Countries Processed        : 8
  → Total Schools Discovered    : 31
  → Schools with Programmes    : 8
  → Schools with Research      : 4
  → Staff Members Extracted    : 23

✨ Discovery Complete! (Duration: 45.3 seconds)
```

---

## 📁 Where Are My Files?

All exports saved to:
```
health_app/business_school_data/

discovered_schools_zimbabwe.csv
discovered_schools_zimbabwe.md
staff_members_zimbabwe.csv
research_centres_zimbabwe.csv

discovered_schools_south_africa.csv
discovered_schools_south_africa.md
staff_members_south_africa.csv
research_centres_south_africa.csv

... (and so on for each country)
```

---

## ✅ Verify It's Working

After running, check that files exist:

### PowerShell
```powershell
Get-ChildItem health_app/business_school_data/*.csv | Select-Object Name
```

### Command Line
```cmd
dir health_app\business_school_data\*.csv
```

### Expected Output (at least 25 files):
```
discovered_schools_zimbabwe.csv
discovered_schools_zimb abwe.md
staff_members_zimbabwe.csv
research_centres_zimbabwe.csv
...
```

---

## 🔧 Advanced Options

### Run with Ollama LLM (More Accurate)
```python
python run_discovery.py --regions Africa --ollama
```

### Run Specific Regions
```python
python run_discovery.py --regions Africa Europe
python run_discovery.py --regions Asia Americas
```

### View Help
```python
python run_discovery.py --help
```

---

## 🚨 Troubleshooting

### "Command not found"
Make sure you're in the `E:\Healthcare_Bot` directory:
```powershell
cd E:\Healthcare_Bot
```

### "Python not found"
Activate the virtual environment first:
```powershell
.\.venv\Scripts\Activate.ps1
```

### No output, just hangs
Discovery is running! It takes 30-60 seconds per region. Be patient.

### See network errors (SSL, DNS, timeouts)
This is normal! The system gracefully handles these and continues. Check the export files - data is still saved.

---

## ⏱️ Time Estimates

| Scope | Duration |
|-------|----------|
| Africa (8 countries) | ~45 seconds |
| Europe (10 countries) | ~60 seconds |
| Asia (10 countries) | ~60 seconds |
| Americas (10 countries) | ~60 seconds |
| **All Global (40 countries)** | **~4 minutes** |

---

## 📈 Data Quality Notes

✅ **What's Verified**
- All 31 African schools are real universities
- No fake healthcare sites
- Hardcoded source database (no web search)
- Staff extraction from official websites

⚠️ **Known Limitations**
- Staff pages may have SSL/network issues (gracefully skipped)
- Some older university sites don't list staff online
- International sites may have timeout issues

---

## 🎓 What's in the CSV Files?

### discovered_schools_zimbabwe.csv
```csv
School Name,Country,Website,Programmes,Masters Count,PhDs Count,MBAs Count,Bachelor Count,Research Centres,Research Themes,...
```

### staff_members_south_africa.csv
```csv
School Name,School URL,Staff Name,Degree,Research Interests,ORCID,URL
University of Cape Town GSB,https://www.gsb.uct.ac.za,Catherine Duggan,phd,,,https://www.gsb.uct.ac.za
```

### research_centres_zimbabwe.csv
```csv
Centre Name,Theme,School Name,School URL
```

---

## 🚀 Next Steps (After Data Verification)

1. ✅ Run `.\run_africa.ps1` - Verify Africa works
2. ✅ Check `health_app/business_school_data/*.csv` for data
3. ✅ If data looks good, run `python run_discovery.py --regions Africa Europe Asia Americas`
4. ✅ Integrate with Django API endpoints
5. ✅ Build web dashboard

---

**Ready to start? Run:** `.\run_africa.ps1`

**Want more? Run:** `python run_discovery.py --regions Africa Europe Asia Americas`

Good luck! 🚀
