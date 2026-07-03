"""
OllamaKPIExtractor - Uses Ollama (local LLM) to extract KPIs from website content

Sends website text to Ollama with a specialized prompt to extract:
- Programmes (MBA, EXECUTIVE, MA, POSTGRADUATE, etc.)
- Research centres and themes
- Academic staff and disciplines
- Accreditation standards
"""

import logging
import json
import re
import os
from typing import Dict, List, Optional, Any
import requests

logger = logging.getLogger(__name__)
DEFAULT_OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'ministral-3:3b')


class OllamaKPIExtractor:
    """Extract KPIs from website content using Ollama"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        """
        Initialize Ollama extractor
        
        Args:
            ollama_url: Ollama API endpoint (default: localhost:11434)
        """
        self.ollama_url = ollama_url
        self.model = DEFAULT_OLLAMA_MODEL
        self.timeout = 30
        
        # Check if Ollama is available
        self.available = self._check_ollama_available()
        
        if self.available:
            logger.info(f"✅ Ollama available at {ollama_url}")
        else:
            logger.warning(f"⚠️ Ollama not available at {ollama_url} - KPI extraction will be limited")
    
    def extract_kpis_from_content(self, content: str, school_name: str) -> Dict[str, Any]:
        """
        Extract structured KPIs from website content using Ollama
        
        Args:
            content: Website text content
            school_name: Name of the school (for context)
            
        Returns:
            Dictionary with extracted programmes, research centres, staff, etc.
        """
        kpis = {
            'programmes': [],
            'research_centres': [],
            'academic_staff_disciplines': {},
            'academic_staff_count': 0,
            'accreditation': [],
            'data_quality': 'MEDIUM'
        }
        
        if not self.available:
            logger.warning("  ⚠️ Ollama not available - using pattern matching instead")
            return self._extract_kpis_with_patterns(content, kpis)
        
        try:
            # Create extraction prompt
            prompt = self._create_extraction_prompt(content, school_name)
            
            logger.info(f"    📤 Sending content to Ollama ({len(content)} chars)...")
            
            # Call Ollama API
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.3  # Lower temperature for accurate extraction
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                extracted_text = result.get('response', '')
                
                logger.info(f"    ✓ Ollama response received ({len(extracted_text)} chars)")
                
                # Parse Ollama's response
                kpis = self._parse_ollama_response(extracted_text, kpis)
                kpis['extraction_method'] = 'ollama'
            else:
                logger.warning(f"    ⚠️ Ollama error: {response.status_code}")
                kpis = self._extract_kpis_with_patterns(content, kpis)
        
        except requests.exceptions.ConnectionError:
            logger.warning("    ⚠️ Cannot connect to Ollama - using pattern matching")
            kpis = self._extract_kpis_with_patterns(content, kpis)
        except Exception as e:
            logger.warning(f"    ⚠️ Error calling Ollama: {e}")
            kpis = self._extract_kpis_with_patterns(content, kpis)
        
        return kpis
    
    def _create_extraction_prompt(self, content: str, school_name: str) -> str:
        """
        Create a prompt for Ollama to extract KPIs from content
        
        Args:
            content: Website content
            school_name: School name for context
            
        Returns:
            Structured prompt for Ollama
        """
        # Limit content size for API
        if len(content) > 4000:
            content = content[:4000] + "\n... [content truncated]"
        
        prompt = f"""Extract key business school information from this website content.

School Name: {school_name}

Website Content:
{content}

Please extract and format as JSON with the following structure:
{{
  "programmes": [
    {{"type": "MBA", "name": "Master of Business Administration"}},
    {{"type": "EXECUTIVE", "name": "Executive MBA"}}
  ],
  "research_centres": [
    {{"name": "Finance Research Centre", "theme": "Finance and Banking"}}
  ],
  "academic_staff_disciplines": {{
    "Finance": 25,
    "Strategy": 20,
    "Marketing": 18
  }},
  "academic_staff_count": 150,
  "accreditation": ["AACSB", "EQUIS", "AMBA"]
}}

Extract ONLY what is clearly mentioned. Use empty arrays/objects for missing data.
Return ONLY the JSON, no other text."""
        
        return prompt
    
    def _parse_ollama_response(self, response_text: str, default_kpis: Dict) -> Dict[str, Any]:
        """
        Parse Ollama's response and extract JSON
        
        Args:
            response_text: Ollama's text response
            default_kpis: Default KPI structure
            
        Returns:
            Extracted KPIs dictionary
        """
        try:
            # Find JSON in response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                extracted = json.loads(json_str)
                
                # Merge with defaults
                kpis = default_kpis.copy()
                kpis['programmes'] = extracted.get('programmes', [])
                kpis['research_centres'] = extracted.get('research_centres', [])
                kpis['academic_staff_disciplines'] = extracted.get('academic_staff_disciplines', {})
                kpis['academic_staff_count'] = extracted.get('academic_staff_count', 0)
                kpis['accreditation'] = extracted.get('accreditation', [])
                
                logger.info(f"    ✓ Parsed: {len(kpis['programmes'])} programmes, {len(kpis['research_centres'])} centres")
                
                return kpis
        except json.JSONDecodeError as e:
            logger.warning(f"    ⚠️ Error parsing Ollama JSON: {e}")
        
        return default_kpis
    
    def _extract_kpis_with_patterns(self, content: str, kpis: Dict) -> Dict[str, Any]:
        """
        Fallback: Extract KPIs using regex patterns
        Used when Ollama is not available
        
        Args:
            content: Website content
            kpis: Default KPI structure
            
        Returns:
            Extracted KPIs dictionary
        """
        logger.info("    🔎 Extracting KPIs with pattern matching...")
        content_lower = content.lower()
        
        # Extract programmes
        programme_patterns = {
            'MBA': [r'\bmba\b', r'master of business'],
            'EXECUTIVE': [r'executive mba', r'emba', r'executive education'],
            'MA': [r'\bma\b', r'master of arts'],
            'POSTGRADUATE': [r'postgraduate', r'pgdip', r'graduate diploma'],
            'BACHELOR': [r'bachelor', r'undergraduate', r'bba'],
            'PDH': [r'pdh', r'cpd', r'professional development']
        }
        
        for prog_type, patterns in programme_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    kpis['programmes'].append({
                        'type': prog_type,
                        'name': f'{prog_type} Programme'
                    })
                    break
        
        # Extract research centres
        centre_keywords = ['research centre', 'research center', 'institute', 'lab', 'laboratory', 'department']
        for keyword in centre_keywords:
            if keyword in content_lower:
                kpis['research_centres'].append({
                    'name': f'{keyword.title()} Research',
                    'theme': 'Business Research'
                })
                break
        
        # Extract accreditation
        accred_patterns = {
            'AACSB': [r'aacsb', r'aacsb international'],
            'EQUIS': [r'equis', r'european quality'],
            'AMBA': [r'amba', r'association of mbas']
        }
        
        for accred, patterns in accred_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    kpis['accreditation'].append(accred)
                    break
        
        # Default to MBA if nothing found
        if not kpis['programmes']:
            kpis['programmes'].append({
                'type': 'MBA',
                'name': 'MBA Programme'
            })
        
        # Extract staff count if mentioned
        staff_match = re.search(r'(\d+)\s+(?:faculty|staff|professor|academic)', content_lower)
        if staff_match:
            kpis['academic_staff_count'] = int(staff_match.group(1))
        
        kpis['extraction_method'] = 'pattern_matching'
        
        logger.info(f"    ✓ Extracted: {len(kpis['programmes'])} programmes, {len(kpis['accreditation'])} accreditations")
        
        return kpis
    
    def _check_ollama_available(self) -> bool:
        """Check if Ollama API is available"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                return True
        except:
            pass
        return False
    
    def test_connection(self) -> Dict[str, Any]:
        """Test Ollama connection and return info"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = [m.get('name', '') for m in data.get('models', [])]
                return {
                    'available': True,
                    'url': self.ollama_url,
                    'models': models,
                    'message': f'✅ Ollama is running with {len(models)} models'
                }
        except Exception as e:
            return {
                'available': False,
                'url': self.ollama_url,
                'models': [],
                'message': f'❌ Ollama not available: {e}'
            }
