"""
AQI Predictor - Setup Verification Script
Run this to check if everything is configured correctly
"""

import os
import sys

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_section(text):
    """Print a section header"""
    print(f"\n[{text}]")
    print("-" * 60)

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (Need 3.8+)")
        return False

def check_file(filepath, required=True):
    """Check if a file exists"""
    exists = os.path.exists(filepath)
    status = "✅" if exists else "❌"
    req_status = " (REQUIRED)" if required and not exists else ""
    print(f"{status} {filepath}{req_status}")
    return exists

def check_package(package_name):
    """Check if a package is installed"""
    try:
        __import__(package_name)
        print(f"✅ {package_name}")
        return True
    except ImportError:
        print(f"❌ {package_name} - Run: pip install {package_name}")
        return False

def check_model_loading():
    """Try to load the model and scaler"""
    try:
        import joblib
        
        if not os.path.exists('best_aqi_model.pkl'):
            print("❌ Model file not found")
            return False
            
        if not os.path.exists('scaler.pkl'):
            print("❌ Scaler file not found")
            return False
        
        model = joblib.load('best_aqi_model.pkl')
        scaler = joblib.load('scaler.pkl')
        print("✅ Model and scaler loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Error loading model/scaler: {e}")
        return False

def check_api_token():
    """Check if API token is configured"""
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'YOUR_TOKEN_HERE' in content or 'demo' in content.lower():
                print("⚠️  API token not configured (using default)")
                print("   Get your token from: https://aqicn.org/data-platform/token/")
                print("   Update WAQI_TOKEN in app.py")
                return False
            else:
                print("✅ API token configured")
                return True
    except Exception as e:
        print(f"❌ Error checking API token: {e}")
        return False

def main():
    """Main test function"""
    print_header("AQI Predictor - Setup Verification")
    
    results = {}
    
    # Check Python version
    print_section("1. Python Version")
    results['python'] = check_python_version()
    
    # Check directory structure
    print_section("2. Directory Structure")
    dirs_ok = all([
        check_file('templates', required=True),
        check_file('static', required=True),
        check_file('static/css', required=True),
    ])
    results['directories'] = dirs_ok
    
    # Check required files
    print_section("3. Required Files")
    files_ok = all([
        check_file('app.py', required=True),
        check_file('requirements.txt', required=True),
        check_file('templates/index.html', required=True),
        check_file('static/css/style.css', required=True),
        check_file('best_aqi_model.pkl', required=True),
        check_file('scaler.pkl', required=True),
    ])
    results['files'] = files_ok
    
    # Check optional files
    print_section("4. Optional Files")
    check_file('city_day.csv', required=False)
    check_file('train_model.py', required=False)
    
    # Check Python packages
    print_section("5. Python Packages")
    packages = ['flask', 'requests', 'numpy', 'pandas', 'sklearn', 'xgboost', 'joblib']
    packages_ok = all(check_package(pkg) for pkg in packages)
    results['packages'] = packages_ok
    
    # Check model loading
    print_section("6. Model Loading Test")
    results['model'] = check_model_loading()
    
    # Check API configuration
    print_section("7. API Configuration")
    results['api'] = check_api_token()
    
    # Print summary
    print_header("SUMMARY")
    
    all_critical_pass = all([
        results['python'],
        results['directories'],
        results['files'],
        results['packages'],
        results['model']
    ])
    
    if all_critical_pass:
        print("\n✅ ALL CRITICAL CHECKS PASSED!")
        if not results['api']:
            print("\n⚠️  Note: You should configure your WAQI API token for full functionality")
        print("\n" + "=" * 60)
        print("Ready to run! Execute one of these commands:")
        print("  • Windows: run.bat")
        print("  • Command: python app.py")
        print("\nThen visit: http://localhost:5000")
        print("=" * 60)
    else:
        print("\n❌ SOME CHECKS FAILED")
        print("\n" + "=" * 60)
        print("Please fix the issues above:")
        
        if not results['packages']:
            print("\n📦 To install packages:")
            print("  pip install -r requirements.txt")
            print("  OR run: setup.bat")
        
        if not results['files']:
            print("\n📁 Missing files:")
            print("  Make sure all files are in the correct folders")
            print("  Check the directory structure in README.md")
        
        if not results['model']:
            print("\n🤖 Model files:")
            print("  Ensure best_aqi_model.pkl and scaler.pkl are present")
            print("  You can train a new model with: python train_model.py")
        
        print("\n" + "=" * 60)
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()