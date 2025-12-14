#!/usr/bin/env python3
"""
Modrinth Uploader
Zips resource pack and uploads to Modrinth for a specific Minecraft version.
"""

import json
import os
import shutil
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional


def create_zip(
    source_dir: str,
    output_zip: str,
    include_files: list = None
) -> bool:
    """
    Create a zip file with specific contents.
    
    Args:
        source_dir: Root directory of the resource pack
        output_zip: Path for output zip file
        include_files: List of files/directories to include (relative to source_dir)
                      Defaults to ["assets", "pack.mcmeta"]
    
    Returns:
        True if successful, False otherwise
    """
    if include_files is None:
        include_files = ["assets", "pack.mcmeta"]
    
    try:
        source_path = Path(source_dir)
        zip_path = Path(output_zip)
        
        # Verify all files exist
        for item in include_files:
            item_path = source_path / item
            if not item_path.exists():
                print(f"WARNING: {item} not found at {item_path}", file=sys.stderr)
        
        # Create temporary directory for zip contents
        temp_dir = zip_path.parent / f"{zip_path.stem}_temp"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir(parents=True)
        
        # Copy files to temp directory
        for item in include_files:
            src = source_path / item
            dst = temp_dir / item
            
            if src.is_dir():
                shutil.copytree(src, dst, dirs_exist_ok=True)
            elif src.is_file():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
        
        # Create zip from temp directory
        zip_path_without_ext = zip_path.with_suffix('')
        shutil.make_archive(str(zip_path_without_ext), 'zip', temp_dir)
        
        # Cleanup temp directory
        shutil.rmtree(temp_dir)
        
        zip_size = zip_path.stat().st_size
        print(f"[+] Created zip: {output_zip} ({zip_size:,} bytes)", file=sys.stderr)
        return True
    
    except Exception as e:
        print(f"ERROR: Failed to create zip: {e}", file=sys.stderr)
        return False


def upload_to_modrinth(
    zip_path: str,
    project_id: str,
    minecraft_version: str,
    api_token: str,
    version_name: Optional[str] = None,
    changelog: Optional[str] = None
) -> bool:
    """
    Upload resource pack to Modrinth.
    
    Args:
        zip_path: Path to the zip file
        project_id: Modrinth project ID (slug or UUID)
        minecraft_version: Target Minecraft version (e.g., "1.20.1")
        api_token: Modrinth API token
        version_name: Version name (defaults to "Minecraft <version>")
        changelog: Release changelog (optional)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        if version_name is None:
            version_name = f"Minecraft {minecraft_version}"
        
        if changelog is None:
            changelog = f"Auto-updated resource pack for Minecraft {minecraft_version}"
        
        zip_file = Path(zip_path)
        if not zip_file.exists():
            print(f"ERROR: Zip file not found: {zip_path}", file=sys.stderr)
            return False
        
        # Read zip file
        with open(zip_file, 'rb') as f:
            zip_data = f.read()
        
        # Prepare request
        url = f"https://api.modrinth.com/v2/version"
        
        body = {
            "name": version_name,
            "version_number": minecraft_version,
            "changelog": changelog,
            "dependencies": [],
            "game_versions": [minecraft_version],
            "release_channel": "release",
            "loaders": ["minecraft"],
            "featured": False,
            "project_id": project_id,
            "file_parts": ["data"]
        }
        
        # Create multipart request
        boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
        
        body_str = json.dumps(body)
        
        multipart_body = (
            f"--{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"data\"\r\n"
            f"Content-Type: application/json\r\n\r\n"
            f"{body_str}\r\n"
            f"--{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"file\"; filename=\"{zip_file.name}\"\r\n"
            f"Content-Type: application/zip\r\n\r\n"
        ).encode() + zip_data + f"\r\n--{boundary}--\r\n".encode()
        
        request = urllib.request.Request(url, data=multipart_body)
        request.add_header('Authorization', api_token)
        request.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
        request.add_header('User-Agent', 'XYZ-Classic-Panorama-Updater/1.0')
        
        print(f"[*] Uploading to Modrinth ({zip_file.stat().st_size:,} bytes)...", file=sys.stderr)
        
        with urllib.request.urlopen(request, timeout=30) as response:
            response_data = response.read().decode()
            print(f"[+] Upload successful for Minecraft {minecraft_version}", file=sys.stderr)
            print(f"    Response: {response_data[:100]}...", file=sys.stderr)
            return True
    
    except urllib.error.HTTPError as e:
        error_body = ""
        try:
            error_body = e.read().decode()
        except:
            pass
        print(f"ERROR: Modrinth API error ({e.code}): {error_body[:200]}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"ERROR: Upload failed: {e}", file=sys.stderr)
        return False


def main():
    """Main entry point."""
    if len(sys.argv) < 5:
        print(
            "Usage: python3 upload_modrinth.py <project_id> <minecraft_version> <api_token> <pack_dir> [output_zip] [version_name]",
            file=sys.stderr
        )
        sys.exit(1)
    
    project_id = sys.argv[1]
    minecraft_version = sys.argv[2]
    api_token = sys.argv[3]
    pack_dir = sys.argv[4]
    output_zip = sys.argv[5] if len(sys.argv) > 5 else f"XYZ-{minecraft_version}.zip"
    version_name = sys.argv[6] if len(sys.argv) > 6 else f"Minecraft {minecraft_version}"
    
    # Create zip
    if not create_zip(pack_dir, output_zip):
        sys.exit(1)
    
    # Upload to Modrinth
    if not upload_to_modrinth(output_zip, project_id, minecraft_version, api_token, version_name):
        sys.exit(1)
    
    # Cleanup zip
    try:
        os.remove(output_zip)
        print(f"[+] Cleaned up temporary zip file", file=sys.stderr)
    except:
        pass
    
    print("[+] Upload workflow complete", file=sys.stderr)


if __name__ == "__main__":
    main()
