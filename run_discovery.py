#!/usr/bin/env python
"""
Comprehensive Business School Discovery Runner
Run discovery for all African countries with beautiful terminal output
Ready to scale to Europe, Asia, and other continents
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from health_app.services.business_school_kpi import BusinessSchoolDiscoverer

# ANSI Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    DIM = '\033[2m'

class PrettyPrinter:
    """Pretty print results to terminal"""
    
    @staticmethod
    def header(text, char="="):
        """Print a header with decorative characters"""
        width = 100
        print(f"\n{Colors.HEADER}{Colors.BOLD}{char * width}")
        print(f"{text.center(width)}")
        print(f"{char * width}{Colors.ENDC}\n")
    
    @staticmethod
    def subheader(text, char="-"):
        """Print a subheader"""
        width = 90
        print(f"{Colors.OKBLUE}{Colors.BOLD}{char * width}")
        print(f"{text.ljust(90)}")
        print(f"{char * width}{Colors.ENDC}")
    
    @staticmethod
    def success(text):
        """Print success message"""
        print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")
    
    @staticmethod
    def warning(text):
        """Print warning message"""
        print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")
    
    @staticmethod
    def error(text):
        """Print error message"""
        print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")
    
    @staticmethod
    def info(text):
        """Print info message"""
        print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")
    
    @staticmethod
    def table_header(columns: List[str], widths: List[int]):
        """Print table header"""
        row = ""
        for col, width in zip(columns, widths):
            row += col.ljust(width) + " │ "
        print(f"{Colors.BOLD}{row[:-3]}{Colors.ENDC}")
        print(f"{Colors.DIM}{'-'.ljust(sum(widths) + (len(widths)-1)*3, '-')}{Colors.ENDC}")
    
    @staticmethod
    def table_row(values: List[str], widths: List[int], color=None):
        """Print table row"""
        row = ""
        for val, width in zip(values, widths):
            row += str(val).ljust(width) + " │ "
        if color:
            print(f"{color}{row[:-3]}{Colors.ENDC}")
        else:
            print(row[:-3])

class DiscoveryRunner:
    """Run discovery for multiple regions/continents"""
    
    # Define region configurations
    REGIONS = {
        'Africa': {
            'countries': [
                'Zimbabwe', 'South Africa', 'Nigeria', 'Kenya',
                'Ethiopia', 'Ghana', 'Morocco', 'Botswana'
            ],
            'emoji': '🌍'
        },
        'Europe': {
            'countries': [
                'United Kingdom', 'Germany', 'France', 'Spain', 'Italy',
                'Netherlands', 'Belgium', 'Switzerland', 'Austria', 'Sweden'
            ],
            'emoji': '🏛️'
        },
        'Asia': {
            'countries': [
                'India', 'China', 'Japan', 'Singapore', 'South Korea',
                'Thailand', 'Philippines', 'Vietnam', 'Malaysia', 'Indonesia'
            ],
            'emoji': '🏯'
        },
        'Americas': {
            'countries': [
                'United States', 'Canada', 'Brazil', 'Mexico', 'Argentina',
                'Colombia', 'Chile', 'Peru', 'Venezuela', 'Ecuador'
            ],
            'emoji': '🗽'
        }
    }
    
    def __init__(self):
        """Initialize discovery runner"""
        self.discoverer = BusinessSchoolDiscoverer()
        self.results = {}
    
    def run_region(self, region_name: str, use_ollama=False) -> Dict:
        """Run discovery for all countries in a region"""
        if region_name not in self.REGIONS:
            PrettyPrinter.error(f"Region '{region_name}' not found")
            return {}
        
        region_config = self.REGIONS[region_name]
        countries = region_config['countries']
        emoji = region_config['emoji']
        
        PrettyPrinter.header(f"{emoji}  {region_name.upper()} - BUSINESS SCHOOL DISCOVERY", "═")
        
        region_stats = {
            'region': region_name,
            'total_countries': len(countries),
            'countries_processed': 0,
            'total_schools': 0,
            'total_schools_with_programmes': 0,
            'total_schools_with_research': 0,
            'total_staff_extracted': 0,
            'country_results': {}
        }
        
        # Table header
        columns = ['Country', 'Schools', 'Programmes', 'Research', 'Staff', 'Files']
        widths = [20, 12, 14, 12, 10, 8]
        print()
        PrettyPrinter.table_header(columns, widths)
        
        # Run discovery for each country
        for country in countries:
            try:
                # Run discovery
                schools = self.discoverer.discover_and_extract(country, use_ollama=use_ollama)
                
                # Gather statistics
                schools_with_prog = len([s for s in schools if s.get('programmes')])
                schools_with_research = len([s for s in schools if s.get('research_centres')])
                
                # Count staff
                cache_dir = self.discoverer.cache_dir
                staff_csv = os.path.join(cache_dir, f'staff_members_{country.lower().replace(" ", "_")}.csv')
                staff_count = 0
                if os.path.exists(staff_csv):
                    with open(staff_csv, 'r', encoding='utf-8') as f:
                        staff_count = sum(1 for _ in f) - 1  # Subtract header
                
                # Check for export files
                csv_files = sum(1 for _ in Path(cache_dir).glob(f'*{country.lower().replace(" ", "_")}.csv'))
                md_files = sum(1 for _ in Path(cache_dir).glob(f'*{country.lower().replace(" ", "_")}.md'))
                total_files = csv_files + md_files
                
                # Update statistics
                region_stats['countries_processed'] += 1
                region_stats['total_schools'] += len(schools)
                region_stats['total_schools_with_programmes'] += schools_with_prog
                region_stats['total_schools_with_research'] += schools_with_research
                region_stats['total_staff_extracted'] += staff_count
                
                country_key = country.lower().replace(' ', '_')
                region_stats['country_results'][country_key] = {
                    'schools': len(schools),
                    'programmes': schools_with_prog,
                    'research': schools_with_research,
                    'staff': staff_count,
                    'files': total_files
                }
                
                # Print table row
                values = [
                    country,
                    str(len(schools)),
                    str(schools_with_prog),
                    str(schools_with_research),
                    str(staff_count),
                    str(total_files)
                ]
                color = Colors.OKGREEN if len(schools) > 0 else Colors.WARNING
                PrettyPrinter.table_row(values, widths, color=color)
                
            except Exception as e:
                PrettyPrinter.error(f"{country}: {str(e)}")
                values = [country, "ERROR", "-", "-", "-", "-"]
                PrettyPrinter.table_row(values, widths, color=Colors.FAIL)
        
        print()
        return region_stats
    
    def print_region_summary(self, region_stats: Dict):
        """Print summary for a region"""
        PrettyPrinter.subheader("📊 REGION SUMMARY")
        
        print(f"\n{Colors.BOLD}Region:{Colors.ENDC} {region_stats['region'].upper()}")
        print(f"{Colors.BOLD}Timestamp:{Colors.ENDC} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        summary_items = [
            ("Countries Processed", region_stats['countries_processed']),
            ("Total Schools Discovered", region_stats['total_schools']),
            ("Schools with Programmes", region_stats['total_schools_with_programmes']),
            ("Schools with Research Centers", region_stats['total_schools_with_research']),
            ("Staff Members Extracted", region_stats['total_staff_extracted']),
        ]
        
        for label, value in summary_items:
            print(f"  {Colors.OKCYAN}→{Colors.ENDC} {label.ljust(35)}: {Colors.BOLD}{value}{Colors.ENDC}")
        
        print()
    
    def print_global_summary(self):
        """Print global summary across all regions"""
        PrettyPrinter.header("🌐 GLOBAL SUMMARY", "═")
        
        total_countries = 0
        total_schools = 0
        total_programmes = 0
        total_research = 0
        total_staff = 0
        
        for region_name, stats in self.results.items():
            total_countries += stats['countries_processed']
            total_schools += stats['total_schools']
            total_programmes += stats['total_schools_with_programmes']
            total_research += stats['total_schools_with_research']
            total_staff += stats['total_staff_extracted']
        
        # Global statistics
        print(f"\n{Colors.BOLD}🌍 GLOBAL DISCOVERY STATISTICS{Colors.ENDC}\n")
        
        global_stats = [
            ("Regions Processed", len(self.results)),
            ("Total Countries", total_countries),
            ("Total Business Schools", total_schools),
            ("Schools with Programmes", total_programmes),
            ("Schools with Research Centers", total_research),
            ("Staff Members Extracted", total_staff),
        ]
        
        for label, value in global_stats:
            bar_length = 40
            percentage = 0
            if label == "Schools with Programmes" and total_schools > 0:
                percentage = (value / total_schools) * 100
            elif label == "Schools with Research Centers" and total_schools > 0:
                percentage = (value / total_schools) * 100
            
            bar = "█" * int((percentage or 0) / 2.5) + "░" * (40 - int((percentage or 0) / 2.5))
            
            if percentage:
                print(f"  {Colors.BOLD}{label.ljust(35)}{Colors.ENDC}: {Colors.OKGREEN}{value:>5}{Colors.ENDC} ({bar}) {percentage:.1f}%")
            else:
                print(f"  {Colors.BOLD}{label.ljust(35)}{Colors.ENDC}: {Colors.OKGREEN}{value:>5}{Colors.ENDC}")
        
        print()
    
    def run(self, regions: List[str], use_ollama=False):
        """Run discovery for specified regions"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}")
        print("╔" + "═" * 98 + "╗")
        print("║" + "BUSINESS SCHOOL DISCOVERY SYSTEM - MULTI-REGION RUNNER".center(98) + "║")
        print("╚" + "═" * 98 + "╝")
        print(Colors.ENDC)
        
        PrettyPrinter.info(f"Starting discovery for: {', '.join(regions)}")
        PrettyPrinter.info(f"LLM Extraction: {'Enabled (Ollama)' if use_ollama else 'Disabled (Fast mode)'}")
        PrettyPrinter.info(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        start_time = datetime.now()
        
        for region in regions:
            if region in self.REGIONS:
                stats = self.run_region(region, use_ollama=use_ollama)
                self.results[region] = stats
                self.print_region_summary(stats)
            else:
                PrettyPrinter.error(f"Region '{region}' not configured")
        
        # Print global summary
        if len(self.results) > 1:
            self.print_global_summary()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        PrettyPrinter.header("✨ DISCOVERY COMPLETE", "═")
        print(f"{Colors.OKGREEN}All regions processed successfully!{Colors.ENDC}")
        print(f"Total Duration: {Colors.BOLD}{duration:.1f} seconds{Colors.ENDC}\n")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Run Business School Discovery across regions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Run African countries only
  python run_discovery.py --regions Africa
  
  # Run all continents
  python run_discovery.py --regions Africa Europe Asia Americas
  
  # Run with Ollama LLM extraction
  python run_discovery.py --regions Africa Europe --ollama
        '''
    )
    
    parser.add_argument(
        '--regions',
        nargs='+',
        default=['Africa'],
        choices=['Africa', 'Europe', 'Asia', 'Americas'],
        help='Regions to run discovery for (default: Africa)'
    )
    
    parser.add_argument(
        '--ollama',
        action='store_true',
        help='Enable Ollama LLM for KPI extraction (slower but more accurate)'
    )
    
    args = parser.parse_args()
    
    runner = DiscoveryRunner()
    runner.run(args.regions, use_ollama=args.ollama)

if __name__ == '__main__':
    main()
