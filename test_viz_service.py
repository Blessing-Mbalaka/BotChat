#!/usr/bin/env python
"""
Direct test of visualization service and LLM response generation
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'health_project.settings')
sys.path.insert(0, 'e:\\Healthcare_Bot')
django.setup()

from health_app.services.visualization_service import VisualizationService
import json

print("Testing VisualizationService...")
print("="*60)

# Test 1: get_context_for_llm
print("\nTest 1: LLM Context Generation")
context = VisualizationService.get_context_for_llm()
print(f"Context length: {len(context)} characters")
print("Sample context:")
print(context[:300] if context else "(No tables available)")

# Test 2: Synthetic data generation
print("\n" + "="*60)
print("Test 2: Synthetic Data Generation")

test_cases = [
    ("Show me common symptoms", "bar"),
    ("Age distribution", "pie"),
    ("Treatment recovery trends", "line"),
]

for context, expected_type in test_cases:
    data = VisualizationService.generate_synthetic_data(expected_type, context, num_items=5)
    if data:
        print(f"\n✓ Generated {expected_type} data for '{context}'")
        print(f"  Columns: {data.get('columns')}")
        print(f"  Rows: {len(data.get('rows'))} rows")
    else:
        print(f"\n✗ Failed to generate {expected_type} data")

# Test 3: Validate chart config
print("\n" + "="*60)
print("Test 3: Chart Configuration Validation")

configs = [
    {
        "type": "bar",
        "title": "Symptoms",
        "data": {"columns": ["Name", "Count"], "rows": [["Fever", 10]]}
    },
    {
        "type": "invalid_type",
        "title": "Bad Chart",
        "data": {}
    },
    {
        "type": "table",
        "title": "Data Table",
        "data": {"columns": ["A", "B"], "rows": []}
    }
]

for i, config in enumerate(configs):
    is_valid = VisualizationService.validate_chart_config(config)
    status = "✓ Valid" if is_valid else "✗ Invalid"
    print(f"{status}: {config.get('type')} - {config.get('title')}")

print("\n" + "="*60)
print("✓ Visualization service tests completed!")
print("="*60)
