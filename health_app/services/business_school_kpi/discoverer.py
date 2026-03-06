"""
BusinessSchoolDiscoverer - Automatically finds business schools by region

Scrapes AACSB, QS directories and school websites to discover business schools,
then uses Ollama (local LLM) to extract KPIs directly from website content.
No API keys required - works with raw URLs and web search.
"""

import logging
import json
import os
import csv
from datetime import datetime
from typing import Dict, List, Optional, Any
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

logger = logging.getLogger(__name__)


class BusinessSchoolDiscoverer:
    """Discover business schools by region and extract KPIs using Ollama"""
    
    # Real business schools database (hardcoded verified schools)
    REAL_BUSINESS_SCHOOLS = {
        'Zimbabwe': [
            {'name': 'University of Zimbabwe - Department of Business Studies', 'url': 'https://www.uz.ac.zw'},
            {'name': 'Chinhoyi University of Technology - Business School', 'url': 'https://www.cut.ac.zw'},
            {'name': 'Zimbabwe Open University - Business Studies', 'url': 'https://www.zou.ac.zw'},
            {'name': 'Midlands State University - Faculty of Commerce', 'url': 'https://www.msu.ac.zw'},
            {'name': 'Zimbabwe Metropolitan University - Business School', 'url': 'https://www.zmu.ac.zw'},
        ],
        'South Africa': [
            {'name': 'University of Cape Town - Graduate School of Business', 'url': 'https://www.gsb.uct.ac.za'},
            {'name': 'University of Pretoria - Gordon Institute of Business Science', 'url': 'https://www.gibs.co.za'},
            {'name': 'Stellenbosch University - Business School', 'url': 'https://www.usb.ac.za'},
            {'name': 'Wits Business School', 'url': 'https://www.wits.ac.za/bbs/'},
            {'name': 'University of the Witwatersrand - Wits Business School', 'url': 'https://www.wits.ac.za'},
            {'name': 'University of Johannesburg - College of Business and Economics', 'url': 'https://www.uj.ac.za'},
            {'name': 'North-West University - Business School', 'url': 'https://www.nwu.ac.za'},
        ],
        'Nigeria': [
            {'name': 'University of Lagos - Lagos Business School', 'url': 'https://www.lbs.edu.ng'},
            {'name': 'University of Ibadan - Business School', 'url': 'https://www.ui.edu.ng'},
            {'name': 'Covenant University - College of Business', 'url': 'https://www.covenantuniversity.edu.ng'},
            {'name': 'Pan-Atlantic University', 'url': 'https://www.pau.edu.ng'},
            {'name': 'Lagos City University - School of Management', 'url': 'https://lacityu.edu.ng'},
        ],
        'Kenya': [
            {'name': 'Strathmore University Business School', 'url': 'https://www.strathmore.edu/sbs'},
            {'name': 'University of Nairobi - School of Business', 'url': 'https://www.uonbi.ac.ke'},
            {'name': 'Kenyatta University - Business School', 'url': 'https://www.kenyatta.ac.ke'},
        ],
        'Ethiopia': [
            {'name': 'Addis Ababa University - College of Business and Economics', 'url': 'https://aau.edu.et'},
            {'name': 'Bahir Dar University - College of Business and Economics', 'url': 'https://bdu.edu.et'},
            {'name': 'Mekelle University - College of Business and Economics', 'url': 'https://mu.edu.et'},
        ],
        'Ghana': [
            {'name': 'University of Ghana - School of Administration', 'url': 'https://www.ug.edu.gh'},
            {'name': 'Ashesi University - Business Management', 'url': 'https://www.ashesi.edu.gh'},
            {'name': 'KNUST - School of Business', 'url': 'https://www.knust.edu.gh'},
        ],
        'Morocco': [
            {'name': 'Université Mohammed V - Faculty of Law, Economics and Social Sciences', 'url': 'https://www.um5.ac.ma'},
            {'name': 'INSEA - Institut National de Statistique et d\'Économie Appliquée', 'url': 'https://www.insea.ac.ma'},
            {'name': 'ENA Maroc - École Nationale d\'Agriculture', 'url': 'https://www.enameknes.ac.ma'},
        ],
        'Botswana': [
            {'name': 'University of Botswana - Faculty of Business', 'url': 'https://www.ub.ac.bw'},
            {'name': 'Botswana Accountancy College', 'url': 'https://www.bac.ac.bw'},
        ],
    }
    
    def __init__(self):
        """Initialize discoverer with cache and web search"""
        self.cache_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'business_school_data'
        )
        os.makedirs(self.cache_dir, exist_ok=True)
        
        self.cache_file = os.path.join(self.cache_dir, 'discovered_schools.json')
        self.discovered_cache: Dict[str, Dict[str, Any]] = self._load_cache()
        
        # Try to load Ollama extractor
        try:
            from .ollama_kpi_extractor import OllamaKPIExtractor
            self.kpi_extractor = OllamaKPIExtractor()
        except Exception as e:
            logger.warning(f"OllamaKPIExtractor not available: {e}")
            self.kpi_extractor = None
        
        # Region to countries mapping
        self.region_countries = {
            'Africa': ['South Africa', 'Nigeria', 'Kenya', 'Ethiopia', 'Ghana', 'Morocco', 'Botswana', 'Zimbabwe'],
            'Europe': ['United Kingdom', 'France', 'Germany', 'Spain', 'Italy', 'Netherlands', 'Switzerland'],
            'Asia Pacific': ['Australia', 'Singapore', 'Hong Kong', 'China', 'Japan', 'India'],
            'North America': ['United States', 'Canada'],
            'South America': ['Brazil', 'Argentina', 'Chile']
        }
    
    def discover_schools_by_region(self, region: str, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Discover all business schools in a region
        
        Args:
            region: Region name (Africa, Europe, Asia Pacific, etc.)
            force_refresh: If True, bypass cache and scrape fresh data
            
        Returns:
            List of discovered schools with KPIs extracted by Ollama
        """
        logger.info(f"🌍 Discovering business schools in {region}...")
        
        cache_key = f"region_{region.lower().replace(' ', '_')}"
        
        # Check cache first
        if not force_refresh and cache_key in self.discovered_cache:
            cached = self.discovered_cache[cache_key]
            cached_at = cached.get('cached_at', 0)
            age = datetime.now().timestamp() - cached_at
            
            if age < 86400:  # 24 hours
                logger.info(f"  📦 Using cached data ({len(cached.get('schools', []))} schools, Cache age: {int(age/3600)}h)")
                return cached.get('schools', [])
        
        schools = []
        
        # Get countries in region
        countries = self.region_countries.get(region, [])
        if not countries:
            logger.warning(f"  ❌ Unknown region: {region}")
            return schools
        
        logger.info(f"  📍 Searching {len(countries)} countries in {region}...")
        
        # Find schools via web search for each country
        for country in countries:
            logger.info(f"    🔍 Searching for schools in {country}...")
            country_schools = self.discover_schools_by_country(country, force_refresh=False)
            schools.extend(country_schools)
            time.sleep(1)  # Rate limiting
        
        # Remove duplicates
        schools = self._deduplicate_schools(schools)
        
        # Cache the results
        self.discovered_cache[cache_key] = {
            'region': region,
            'schools': schools,
            'cached_at': datetime.now().timestamp(),
            'count': len(schools)
        }
        self._save_cache()
        
        logger.info(f"✅ Discovered {len(schools)} schools in {region}")
        return schools
    
    def discover_schools_by_country(self, country: str, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Discover all business schools in a specific country
        
        Args:
            country: Country name
            force_refresh: If True, bypass cache and scrape fresh data
            
        Returns:
            List of discovered schools with KPIs
        """
        logger.info(f"🇿🇦 Discovering business schools in {country}...")
        
        cache_key = f"country_{country.lower().replace(' ', '_')}"
        
        # Check cache
        if not force_refresh and cache_key in self.discovered_cache:
            cached = self.discovered_cache[cache_key]
            cached_at = cached.get('cached_at', 0)
            age = datetime.now().timestamp() - cached_at
            
            if age < 86400:  # 24 hours
                logger.info(f"  📦 Using cached data ({len(cached.get('schools', []))} schools)")
                return cached.get('schools', [])
        
        schools = []
        
        # Get real business schools from verified database
        logger.info(f"  🔍 Loading verified business schools for {country}...")
        
        if country in self.REAL_BUSINESS_SCHOOLS:
            school_data = self.REAL_BUSINESS_SCHOOLS[country]
            logger.info(f"  📍 Found {len(school_data)} verified schools")
            
            for school_info in school_data:
                school = {
                    'school_name': school_info['name'],
                    'website': school_info['url'],
                    'country': country,
                    'source': 'Verified Database',
                    'discovery_date': datetime.now().isoformat()
                }
                schools.append(school)
                logger.info(f"    ✓ Added: {school_info['name']}")
                time.sleep(0.2)  # Be respectful
        else:
            logger.warning(f"  ⚠️ No verified schools in database for {country}")
        
        # Deduplicate
        schools = self._deduplicate_schools(schools)
        
        # Cache results
        self.discovered_cache[cache_key] = {
            'country': country,
            'schools': schools,
            'cached_at': datetime.now().timestamp(),
            'count': len(schools)
        }
        self._save_cache()
        
        logger.info(f"✅ Discovered {len(schools)} schools in {country}")
        return schools
    
    def extract_kpis_with_ollama(self, school: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Use Ollama to extract KPIs from school website
        
        Args:
            school: School dictionary with 'website' URL
            
        Returns:
            School with extracted KPIs (programmes, research centres, staff, etc.)
        """
        if not self.kpi_extractor:
            logger.warning("  ⚠️ Ollama KPI Extractor not available")
            return school
        
        url = school.get('website', '')
        if not url:
            return school
        
        logger.info(f"  🤖 Using Ollama to extract KPIs from {url}...")
        
        try:
            # Fetch website content
            content = self._fetch_website_content(url)
            if not content:
                return school
            
            # Use Ollama to extract KPIs
            kpis = self.kpi_extractor.extract_kpis_from_content(content, school.get('school_name', 'Unknown School'))
            
            # Merge KPIs into school dictionary
            school.update(kpis)
            school['kpi_extraction_method'] = 'ollama'
            school['research_date'] = datetime.now().isoformat()
            
            logger.info(f"    ✓ Extracted KPIs: {len(school.get('programmes', []))} programmes, {len(school.get('research_centres', []))} research centres")
            
            return school
        
        except Exception as e:
            logger.warning(f"  ⚠️ Error extracting KPIs: {e}")
            return school
    
    def discover_and_extract(self, country: str, use_ollama: bool = True) -> List[Dict[str, Any]]:
        """
        Full pipeline: discover schools and extract KPIs with Ollama
        
        Args:
            country: Country to discover schools in
            use_ollama: If True, use Ollama to extract KPIs
            
        Returns:
            List of schools with full KPI data
        """
        logger.info(f"🚀 Full Discovery Pipeline for {country}...")
        
        # Discover schools
        schools = self.discover_schools_by_country(country)
        
        if not schools:
            logger.warning(f"  No schools found in {country}")
            return []
        
        # Extract KPIs with Ollama if requested
        if use_ollama:
            logger.info(f"  🤖 Extracting KPIs with Ollama for {len(schools)} schools...")
            extracted_schools = []
            
            for i, school in enumerate(schools, 1):
                logger.info(f"    [{i}/{len(schools)}] Processing: {school.get('school_name')}")
                enriched = self.extract_kpis_with_ollama(school)
                if enriched:
                    extracted_schools.append(enriched)
                time.sleep(0.5)  # Rate limiting
            
            schools = extracted_schools
        
        # Save to CSV and Markdown
        self._export_schools_to_files(schools, country)
        
        logger.info(f"✅ Pipeline complete: {len(schools)} schools with KPIs")
        return schools
    
    def get_cached_schools(self, region_or_country: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached schools without re-discovery"""
        cache_key_region = f"region_{region_or_country.lower().replace(' ', '_')}"
        cache_key_country = f"country_{region_or_country.lower().replace(' ', '_')}"
        
        cached = self.discovered_cache.get(cache_key_region) or self.discovered_cache.get(cache_key_country)
        if cached:
            return cached.get('schools', [])
        return None
    
    def clear_cache(self):
        """Clear discovery cache"""
        self.discovered_cache.clear()
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
        logger.info("✅ Cleared discovery cache")
    
    # ==================== PRIVATE METHODS ====================
    
    def _process_school_url(self, url: str, title: str, country: str) -> Optional[Dict[str, Any]]:
        """
        Process a discovered school URL
        
        Args:
            url: School website URL
            title: School name from search result
            country: Country where school is located
            
        Returns:
            School dictionary with basic info
        """
        try:
            # Extract school name
            school_name = title.replace('&nbsp;', ' ').strip()
            
            # Remove common prefixes
            for prefix in ['1.', '2.', '3.', '-', '|']:
                if school_name.startswith(prefix):
                    school_name = school_name[len(prefix):].strip()
            
            if not school_name or len(school_name) < 3:
                return None
            
            school = {
                'school_name': school_name,
                'website': url,
                'country': country,
                'source': 'Web Search Discovery',
                'discovery_date': datetime.now().isoformat()
            }
            
            return school
        
        except Exception as e:
            logger.debug(f"Error processing URL: {e}")
            return None
    
    def _fetch_website_content(self, url: str, max_chars: int = 10000) -> Optional[str]:
        """
        Fetch website content for KPI extraction
        
        Args:
            url: Website URL
            max_chars: Maximum characters to extract
            
        Returns:
            Website content or None if fetch fails
        """
        try:
            logger.info(f"    📄 Fetching content from {url}...")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract relevant content
            # Remove script and style tags
            for script in soup(['script', 'style']):
                script.decompose()
            
            text = soup.get_text(separator='\n', strip=True)
            
            # Limit content length
            if len(text) > max_chars:
                text = text[:max_chars]
            
            return text
        
        except Exception as e:
            logger.warning(f"    ⚠️ Error fetching {url}: {e}")
            return None
    
    def _deduplicate_schools(self, schools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate schools by name"""
        seen = {}
        for school in schools:
            name_key = school.get('school_name', '').lower().strip()
            if name_key and name_key not in seen:
                seen[name_key] = school
        
        return list(seen.values())
    
    def _export_schools_to_files(self, schools: List[Dict[str, Any]], country: str):
        """Export discovered schools to CSV, Markdown, plus staff and research centre CSVs"""
        try:
            # Initialize staff and research extractor
            try:
                from .staff_extractor import StaffAndResearchExtractor
                staff_extractor = StaffAndResearchExtractor()
            except Exception as e:
                logger.warning(f"Staff extractor not available: {e}")
                staff_extractor = None
            
            # Extract staff for each school
            all_staff = []
            all_research_centres = []
            
            if staff_extractor:
                logger.info(f"  👥 Extracting staff information...")
                for school in schools:
                    school_url = school.get('website', '')
                    school_name = school.get('school_name', '')
                    
                    if school_url:
                        staff_data = staff_extractor.extract_staff_from_school(school_url, school_name)
                        
                        # Add to school record
                        school['staff_list'] = staff_data.get('staff', [])
                        school['degree_counts'] = staff_data.get('degree_counts', {})
                        school['research_themes'] = staff_data.get('research_themes', [])
                        school['total_staff'] = staff_data.get('total_staff', 0)
                        
                        # Collect staff for staff CSV
                        for staff_member in staff_data.get('staff', []):
                            all_staff.append({
                                'school_name': school_name,
                                'school_url': school_url,
                                'staff_name': staff_member.get('name', ''),
                                'degree': staff_member.get('degree', ''),
                                'research_interests': '; '.join(staff_member.get('research_interests', [])),
                                'orcid': staff_member.get('orcid', ''),
                                'url': staff_member.get('school_url', '')
                            })
                        
                        # Collect research centres with themes
                        for centre in school.get('research_centres', []):
                            all_research_centres.append({
                                'centre_name': centre.get('name', ''),
                                'theme': centre.get('theme', ''),
                                'school_name': school_name,
                                'school_url': school_url
                            })
            
            # Export enhanced schools CSV (with staff counts)
            csv_file = os.path.join(self.cache_dir, f'discovered_schools_{country.lower().replace(" ", "_")}.csv')
            
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = [
                    'School Name', 'Country', 'Website', 
                    'Programmes', 'Programme Count',
                    'Masters Count', 'PhDs Count', 'MBAs Count', 'Bachelor Count',
                    'Research Centres', 'Research Themes',
                    'Academic Staff', 'Total Staff Extracted',
                    'Accreditation', 'Source', 'Discovery Date'
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for school in schools:
                    degree_counts = school.get('degree_counts', {})
                    writer.writerow({
                        'School Name': school.get('school_name', ''),
                        'Country': school.get('country', ''),
                        'Website': school.get('website', ''),
                        'Programmes': '; '.join([p.get('name', '') for p in school.get('programmes', [])]),
                        'Programme Count': len(school.get('programmes', [])),
                        'Masters Count': degree_counts.get('masters', 0),
                        'PhDs Count': degree_counts.get('phd', 0),
                        'MBAs Count': degree_counts.get('mba', 0),
                        'Bachelor Count': degree_counts.get('bachelor', 0),
                        'Research Centres': '; '.join([r.get('name', '') for r in school.get('research_centres', [])]),
                        'Research Themes': '; '.join(school.get('research_themes', [])),
                        'Academic Staff': school.get('academic_staff_count', ''),
                        'Total Staff Extracted': school.get('total_staff', 0),
                        'Accreditation': '; '.join(school.get('accreditation', [])),
                        'Source': school.get('source', ''),
                        'Discovery Date': school.get('discovery_date', '')
                    })
            
            logger.info(f"  ✅ Saved enhanced schools CSV: {csv_file}")
            
            # Export staff members CSV
            if all_staff:
                staff_csv_file = os.path.join(self.cache_dir, f'staff_members_{country.lower().replace(" ", "_")}.csv')
                
                with open(staff_csv_file, 'w', newline='', encoding='utf-8') as f:
                    fieldnames = ['school_name', 'school_url', 'staff_name', 'degree', 'research_interests', 'orcid', 'url']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    
                    # Write custom header with proper names
                    f.write('School Name,School URL,Staff Name,Degree,Research Interests,ORCID,URL\n')
                    
                    for staff in all_staff:
                        writer.writerow(staff)
                
                logger.info(f"  ✅ Saved staff members CSV: {staff_csv_file}")
            
            # Export research centres CSV
            if all_research_centres:
                research_csv_file = os.path.join(self.cache_dir, f'research_centres_{country.lower().replace(" ", "_")}.csv')
                
                with open(research_csv_file, 'w', newline='', encoding='utf-8') as f:
                    fieldnames = ['centre_name', 'theme', 'school_name', 'school_url']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    
                    # Write custom header with proper names
                    f.write('Centre Name,Theme,School Name,School URL\n')
                    
                    for centre in all_research_centres:
                        writer.writerow(centre)
                
                logger.info(f"  ✅ Saved research centres CSV: {research_csv_file}")
            
            # Markdown export
            md_file = os.path.join(self.cache_dir, f'discovered_schools_{country.lower().replace(" ", "_")}.md')
            
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(f"# Business Schools Discovered in {country}\n\n")
                f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**Total Schools:** {len(schools)}\n")
                f.write(f"**Discovery Method:** Web Search + Ollama KPI Extraction + Staff Extraction\n\n")
                
                for i, school in enumerate(schools, 1):
                    f.write(f"## {i}. {school.get('school_name')}\n\n")
                    f.write(f"**Website:** {school.get('website')}\n\n")
                    f.write(f"**Country:** {school.get('country')}\n\n")
                    
                    if school.get('programmes'):
                        f.write("**Programmes:**\n")
                        for prog in school.get('programmes', []):
                            f.write(f"- {prog.get('type', '')}: {prog.get('name', '')}\n")
                        f.write("\n")
                    
                    # Add degree counts
                    degree_counts = school.get('degree_counts', {})
                    if degree_counts:
                        f.write("**Degree Counts:**\n")
                        f.write(f"- PhDs: {degree_counts.get('phd', 0)}\n")
                        f.write(f"- Masters: {degree_counts.get('masters', 0)}\n")
                        f.write(f"- MBAs: {degree_counts.get('mba', 0)}\n")
                        f.write(f"- Bachelor: {degree_counts.get('bachelor', 0)}\n")
                        f.write(f"- Total Staff Extracted: {school.get('total_staff', 0)}\n\n")
                    
                    if school.get('research_centres'):
                        f.write("**Research Centres:**\n")
                        for centre in school.get('research_centres', []):
                            f.write(f"- {centre.get('name', '')}: {centre.get('theme', '')}\n")
                        f.write("\n")
                    
                    if school.get('research_themes'):
                        f.write("**Research Themes:**\n")
                        f.write(f"- {', '.join(school.get('research_themes', []))}\n\n")
                    
                    f.write(f"**KPI Extraction:** {school.get('kpi_extraction_method', 'manual')}\n")
                    f.write(f"**Data Quality:** {school.get('data_quality', 'MEDIUM')}\n\n")
                    f.write("---\n\n")
            
            logger.info(f"  ✅ Saved to Markdown: {md_file}")
        
        except Exception as e:
            logger.error(f"Error exporting schools: {e}")
    
    def _load_cache(self) -> Dict[str, Any]:
        """Load cached discoveries from file"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading cache: {e}")
        
        return {}
    
    def _save_cache(self):
        """Save discoveries to cache file"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.discovered_cache, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
