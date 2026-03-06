"""
StaffAndResearchExtractor - Extract detailed staff info, research themes, degrees from business schools
"""

import logging
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any
import re
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class StaffAndResearchExtractor:
    """Extract staff members, degrees, research themes, and ORCID information"""
    
    # Common degree patterns to identify
    DEGREE_PATTERNS = {
        'phd': r'\b(phd|ph\.d|doctorate|dr\.?\s|doctor of philosophy)\b',
        'masters': r'\b(m(\.)?a|m(\.)?sc|m(\.)?ba|mba|master|m\.s|master\'s)\b',
        'mba': r'\b(mba|master of business administration)\b',
        'bachelor': r'\b(b(\.)?a|b(\.)?sc|b(\.)?com|bachelor|undergraduate)\b',
    }
    
    RESEARCH_KEYWORDS = [
        'business strategy', 'entrepreneurship', 'marketing', 'finance',
        'organizational behavior', 'human resources', 'operations', 'management',
        'supply chain', 'corporate governance', 'innovation', 'international business',
        'economics', 'accounting', 'taxation', 'risk management', 'leadership',
        'decision making', 'consumer behavior', 'digital transformation',
        'sustainability', 'business ethics', 'stakeholder management'
    ]
    
    def __init__(self):
        """Initialize staff extractor"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.timeout = 10
    
    def extract_staff_from_school(self, school_url: str, school_name: str) -> Dict[str, Any]:
        """
        Extract staff information from university website
        
        Args:
            school_url: University website URL
            school_name: Name of school
            
        Returns:
            Dict with staff list, degree counts, and research themes
        """
        staff_list = []
        degree_counts = {
            'phd': 0,
            'masters': 0,
            'mba': 0,
            'bachelor': 0,
            'unknown': 0
        }
        research_themes = {}
        
        try:
            # Try to fetch faculty/staff page
            staff_pages = [
                school_url,
                urljoin(school_url, '/about/faculty'),
                urljoin(school_url, '/faculty'),
                urljoin(school_url, '/staff'),
                urljoin(school_url, '/team'),
                urljoin(school_url, '/people'),
            ]
            
            content = None
            for page_url in staff_pages:
                try:
                    response = self.session.get(page_url, timeout=self.timeout)
                    if response.status_code == 200:
                        content = response.text
                        logger.info(f"  ✓ Fetched staff from {page_url}")
                        break
                except Exception:
                    continue
            
            if not content:
                logger.warning(f"  ⚠️ Could not fetch staff page for {school_name}")
                return {
                    'school_name': school_name,
                    'staff': [],
                    'degree_counts': degree_counts,
                    'research_themes': []
                }
            
            # Parse content
            soup = BeautifulSoup(content, 'html.parser')
            text_content = soup.get_text()
            
            # Extract staff names (look for patterns like "Dr. John Smith", "Prof. Jane Doe")
            name_patterns = [
                r'(?:Dr\.|Prof\.|Professor|Dr)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
                r'(?:Mr\.|Ms\.|Mrs\.)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            ]
            
            found_names = set()
            for pattern in name_patterns:
                matches = re.finditer(pattern, text_content)
                for match in matches:
                    name = match.group(1).strip()
                    if len(name) > 3 and name not in found_names:
                        found_names.add(name)
                        
                        # Determine degree from surrounding context
                        context_window = 200
                        context_start = max(0, match.start() - context_window)
                        context_end = min(len(text_content), match.end() + context_window)
                        context = text_content[context_start:context_end].lower()
                        
                        degree = self._identify_degree(context)
                        
                        # Extract research interests (look for keywords near name)
                        research_interests = self._extract_research_interests(context)
                        
                        # Try to find ORCID
                        orcid = self._extract_orcid(context)
                        
                        staff_member = {
                            'name': name,
                            'degree': degree,
                            'research_interests': research_interests,
                            'orcid': orcid,
                            'school_url': school_url
                        }
                        
                        staff_list.append(staff_member)
                        degree_counts[degree] += 1
            
            # Extract research themes from page
            for theme in self.RESEARCH_KEYWORDS:
                count = text_content.lower().count(theme)
                if count > 0:
                    research_themes[theme] = count
            
            # Sort themes by frequency
            research_themes = dict(sorted(research_themes.items(), key=lambda x: x[1], reverse=True))
            
        except Exception as e:
            logger.error(f"  ❌ Error extracting staff from {school_name}: {e}")
        
        return {
            'school_name': school_name,
            'school_url': school_url,
            'staff': staff_list,
            'degree_counts': degree_counts,
            'research_themes': list(research_themes.keys())[:5],  # Top 5 themes
            'total_staff': len(staff_list)
        }
    
    def _identify_degree(self, context: str) -> str:
        """Identify degree level from context"""
        degree_order = ['phd', 'mba', 'masters', 'bachelor']
        
        for degree in degree_order:
            pattern = self.DEGREE_PATTERNS[degree]
            if re.search(pattern, context, re.IGNORECASE):
                return degree
        
        return 'unknown'
    
    def _extract_research_interests(self, context: str) -> List[str]:
        """Extract research interests from context"""
        interests = []
        
        # Look for explicit "research interests" or "areas of expertise"
        interest_section = re.search(
            r'(?:research interests?|areas of expertise|research focus)[:\s]*([^.\n]*)',
            context,
            re.IGNORECASE
        )
        
        if interest_section:
            text = interest_section.group(1)
            # Extract keywords or phrases
            interests = [x.strip() for x in text.split(',') if x.strip()]
        
        # Also check for research keyword matches
        for keyword in self.RESEARCH_KEYWORDS[:10]:
            if keyword.lower() in context:
                if keyword not in interests:
                    interests.append(keyword)
        
        return interests[:5]  # Return top 5
    
    def _extract_orcid(self, context: str) -> Optional[str]:
        """Extract ORCID identifier if present"""
        orcid_pattern = r'(?:orcid|orcid\.org)[:\s/]*(\d{4}-\d{4}-\d{4}-\d{3}[0-9X])'
        match = re.search(orcid_pattern, context, re.IGNORECASE)
        
        if match:
            return match.group(1)
        return None
