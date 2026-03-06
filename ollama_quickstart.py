#!/usr/bin/env python
"""
QUICK START: Ollama Offline Mode

This script helps you set up and test Ollama in 2 minutes.
"""

import subprocess
import platform
import sys
import requests


def check_ollama():
    """Check if Ollama is installed and running"""
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=2)
        return response.status_code == 200
    except:
        return False


def main():
    os_name = platform.system()
    
    print("""
╔════════════════════════════════════════════════════════════════╗
║         OLLAMA OFFLINE MODE - QUICK START (2 MIN)              ║
╚════════════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: Check existing installation
    if check_ollama():
        print("✅ Ollama is RUNNING!")
        print("\nYour app will automatically use Ollama when Gemini API quota is exceeded.")
        print("\nYou can now:")
        print("  1. Run: python manage.py runserver")
        print("  2. Ask for visualizations (they'll use Ollama in offline mode)")
        return
    
    print("❌ Ollama is NOT running\n")
    
    # Step 2: Download instructions
    print("📥 STEP 1: Download Ollama")
    print("-" * 60)
    
    if os_name == "Windows":
        print("Windows Users:")
        print("  • Go to: https://ollama.ai/download/windows")
        print("  • Click 'Download'")
        print("  • Run the installer (OllamaSetup.exe)")
        print("  • Click the Ollama icon when done (should appear in system tray)")
    
    elif os_name == "Darwin":  # Mac
        print("Mac Users:")
        print("  • Go to: https://ollama.ai/download/mac")
        print("  • Or run: brew install ollama")
        print("  • Then start: ollama serve")
    
    else:  # Linux
        print("Linux Users:")
        print("  curl https://ollama.ai/install.sh | sh")
        print("  Then start: ollama serve")
    
    # Step 3: Pull a model
    print("\n⬇️  STEP 2: Get a Model (in NEW terminal/PowerShell)")
    print("-" * 60)
    print("  ollama pull mistral")
    print("\n  (Takes 2-5 min depending on internet speed)")
    print("  (Mistral is fast and good quality - recommended!)")
    
    # Step 4: Verify
    print("\n✔️  STEP 3: Verify Setup")
    print("-" * 60)
    print("  Run: python test_ollama.py")
    
    # Step 5: Done
    print("\n🎉 DONE! Your app now has offline AI!")
    print("-" * 60)
    print("\nWhat happens next:")
    print("  1. Gemini API tries first (if quota available)")
    print("  2. Falls back to Ollama (if running locally)")
    print("  3. Falls back to demo mode (realistic synthetic data)")
    
    print("\n📖 Full guide: See OLLAMA_SETUP.md")
    
    # Offer to open download page
    if sys.platform == 'win32':
        try:
            import webbrowser
            response = input("\nOpen ollama.ai in browser? (y/n): ").strip().lower()
            if response == 'y':
                webbrowser.open('https://ollama.ai')
        except:
            pass


if __name__ == '__main__':
    main()
