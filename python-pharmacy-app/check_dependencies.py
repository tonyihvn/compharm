#!/usr/bin/env python3
"""
Installation verification - Check all required dependencies are installed
"""
import sys
import subprocess

def check_package(package_name, import_name=None):
    """Check if a package is installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✓ {package_name}")
        return True
    except ImportError:
        print(f"✗ {package_name} - NOT INSTALLED")
        return False

def main():
    print("\n" + "="*70)
    print("DEPENDENCY CHECK")
    print("="*70 + "\n")
    
    packages = [
        ("PyQt6", "PyQt6"),
        ("SQLAlchemy", "sqlalchemy"),
        ("requests", "requests"),
        ("python-dotenv", "dotenv"),
        ("json", "json"),
        ("pathlib", "pathlib"),
        ("logging", "logging"),
        ("datetime", "datetime"),
    ]
    
    all_ok = True
    for package, import_name in packages:
        if not check_package(package, import_name):
            all_ok = False
    
    print("\n" + "="*70)
    if all_ok:
        print("✓ ALL DEPENDENCIES INSTALLED")
        print("="*70 + "\n")
        print("Installation verified successfully!")
        print("\nNext steps:")
        print("  1. Configure System Settings (Admin Panel > Settings)")
        print("  2. Set backend credentials")
        print("  3. Run: python main.py")
        return 0
    else:
        print("✗ MISSING DEPENDENCIES")
        print("="*70 + "\n")
        print("Install requirements with:")
        print("  pip install -r requirements.txt")
        print("\nOr install individually:")
        print("  pip install PyQt6")
        print("  pip install sqlalchemy")
        print("  pip install requests")
        return 1

if __name__ == "__main__":
    sys.exit(main())
