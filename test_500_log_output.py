#!/usr/bin/env python
"""
Simulate what the server logs look like when a 500 error occurs
Shows the RAM and disk diagnostics that get printed
"""

import logging
import sys

# Set up logging just like Django does
logging.basicConfig(
    level=logging.ERROR,
    format='%(levelname)s - %(name)s - %(message)s',
    stream=sys.stdout
)

logger = logging.getLogger('health_app.services.ollama_service')

# Simulate getting resources
resources = {
    'ram': {
        'total_gb': 7.7,
        'available_gb': 0.86,
        'percent_used': 88.9
    },
    'disk': {
        'total_gb': 447.08,
        'free_gb': 411.69,
        'percent_used': 7.9
    }
}

print("=" * 70)
print("SIMULATED SERVER LOG OUTPUT - When Ollama 500 Error Occurs")
print("=" * 70)
print()

# Simulate what gets logged
logger.error(f"❌ Ollama 500 Internal Server Error")
logger.error(f"Model: phi3:mini")
logger.error(f"Response: Bad Gateway error from Ollama server")
logger.error(f"System Resources: {resources}")

print()
print("=" * 70)
print("What the above means:")
print("=" * 70)
print()

ram = resources['ram']
disk = resources['disk']

print("RAM Status:")
print(f"  Total: {ram['total_gb']}GB")
print(f"  Used: {ram['percent_used']}%")
print(f"  Available: {ram['available_gb']}GB")
print()

print("Disk Status:")
print(f"  Total: {disk['total_gb']}GB")
print(f"  Used: {disk['percent_used']}%")
print(f"  Free: {disk['free_gb']}GB")
print()

print("Analysis:")
if ram['percent_used'] > 85:
    print(f"  ⚠️  RAM is CRITICALLY LOW! ({ram['percent_used']}% used)")
    print(f"     Only {ram['available_gb']}GB available - this is likely the cause of the 500 error")
    print()
    print("  👉 What to do:")
    print(f"     1. Close unnecessary applications to free RAM")
    print(f"     2. Reduce Ollama model size: ollama pull phi3:mini")
    print(f"     3. Restart Ollama: Stop and run 'ollama serve'")
else:
    print(f"  ✅ RAM looks OK ({ram['percent_used']}% used)")

if disk['percent_used'] > 90:
    print(f"  ⚠️  Disk space is LOW! Only {disk['free_gb']}GB free")
else:
    print(f"  ✅ Disk space is OK ({disk['percent_used']}% used)")

print()
print("=" * 70)
print("Key Points:")
print("=" * 70)
print("✅ When a 500 error occurs, the server console will show:")
print("   1. The error message")
print("   2. The model name")
print("   3. The Ollama response")
print("   4. RAM percentage and available GB")
print("   5. Disk percentage and free space")
print()
print("✅ You can then immediately see if:")
print("   - RAM is the problem (low available GB)")
print("   - Disk is the problem (low free space)")
print("   - Something else crashed the model")
