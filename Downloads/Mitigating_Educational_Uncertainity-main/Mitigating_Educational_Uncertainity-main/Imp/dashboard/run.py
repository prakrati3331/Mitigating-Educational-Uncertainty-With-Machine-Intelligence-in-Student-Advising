#!/usr/bin/env python3
"""
Dashboard startup script
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required")
        sys.exit(1)

def check_virtual_env():
    """Check if running in virtual environment"""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✓ Running in virtual environment")
        return True
    else:
        print("⚠ Warning: Not running in virtual environment")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)

def check_services():
    """Check if required services are available"""
    print("Checking services...")
    
    # Check if we can import required modules
    required_modules = [
        'Arts_dataset.flask_app',
        'Commerce_dataset.flask_app', 
        'pcb_dataset.flask_app',
        'pcm_dataset.flask_app',
        'Vocational_dataset.flask_app',
        'Career_Mapping.career_service',
        'Interest_and_quizzes.quiz_service',
        'Dropout_risk_factor.imp.dropout_risk_service'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module} - {e}")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\nWarning: Some services are not available: {missing_modules}")
        print("The dashboard will still run but some features may not work.")
    
    return len(missing_modules) == 0

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = Path('.env')
    if not env_file.exists():
        print("Creating .env file...")
        env_content = """# Dashboard Configuration
SECRET_KEY=dashboard-secret-key-change-in-production
DEBUG=True
DASHBOARD_PORT=5007
MAIN_API_URL=http://localhost:5006
LOG_LEVEL=INFO
"""
        env_file.write_text(env_content)
        print("✓ .env file created")
    else:
        print("✓ .env file exists")

def main():
    """Main startup function"""
    print("🚀 Starting AI Education Dashboard...")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Check virtual environment
    in_venv = check_virtual_env()
    
    # Install dependencies
    if not in_venv:
        response = input("Install dependencies? (y/n): ")
        if response.lower() == 'y':
            install_dependencies()
    
    # Create env file
    create_env_file()
    
    # Check services
    services_ok = check_services()
    
    print("\n" + "=" * 50)
    if services_ok:
        print("✓ All checks passed. Starting dashboard...")
    else:
        print("⚠ Some services are missing, but dashboard can still start...")
    
    print("Dashboard will be available at: http://localhost:5007")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Start the dashboard
    try:
        from app import app
        app.run(host='0.0.0.0', port=5007, debug=True)
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped")
    except Exception as e:
        print(f"Error starting dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
