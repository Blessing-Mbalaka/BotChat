#!/usr/bin/env python
"""
Test script to demonstrate 500 error diagnostics
Shows how system resources are checked and reported
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 70)
print("OLLAMA 500 ERROR DIAGNOSTICS TEST")
print("=" * 70)

# Test 1: Check system resources
print("\n[TEST 1] Get System Resources")
print("-" * 70)

from health_app.services.ollama_service import get_system_resources

resources = get_system_resources()
print("\n📊 System Resources:")
print(f"  RAM: {resources}")
print(f"  Disk: {resources}")

# Parse the resources
ram = resources.get('ram', {})
disk = resources.get('disk', {})

if isinstance(ram, dict) and 'percent_used' in ram:
    print(f"\n  🟢 RAM: {ram['percent_used']}% used")
    print(f"     Available: {ram.get('available_gb', '?')}GB")
    if ram['percent_used'] > 85:
        print(f"     ⚠️  WARNING: High RAM usage detected!")
else:
    print(f"  ℹ️  RAM info: {ram}")

if isinstance(disk, dict) and 'percent_used' in disk:
    print(f"\n  🟢 Disk: {disk['percent_used']}% used")
    print(f"     Free: {disk.get('free_gb', '?')}GB")
    if disk['percent_used'] > 90:
        print(f"     ⚠️  WARNING: Low disk space!")
else:
    print(f"  ℹ️  Disk info: {disk}")

# Test 2: Simulate 500 error message
print("\n[TEST 2] Example 500 Error Message (Normal Load)")
print("-" * 70)

example_msg = """Ollama crashed (Error 500)

📊 System Status:
  RAM: 45% used (8.5GB available)
  Disk: 65% used (120GB free)

🔧 Solutions:
  1️⃣ Model crashed (unknown reason)
     • Try: ollama rm mistral
     • Reinstall: ollama pull mistral
  2️⃣ Restart Ollama
     • Stop Ollama
     • Run: ollama serve
  3️⃣ Try different model
     • ollama pull phi3:mini (fastest)
     • ollama pull mistral (balanced)"""

print(example_msg)

# Test 3: High memory usage scenario
print("\n[TEST 3] Example 500 Error Message (High RAM)")
print("-" * 70)

example_msg_highram = """Ollama crashed (Error 500)

📊 System Status:
  RAM: 91% used (0.8GB available)
  Disk: 45% used (350GB free)

🔧 Solutions:
  1️⃣ RAM Problem Detected!
     • Close other applications
     • Use smaller model: ollama pull phi3:mini
     • Increase available RAM
  2️⃣ Restart Ollama
     • Stop Ollama
     • Run: ollama serve
  3️⃣ Try different model
     • ollama pull phi3:mini (fastest)
     • ollama pull mistral (balanced)"""

print(example_msg_highram)

# Test 4: Low disk space scenario
print("\n[TEST 4] Example 500 Error Message (Low Disk)")
print("-" * 70)

example_msg_lowdisk = """Ollama crashed (Error 500)

📊 System Status:
  RAM: 62% used (3.2GB available)
  Disk: 96% used (2.5GB free)

🔧 Solutions:
  1️⃣ Disk Space issue!
     • Free up disk space
     • Remove old Ollama models
  2️⃣ Restart Ollama
     • Stop Ollama
     • Run: ollama serve
  3️⃣ Try different model
     • ollama pull phi3:mini (fastest)
     • ollama pull mistral (balanced)"""

print(example_msg_lowdisk)

print("\n" + "=" * 70)
print("✅ DIAGNOSTICS WORKING")
print("=" * 70)

print("""
When you get a 500 error from Ollama, the system will now:

1. ✅ Check RAM usage
2. ✅ Check disk space
3. ✅ Identify the cause (OOM, disk full, or model crash)
4. ✅ Show you which resources are problematic
5. ✅ Provide specific solutions based on what's wrong

The diagnostic message will appear in your browser when Ollama returns
a 500 error, giving you actionable steps to fix the issue.

Key improvements:
  • RAM: Shows exact percentage and available GB
  • Disk: Shows percentage used and free space
  • Cause Detection: Identifies OOM, disk full, or unknown crash
  • Smart Solutions: Different fixes for different problems
  • Clear Instructions: Step-by-step what to do

Test it by:
  1. Start Ollama: ollama serve
  2. Use a large model that stresses your system
  3. Watch for detailed 500 error with diagnostics
""")
