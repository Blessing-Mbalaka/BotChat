"""
South Africa Medical Resources Service
Provides links to medical doctors, clinics, and relevant medical information in South Africa
"""

import json
import requests
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class SouthAfricaMedicalService:
    """Service to provide South African medical resources and doctor links"""
    
    def __init__(self):
        self.medical_directories = {
            "doctor_directories": [
                {
                    "name": "Mediclinic",
                    "url": "https://www.mediclinic.co.za/en/find-a-doctor",
                    "description": "Find doctors and specialists at Mediclinic hospitals across South Africa"
                },
                {
                    "name": "Netcare",
                    "url": "https://www.netcare.co.za/Find-a-doctor",
                    "description": "Locate doctors and medical specialists in the Netcare network"
                },
                {
                    "name": "Discovery Health",
                    "url": "https://www.discovery.co.za/portal/individual/medical-aid-quote-application-landing-page",
                    "description": "Discovery Health medical scheme provider network"
                },
                {
                    "name": "HPCSA (Health Professions Council)",
                    "url": "https://www.hpcsa.co.za/register/",
                    "description": "Official register of healthcare practitioners in South Africa"
                },
                {
                    "name": "Medical Specialist Directory",
                    "url": "https://www.medical-specialists.co.za/",
                    "description": "Comprehensive directory of medical specialists in South Africa"
                }
            ],
            "emergency_services": [
                {
                    "name": "ER24",
                    "url": "https://www.er24.co.za/",
                    "phone": "084 124",
                    "description": "Private emergency medical services across South Africa"
                },
                {
                    "name": "Netcare 911",
                    "url": "https://www.netcare911.co.za/",
                    "phone": "082 911",
                    "description": "Emergency medical response and ambulance services"
                },
                {
                    "name": "Provincial Emergency Services",
                    "phone": "10177",
                    "description": "Government emergency medical services"
                }
            ],
            "major_hospitals": [
                {
                    "name": "Groote Schuur Hospital (Cape Town)",
                    "url": "https://www.westerncape.gov.za/dept/health/hospital/groote-schuur",
                    "location": "Cape Town, Western Cape",
                    "type": "Public Academic Hospital"
                },
                {
                    "name": "Chris Hani Baragwanath Hospital (Johannesburg)",
                    "url": "https://www.gauteng.gov.za/government/departments/health/hospitals/pages/chris-hani-baragwanath-academic-hospital.aspx",
                    "location": "Soweto, Johannesburg",
                    "type": "Public Academic Hospital"
                },
                {
                    "name": "Charlotte Maxeke Hospital (Johannesburg)",
                    "url": "https://www.gauteng.gov.za/government/departments/health/hospitals/pages/charlotte-maxeke-johannesburg-academic-hospital.aspx",
                    "location": "Johannesburg, Gauteng",
                    "type": "Public Academic Hospital"
                },
                {
                    "name": "Inkosi Albert Luthuli Hospital (Durban)",
                    "url": "https://www.kznhealth.gov.za/ialch.htm",
                    "location": "Durban, KwaZulu-Natal",
                    "type": "Public Academic Hospital"
                }
            ],
            "health_organizations": [
                {
                    "name": "South African Medical Association (SAMA)",
                    "url": "https://www.samedical.org/",
                    "description": "Professional association for medical doctors in South Africa"
                },
                {
                    "name": "Department of Health",
                    "url": "https://www.health.gov.za/",
                    "description": "South African National Department of Health"
                },
                {
                    "name": "South African Nursing Council",
                    "url": "https://www.sanc.co.za/",
                    "description": "Regulatory body for nursing profession in South Africa"
                }
            ]
        }
        
        self.medical_article_sources = {
            "south_african_medical": [
                {
                    "name": "South African Medical Journal",
                    "url": "https://www.samj.org.za/",
                    "description": "Premier medical journal of South Africa"
                },
                {
                    "name": "Wits Health Consortium",
                    "url": "https://www.witshealth.co.za/",
                    "description": "Research and medical publications from University of Witwatersrand"
                },
                {
                    "name": "UCT Faculty of Health Sciences",
                    "url": "https://www.health.uct.ac.za/",
                    "description": "Medical research and publications from University of Cape Town"
                }
            ],
            "health_news": [
                {
                    "name": "Health24",
                    "url": "https://www.health24.com/",
                    "description": "South Africa's leading health and medical news website"
                },
                {
                    "name": "Medical Chronicle",
                    "url": "https://www.medicalchronicle.co.za/",  
                    "description": "Medical news and professional updates for healthcare practitioners"
                }
            ]
        }

    def get_doctor_directories(self, specialty: str = None, location: str = None) -> List[Dict[str, Any]]:
        """Get relevant doctor directory links based on specialty or location"""
        directories = self.medical_directories["doctor_directories"].copy()
        
        # Add contextual information based on parameters
        if specialty:
            for directory in directories:
                directory["search_tip"] = f"Use their search function to find {specialty} specialists"
        
        if location:
            for directory in directories:
                directory["location_tip"] = f"Filter results for {location} area"
        
        return directories

    def get_emergency_services(self) -> List[Dict[str, Any]]:
        """Get emergency medical services information"""
        return self.medical_directories["emergency_services"]

    def get_major_hospitals(self, location: str = None) -> List[Dict[str, Any]]:
        """Get major hospital information, optionally filtered by location"""
        hospitals = self.medical_directories["major_hospitals"]
        
        if location:
            # Simple location matching
            location_lower = location.lower()
            filtered = []
            for hospital in hospitals:
                if (location_lower in hospital["location"].lower() or 
                    location_lower in hospital["name"].lower()):
                    filtered.append(hospital)
            return filtered if filtered else hospitals
        
        return hospitals

    def get_health_organizations(self) -> List[Dict[str, Any]]:
        """Get health organization and regulatory body information"""
        return self.medical_directories["health_organizations"]

    def get_medical_articles(self, topic: str = None) -> List[Dict[str, Any]]:
        """Get medical article sources relevant to South Africa"""
        articles = []
        articles.extend(self.medical_article_sources["south_african_medical"])
        articles.extend(self.medical_article_sources["health_news"])
        
        if topic:
            for article in articles:
                article["search_suggestion"] = f"Search for '{topic}' on this platform"
        
        return articles

    def search_medical_resources(self, query: str) -> Dict[str, Any]:
        """
        Comprehensive search for medical resources based on query
        Returns doctors, hospitals, articles, and emergency services
        """
        query_lower = query.lower()
        results = {
            "doctors": [],
            "hospitals": [],
            "emergency": [],
            "articles": [],
            "organizations": []
        }
        
        # Determine what type of information is needed
        if any(word in query_lower for word in ["doctor", "specialist", "physician", "gp", "find doctor"]):
            results["doctors"] = self.get_doctor_directories()
        
        if any(word in query_lower for word in ["hospital", "clinic", "medical center"]):
            results["hospitals"] = self.get_major_hospitals()
        
        if any(word in query_lower for word in ["emergency", "ambulance", "urgent", "911"]):
            results["emergency"] = self.get_emergency_services()
        
        if any(word in query_lower for word in ["article", "research", "study", "information", "news"]):
            results["articles"] = self.get_medical_articles()
        
        if any(word in query_lower for word in ["organization", "association", "council", "department"]):
            results["organizations"] = self.get_health_organizations()
        
        # If no specific category detected, provide general overview
        if not any(results.values()):
            results = {
                "doctors": self.get_doctor_directories()[:2],
                "hospitals": self.get_major_hospitals()[:2], 
                "emergency": self.get_emergency_services()[:1],
                "articles": self.get_medical_articles()[:2],
                "organizations": self.get_health_organizations()[:1]
            }
        
        return results

    def format_medical_links_response(self, resources: Dict[str, Any]) -> str:
        """Format medical resources into a user-friendly response with links"""
        response_parts = []
        
        if resources.get("doctors"):
            response_parts.append("🏥 **Medical Doctor Directories in South Africa:**")
            for doc in resources["doctors"][:3]:  # Limit to top 3
                response_parts.append(f"• [{doc['name']}]({doc['url']}) - {doc['description']}")
            response_parts.append("")
        
        if resources.get("hospitals"):
            response_parts.append("🏨 **Major Hospitals:**")
            for hospital in resources["hospitals"][:3]:
                response_parts.append(f"• **{hospital['name']}** - {hospital['location']}")
                if hospital.get("url"):
                    response_parts.append(f"  [{hospital['name']} Website]({hospital['url']})")
            response_parts.append("")
        
        if resources.get("emergency"):
            response_parts.append("🚑 **Emergency Medical Services:**")
            for emergency in resources["emergency"]:
                if emergency.get("phone"):
                    response_parts.append(f"• **{emergency['name']}** - Call: {emergency['phone']}")
                if emergency.get("url"):
                    response_parts.append(f"  [Visit Website]({emergency['url']})")
                response_parts.append(f"  {emergency['description']}")
            response_parts.append("")
        
        if resources.get("articles"):
            response_parts.append("📚 **Medical Articles & Research:**")
            for article in resources["articles"][:3]:
                response_parts.append(f"• [{article['name']}]({article['url']}) - {article['description']}")
            response_parts.append("")
        
        if resources.get("organizations"):
            response_parts.append("🏛️ **Health Organizations:**")
            for org in resources["organizations"]:
                response_parts.append(f"• [{org['name']}]({org['url']}) - {org['description']}")
            response_parts.append("")
        
        response_parts.append("💡 **Tip:** Click on any link above to visit the website directly.")
        response_parts.append("⚠️  **Disclaimer:** Always consult with qualified healthcare professionals for medical advice.")
        
        return "\n".join(response_parts)

# Global instance
south_africa_medical_service = SouthAfricaMedicalService()