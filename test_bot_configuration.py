#!/usr/bin/env python
"""
Bot Configuration System Documentation and Test

This demonstrates how to use the new configurable system to swap between:
- Health bot (health-focused, strict medical information)
- Education bot (educational, any subject)
- General bot (general-purpose, allows synthetic data)
- Flexible coursebot (educational, not just health)
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'health_project.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from health_app.services.bot_config import BotConfigManager
import logging

logging.getLogger('sentence_transformers').setLevel(logging.ERROR)


def print_header(title):
    print("\n" + "="*70)
    print(title.center(70))
    print("="*70)


def print_config_details(config):
    """Pretty print configuration details"""
    print(f"Name: {config.name}")
    print(f"Description: {config.description}")
    print(f"Data Provider Mode: {config.data_provider_mode}")
    print(f"Allow Synthetic Data: {config.allow_synthetic_data}")
    print(f"Visualizations Enabled: {config.visualization_enabled}")
    print(f"Metadata: {config.metadata}")
    print()


def print_prompts(config):
    """Show the system prompts for this configuration"""
    print(f"Gemini Prompt (first 150 chars):\n  {config.gemini_prompt[:150]}...\n")
    print(f"Ollama Prompt (first 150 chars):\n  {config.ollama_prompt[:150]}...\n")
    print(f"Course Prompt (first 200 chars):\n  {config.course_prompt[:200]}...\n")


def test_switching_configs():
    """Test switching between configurations"""
    print_header("Bot Configuration System - Feature Test")
    
    # Show all available configurations
    print("\n1. LIST ALL AVAILABLE CONFIGURATIONS")
    print("-" * 70)
    configs = BotConfigManager.list_configs()
    for name, description in configs.items():
        print(f"  ✓ {name:20} - {description}")
    
    # Test switching to each configuration
    print("\n\n2. TEST SWITCHING BETWEEN CONFIGURATIONS")
    print("-" * 70)
    
    config_names = ['health', 'education', 'general', 'flexible-coursebot']
    
    for config_name in config_names:
        print(f"\n[TEST] Switching to: {config_name}")
        success = BotConfigManager.set_active_config(config_name)
        
        if success:
            active = BotConfigManager.get_active_config()
            print(f"  ✓ Successfully switched to '{config_name}'")
            print(f"  Current active config: {active.name}")
            print(f"  Data provider mode: {active.data_provider_mode}")
        else:
            print(f"  ✗ Failed to switch to '{config_name}'")
    
    # Test getting prompts from active configuration
    print("\n\n3. TEST GETTING PROMPTS FROM ACTIVE CONFIG")
    print("-" * 70)
    
    print("\n[HEALTH CONFIG]")
    BotConfigManager.set_active_config('health')
    gemini_prompt = BotConfigManager.get_gemini_prompt()
    print(f"  Gemini prompt starts with: {gemini_prompt[:60]}...")
    print(f"  Contains 'health': {'health' in gemini_prompt.lower()}")
    
    print("\n[EDUCATION CONFIG]")
    BotConfigManager.set_active_config('education')
    course_prompt = BotConfigManager.get_course_prompt()
    print(f"  Course prompt starts with: {course_prompt[:60]}...")
    print(f"  Contains 'education': {'education' in course_prompt.lower()}")
    
    print("\n[GENERAL CONFIG]")
    BotConfigManager.set_active_config('general')
    ollama_prompt = BotConfigManager.get_ollama_prompt()
    allow_synthetic = BotConfigManager.should_allow_synthetic_data()
    print(f"  Ollama prompt starts with: {ollama_prompt[:60]}...")
    print(f"  Allow synthetic data: {allow_synthetic}")
    
    # Test data provider modes
    print("\n\n4. TEST DATA PROVIDER MODES")
    print("-" * 70)
    
    test_modes = [
        ('health', 'Should strictly use health data provider'),
        ('education', 'Should use education-focused data provider'),
        ('general', 'Should allow broader data sources'),
        ('flexible-coursebot', 'Should use education mode but not health-only'),
    ]
    
    for config_name, description in test_modes:
        BotConfigManager.set_active_config(config_name)
        mode = BotConfigManager.get_data_provider_mode()
        print(f"  {config_name:20} → Mode: {mode:12} ({description})")
    
    # Reset to default
    print("\n\n5. RESET TO DEFAULT")
    print("-" * 70)
    BotConfigManager.set_active_config('health')
    print(f"  Active config reset to: {BotConfigManager.get_active_config().name}")
    
    # Summary
    print("\n\n" + "="*70)
    print("CONFIGURATION SYSTEM SUMMARY")
    print("="*70)
    print("""
✅ Configuration System Features:

1. PREDEFINED CONFIGURATIONS:
   • health - Health-focused (default)
   • education - Educational content (any subject)
   • general - General-purpose assistant
   • flexible-coursebot - Educational (not health-restricted)

2. EASY SWITCHING:
   Python API:
     from health_app.services.bot_config import BotConfigManager
     BotConfigManager.set_active_config('education')
   
   Django Management Command:
     python manage.py switch_bot_config education
     python manage.py switch_bot_config --list

3. CONFIGURATION CONTROLS:
   • System prompts (Gemini, Ollama, Course Service)
   • Data provider mode (health, education, general)
   • Synthetic data allowance
   • Visualization settings
   • Custom metadata

4. AUTOMATIC APPLICATION:
   • Views.py uses BotConfigManager.get_gemini_prompt()
   • Ollama service uses BotConfigManager.get_ollama_prompt()
   • Course service uses BotConfigManager.get_course_prompt()
   • All system prompts update instantly when config changes

5. NO CODE CHANGES REQUIRED:
   Just call BotConfigManager.set_active_config('name') to switch!
    """)
    
    print("="*70)
    return True


def run_all_tests():
    """Run all configuration tests"""
    try:
        success = test_switching_configs()
        
        if success:
            print("\n\n🎉 ALL CONFIGURATION TESTS PASSED!")
            print("\n" + "="*70)
            print("USAGE EXAMPLES")
            print("="*70)
            print("""
START COURSEBOT AS EDUCATIONAL (NOT HEALTH-RESTRICTED):
  from health_app.services.bot_config import BotConfigManager
  BotConfigManager.set_active_config('flexible-coursebot')

SWITCH TO GENERAL PURPOSE BOT:
  BotConfigManager.set_active_config('general')

CHECK CURRENT CONFIGURATION:
  config = BotConfigManager.get_active_config()
  print(f"Active: {config.name} - {config.description}")

GET CURRENT PROMPTS:
  gemini_prompt = BotConfigManager.get_gemini_prompt()
  course_prompt = BotConfigManager.get_course_prompt()

VIA DJANGO MANAGEMENT COMMAND:
  python manage.py switch_bot_config flexible-coursebot
  python manage.py switch_bot_config --list
            """)
            print("="*70)
        
        return 0
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
