#!/usr/bin/env python
"""
Test script to check course service dependencies
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test imports
try:
    import PyPDF2
    print("✅ PyPDF2 imported successfully")
except ImportError as e:
    print(f"❌ PyPDF2 import failed: {e}")

try:
    from sentence_transformers import SentenceTransformer
    print("✅ sentence_transformers imported successfully")
except ImportError as e:
    print(f"❌ sentence_transformers import failed: {e}")

try:
    from sklearn.metrics.pairwise import cosine_similarity
    print("✅ scikit-learn imported successfully")
except ImportError as e:
    print(f"❌ scikit-learn import failed: {e}")

try:
    import numpy as np
    print("✅ numpy imported successfully")
except ImportError as e:
    print(f"❌ numpy import failed: {e}")

try:
    import pickle
    print("✅ pickle imported successfully")
except ImportError as e:
    print(f"❌ pickle import failed: {e}")

# Test Django imports
try:
    import django
    print(f"✅ Django {django.get_version()} imported successfully")
except ImportError as e:
    print(f"❌ Django import failed: {e}")

# Test course service import
try:
    from health_app.services.course_service import CourseService
    print("✅ CourseService imported successfully")
    service = CourseService()
    print("✅ CourseService initialized successfully")
except ImportError as e:
    print(f"❌ CourseService import failed: {e}")
except Exception as e:
    print(f"❌ CourseService initialization failed: {e}")

print("\n🔍 Dependency check complete!")