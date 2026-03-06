"""
Bot Configuration System - Manage system prompts and rules for different bots

This module provides a centralized configuration system for managing:
- System prompts for different bots (chatbot, coursebot, etc.)
- Visualization data provider preferences
- Bot behavior rules

Easy to swap configurations without editing code.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class BotConfig:
    """Configuration container for a bot"""
    
    def __init__(
        self,
        name: str,
        description: str,
        gemini_prompt: str,
        ollama_prompt: str,
        course_prompt: str = None,
        data_provider_mode: str = 'health',  # 'health', 'education', 'general'
        allow_synthetic_data: bool = False,  # Should synthetic data be allowed as fallback?
        visualization_enabled: bool = True,
        metadata: Dict[str, Any] = None
    ):
        self.name = name
        self.description = description
        self.gemini_prompt = gemini_prompt
        self.ollama_prompt = ollama_prompt
        self.course_prompt = course_prompt or gemini_prompt  # Default to gemini_prompt if not specified
        self.data_provider_mode = data_provider_mode
        self.allow_synthetic_data = allow_synthetic_data
        self.visualization_enabled = visualization_enabled
        self.metadata = metadata or {}
    
    def __repr__(self):
        return f"BotConfig({self.name})"


class BotConfigManager:
    """Centralized manager for bot configurations"""
    
    _configs: Dict[str, BotConfig] = {}
    _active_config: Optional[BotConfig] = None
    
    @classmethod
    def register_config(cls, config: BotConfig):
        """Register a new bot configuration"""
        cls._configs[config.name] = config
        logger.info(f"✅ Registered bot config: {config.name}")
    
    @classmethod
    def get_config(cls, name: str) -> Optional[BotConfig]:
        """Get a configuration by name"""
        return cls._configs.get(name)
    
    @classmethod
    def list_configs(cls) -> Dict[str, str]:
        """List all available configurations"""
        return {name: config.description for name, config in cls._configs.items()}
    
    @classmethod
    def set_active_config(cls, name: str) -> bool:
        """Set the active configuration"""
        config = cls.get_config(name)
        if config:
            cls._active_config = config
            logger.info(f"🔄 Switched to config: {name}")
            return True
        logger.warning(f"Configuration not found: {name}")
        return False
    
    @classmethod
    def get_active_config(cls) -> Optional[BotConfig]:
        """Get the currently active configuration"""
        return cls._active_config
    
    @classmethod
    def get_gemini_prompt(cls) -> str:
        """Get the Gemini system prompt for the active config"""
        if cls._active_config:
            return cls._active_config.gemini_prompt
        return _DEFAULT_HEALTH_GEMINI_PROMPT
    
    @classmethod
    def get_ollama_prompt(cls) -> str:
        """Get the Ollama system prompt for the active config"""
        if cls._active_config:
            return cls._active_config.ollama_prompt
        return _DEFAULT_HEALTH_OLLAMA_PROMPT
    
    @classmethod
    def get_course_prompt(cls) -> str:
        """Get the Course service system prompt for the active config"""
        if cls._active_config:
            return cls._active_config.course_prompt
        return _DEFAULT_COURSE_PROMPT
    
    @classmethod
    def get_data_provider_mode(cls) -> str:
        """Get the data provider mode (health, education, general)"""
        if cls._active_config:
            return cls._active_config.data_provider_mode
        return 'health'
    
    @classmethod
    def should_allow_synthetic_data(cls) -> bool:
        """Check if synthetic data is allowed as fallback"""
        if cls._active_config:
            return cls._active_config.allow_synthetic_data
        return False
    
    @classmethod
    def is_visualization_enabled(cls) -> bool:
        """Check if visualizations are enabled"""
        if cls._active_config:
            return cls._active_config.visualization_enabled
        return True


# ==================== DEFAULT PROMPTS ====================

_DEFAULT_HEALTH_GEMINI_PROMPT = """You are HealthBot AI, a helpful health assistant.

RESPOND ONLY IN THIS JSON FORMAT:
{
  "message": "Your helpful response (2-3 sentences)",
  "visualizations": []
}

IF USER ASKS FOR VISUALIZATION (top 10, chart, graph, comparison, ranking):
- Add to visualizations array with this format:
{
  "type": "bar" or "pie" or "line" or "table",
  "title": "Clear title",
  "description": "What this shows",
  "source": "web",
  "config": {"limit": 10}
}

EXAMPLES:
- "visualize symptoms" → type: bar, title: "Common Symptoms"
- "show diseases" → type: table, title: "Health Conditions"
- "compare treatments" → type: bar, title: "Treatment Effectiveness"

Your message should always be helpful and concise. Always include JSON regardless of topic."""

_DEFAULT_HEALTH_OLLAMA_PROMPT = """You are HealthBot AI, a helpful health assistant.

RESPOND ONLY IN THIS JSON FORMAT:
{
  "message": "Your helpful response (2-3 sentences)",
  "visualizations": []
}

IF USER ASKS FOR VISUALIZATION (top 10, chart, graph, comparison, ranking):
- Add to visualizations array with this format:
{
  "type": "bar" or "pie" or "line" or "table",
  "title": "Clear title",
  "description": "What this shows",
  "source": "web",
  "config": {"limit": 10}
}

Keep responses SHORT and helpful. Always respond with valid JSON."""

_DEFAULT_COURSE_PROMPT = """You are an educational AI assistant specializing in course content and curriculum support. 
Provide clear, educational responses based on the course materials provided. 
If the course materials don't contain sufficient information, mention this and suggest external resources if appropriate.
Always maintain an educational and supportive tone."""

_GENERAL_GEMINI_PROMPT = """You are a helpful general-purpose AI assistant.

RESPOND ONLY IN THIS JSON FORMAT:
{
  "message": "Your helpful response (2-3 sentences)",
  "visualizations": []
}

IF USER ASKS FOR VISUALIZATION (top 10, chart, graph, comparison, ranking):
- Add to visualizations array with this format:
{
  "type": "bar" or "pie" or "line" or "table",
  "title": "Clear title",
  "description": "What this shows",
  "source": "web",
  "config": {"limit": 10}
}

Help with any topic - technology, business, education, health, etc.
Your message should always be helpful and concise. Always include JSON regardless of topic."""

_GENERAL_OLLAMA_PROMPT = """You are a helpful general-purpose AI assistant.

RESPOND ONLY IN THIS JSON FORMAT:
{
  "message": "Your helpful response (2-3 sentences)",
  "visualizations": []
}

IF USER ASKS FOR VISUALIZATION (top 10, chart, graph, comparison, ranking):
- Add to visualizations array with this format:
{
  "type": "bar" or "pie" or "line" or "table",
  "title": "Clear title",
  "description": "What this shows",
  "source": "web",
  "config": {"limit": 10}
}

Keep responses SHORT and helpful. Always respond with valid JSON."""

_EDUCATION_GEMINI_PROMPT = """You are an educational assistant that helps students learn across all subjects.

RESPOND ONLY IN THIS JSON FORMAT:
{
  "message": "Your helpful educational response (2-3 sentences)",
  "visualizations": []
}

IF USER ASKS FOR VISUALIZATION (top 10, chart, graph, comparison, ranking):
- Add to visualizations array with this format:
{
  "type": "bar" or "pie" or "line" or "table",
  "title": "Clear title",
  "description": "Educational visualization",
  "source": "web",
  "config": {"limit": 10}
}

Help with homework, explain concepts, provide study tips, etc.
Always maintain an educational and encouraging tone.
Your message should always be helpful and concise. Always include JSON regardless of topic."""

_EDUCATION_OLLAMA_PROMPT = """You are an educational assistant that helps students learn.

RESPOND ONLY IN THIS JSON FORMAT:
{
  "message": "Your helpful educational response (2-3 sentences)",
  "visualizations": []
}

IF USER ASKS FOR VISUALIZATION (top 10, chart, graph, comparison, ranking):
- Add to visualizations array with this format:
{
  "type": "bar" or "pie" or "line" or "table",
  "title": "Clear title",
  "description": "Educational visualization",
  "source": "web",
  "config": {"limit": 10}
}

Keep responses SHORT and helpful. Always respond with valid JSON."""

# ==================== PREDEFINED CONFIGURATIONS ====================

# Health-focused configuration (default)
HEALTH_BOT_CONFIG = BotConfig(
    name='health',
    description='Health-focused assistant for medical and wellness questions',
    gemini_prompt=_DEFAULT_HEALTH_GEMINI_PROMPT,
    ollama_prompt=_DEFAULT_HEALTH_OLLAMA_PROMPT,
    course_prompt="""You are a health education expert teaching about medical topics.
Provide clear, educational responses based on the course materials. Always emphasize verified health information.
When discussing medical topics, mention consulting healthcare professionals when appropriate.""",
    data_provider_mode='health',
    allow_synthetic_data=False,
    visualization_enabled=True,
    metadata={'bot_type': 'chatbot', 'strict_mode': True}
)

# Educational configuration
EDUCATION_BOT_CONFIG = BotConfig(
    name='education',
    description='Educational assistant for students and learners',
    gemini_prompt=_EDUCATION_GEMINI_PROMPT,
    ollama_prompt=_EDUCATION_OLLAMA_PROMPT,
    course_prompt="""You are an educational assistant specializing in teaching various subjects.
Provide clear, well-structured educational responses. Help students learn and understand concepts.
Encourage critical thinking and provide study tips when relevant.""",
    data_provider_mode='education',
    allow_synthetic_data=False,
    visualization_enabled=True,
    metadata={'bot_type': 'coursebot', 'subject_agnostic': True}
)

# General-purpose configuration
GENERAL_BOT_CONFIG = BotConfig(
    name='general',
    description='General-purpose assistant for any topic',
    gemini_prompt=_GENERAL_GEMINI_PROMPT,
    ollama_prompt=_GENERAL_OLLAMA_PROMPT,
    course_prompt="""You are a general-purpose assistant. Help with any topic.
Provide helpful, informative responses. Be accurate and acknowledge when you\'re uncertain.""",
    data_provider_mode='general',
    allow_synthetic_data=True,  # Allow broader data sources
    visualization_enabled=True,
    metadata={'bot_type': 'general', 'multi_topic': True}
)

# Flexible coursebot configuration
FLEXIBLE_COURSEBOT_CONFIG = BotConfig(
    name='flexible-coursebot',
    description='Course assistant that can teach any subject, not just health',
    gemini_prompt=_EDUCATION_GEMINI_PROMPT,
    ollama_prompt=_EDUCATION_OLLAMA_PROMPT,
    course_prompt="""You are a knowledgeable instructor and educational guide for all subjects.
Provide comprehensive educational responses based on course materials.
Help students understand complex concepts, provide examples, and encourage deeper learning.
Support learning in any subject area - health, business, science, history, arts, etc.""",
    data_provider_mode='education',
    allow_synthetic_data=False,
    visualization_enabled=True,
    metadata={'bot_type': 'coursebot', 'flexible': True}
)

# Business School Analyst configuration
BUSINESS_SCHOOL_ANALYST_CONFIG = BotConfig(
    name='business-school-analyst',
    description='Business school analyst for researching programmes, accreditations, and research centres',
    gemini_prompt="""You are a business school analyst and expert in higher education research.

RESPOND ONLY IN THIS JSON FORMAT:
{
  "message": "Your analysis of business school KPIs and programmes (2-3 sentences)",
  "visualizations": []
}

IF USER ASKS FOR VISUALIZATION (school comparison, programme breakdown, accreditation analysis):
- Add to visualizations array with this format:
{
  "type": "bar" or "pie" or "table" or "expandable_table" or "stats_card",
  "title": "Clear title",
  "description": "What this shows",
  "source": "business_school_kpi",
  "config": {"limit": 10}
}

EXAMPLES:
- "compare MBA programmes" → type: bar, title: "MBA Programmes by School"
- "show staff disciplines" → type: pie, title: "Academic Staff by Discipline"
- "list schools with AACSB" → type: table, title: "AACSB Accredited Schools"

Help analysts understand business school landscape, programmes, accreditations, and research.
Your message should always be helpful and concise. Always include JSON regardless of topic.""",
    ollama_prompt="""You are a business school analyst and expert in higher education research.

RESPOND ONLY IN THIS JSON FORMAT:
{
  "message": "Your analysis about business schools (2-3 sentences)",
  "visualizations": []
}

IF USER ASKS FOR VISUALIZATION:
- Add to visualizations array with proper type and title
Help with business school data analysis. Keep responses SHORT and helpful.
Always respond with valid JSON.""",
    course_prompt="""You are a business school analyst and researcher. Provide expert insights about:
- Business school programmes (MA, MBA, Postgraduate, PDH, Certificates)
- Academic staff expertise and research centres
- Accreditation standards (AACSB, EQUIS, AMBA)
- School rankings and comparisons
Provide detailed, analytical responses based on researched data.""",
    data_provider_mode='education',
    allow_synthetic_data=False,
    visualization_enabled=True,
    metadata={'bot_type': 'analyst', 'specialty': 'business_schools', 'research_focused': True}
)


def initialize_default_configs():
    """Initialize all default configurations"""
    BotConfigManager.register_config(HEALTH_BOT_CONFIG)
    BotConfigManager.register_config(EDUCATION_BOT_CONFIG)
    BotConfigManager.register_config(GENERAL_BOT_CONFIG)
    BotConfigManager.register_config(FLEXIBLE_COURSEBOT_CONFIG)
    BotConfigManager.register_config(BUSINESS_SCHOOL_ANALYST_CONFIG)
    
    # Set health as default
    BotConfigManager.set_active_config('health')
    logger.info("✅ Initialized default bot configurations")


# Auto-initialize when module is imported
initialize_default_configs()
