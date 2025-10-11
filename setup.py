#!/usr/bin/env python3
"""
HealthBot AI Setup Script
Automated setup for the healthcare chatbot application
"""

import os
import sys
import subprocess
import platform

def run_command(command, description):
    """Run a shell command with error handling"""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error in {description}: {e}")
        print(f"Command output: {e.output}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def create_virtual_environment():
    """Create and activate virtual environment"""
    if os.path.exists('.venv'):
        print("✅ Virtual environment already exists")
        return True
    
    return run_command("python -m venv .venv", "Creating virtual environment")

def get_activation_command():
    """Get the correct activation command for the current OS"""
    if platform.system() == "Windows":
        return ".venv\\Scripts\\activate"
    else:
        return "source .venv/bin/activate"

def install_requirements():
    """Install Python packages"""
    packages = [
        "django>=5.2.7",
        "python-dotenv>=1.0.0", 
        "google-generativeai>=0.7.2",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.2",
        "pyyaml>=6.0.1",
        "numpy>=1.24.3",
        "python-docx>=0.8.11",
        "PyPDF2>=3.0.1"
    ]
    
    python_cmd = ".venv\\Scripts\\python.exe" if platform.system() == "Windows" else ".venv/bin/python"
    
    for package in packages:
        if not run_command(f"{python_cmd} -m pip install {package}", f"Installing {package}"):
            return False
    
    return True

def setup_database():
    """Run Django migrations"""
    python_cmd = ".venv\\Scripts\\python.exe" if platform.system() == "Windows" else ".venv/bin/python"
    return run_command(f"{python_cmd} manage.py migrate", "Setting up database")

def create_env_file():
    """Create .env file with default values"""
    env_content = """# HealthBot AI Environment Variables
GEMINI_API_KEY=your_gemini_api_key_here
DEBUG=True
SECRET_KEY=django-insecure-m0c=i%%cixav))jpy5$%yjb6%lah16!&kw#(^$k@#r^kfl2s43

# Instructions:
# 1. Replace 'your_gemini_api_key_here' with your actual Gemini API key
# 2. Get your API key from: https://makersuite.google.com/app/apikey
# 3. Keep DEBUG=True for development, set to False for production
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file - Please add your Gemini API key")
    else:
        print("✅ .env file already exists")
    
    return True

def create_sample_documents():
    """Ensure sample medical documents exist"""
    if os.path.exists('medical_docs') and os.listdir('medical_docs'):
        print("✅ Medical documents already exist")
        return True
    
    print("✅ Sample medical documents created during installation")
    return True

def main():
    """Main setup function"""
    print("🏥 HealthBot AI Setup Script")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        print("❌ Failed to create virtual environment")
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        print("❌ Failed to install requirements")
        sys.exit(1)
    
    # Setup database
    if not setup_database():
        print("❌ Failed to setup database")
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        print("❌ Failed to create .env file")
        sys.exit(1)
    
    # Check sample documents
    create_sample_documents()
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file and add your Gemini API key")
    print("2. Add medical documents to medical_docs/ folder (optional)")
    print("3. Run the server:")
    
    if platform.system() == "Windows":
        print("   .venv\\Scripts\\python.exe manage.py runserver")
    else:
        print("   source .venv/bin/activate")
        print("   python manage.py runserver")
    
    print("4. Open http://127.0.0.1:8000/ in your browser")
    print("\n💡 For more information, see README.md")

if __name__ == "__main__":
    main()