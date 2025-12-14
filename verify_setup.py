#!/usr/bin/env python3
"""
Quick validation script - verify the automation setup is correct.
Run this to check that all files are in place and secrets are configured.
"""

import json
import os
import sys
from pathlib import Path


def check_file_exists(path: str, description: str) -> bool:
    """Check if a file exists."""
    exists = Path(path).exists()
    status = "✓" if exists else "✗"
    print(f"{status} {description}")
    return exists


def check_directory_exists(path: str, description: str) -> bool:
    """Check if a directory exists."""
    exists = Path(path).is_dir()
    status = "✓" if exists else "✗"
    print(f"{status} {description}")
    return exists


def check_pack_mcmeta() -> bool:
    """Validate pack.mcmeta structure."""
    pack_file = Path("pack.mcmeta")
    
    if not pack_file.exists():
        print("✗ pack.mcmeta validation: File not found")
        return False
    
    try:
        with open(pack_file) as f:
            data = json.load(f)
        
        if "pack" not in data:
            print("✗ pack.mcmeta validation: Missing 'pack' key")
            return False
        
        if "pack_format" not in data["pack"]:
            print("✗ pack.mcmeta validation: Missing 'pack_format'")
            return False
        
        if "description" not in data["pack"]:
            print("✗ pack.mcmeta validation: Missing 'description'")
            return False
        
        print("✓ pack.mcmeta validation: Valid structure")
        return True
    
    except json.JSONDecodeError:
        print("✗ pack.mcmeta validation: Invalid JSON")
        return False


def main():
    """Run all validation checks."""
    print("🔍 XYZ Classic Panorama - Setup Verification")
    print("=" * 50)
    print()
    
    all_ok = True
    
    print("📁 Directory Structure:")
    all_ok &= check_directory_exists("scripts", "  Scripts directory")
    all_ok &= check_directory_exists("assets", "  Assets directory")
    all_ok &= check_directory_exists(".github/workflows", "  Workflow directory")
    print()
    
    print("📄 Files:")
    all_ok &= check_file_exists("pack.mcmeta", "  pack.mcmeta")
    all_ok &= check_file_exists("scripts/resolve_versions.py", "  resolve_versions.py")
    all_ok &= check_file_exists("scripts/update_pack.py", "  update_pack.py")
    all_ok &= check_file_exists("scripts/upload_modrinth.py", "  upload_modrinth.py")
    all_ok &= check_file_exists(".github/workflows/auto-update.yml", "  auto-update.yml")
    print()
    
    print("🔧 Configuration:")
    all_ok &= check_pack_mcmeta()
    print()
    
    print("🔐 GitHub Secrets (required):")
    print("  Note: Cannot check secrets from here, verify in GitHub settings:")
    print("  1. Settings → Secrets and variables → Actions")
    print("  2. Add MODRINTH_API_TOKEN (from account settings)")
    print("  3. Add MODRINTH_PROJECT_ID (your project slug or UUID)")
    print()
    
    print("📝 Next Steps:")
    print("  1. Add your resource pack files to assets/")
    print("  2. Configure GitHub Secrets:")
    print("     - MODRINTH_TOKEN")
    print("     - MODRINTH_PROJECT_ID")
    print("  3. Test workflow: Actions → Auto-Update → Run workflow")
    print("  4. See AUTOMATION.md for detailed instructions")
    print()
    
    if all_ok:
        print("✅ Basic setup verification passed!")
        print("   Complete remaining setup steps in GitHub.")
        return 0
    else:
        print("❌ Some files are missing. Please run setup again.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
