#!/usr/bin/env python3
"""
Minecraft Version Resolver
Fetches Minecraft releases and Modrinth versions to identify missing uploads.
"""

import json
import sys
import urllib.request
from typing import Dict, List, Set, Optional
from dataclasses import dataclass


# Minecraft version to pack_format mapping
# Reference: https://minecraft.wiki/w/Pack_format
MINECRAFT_VERSION_MAP: Dict[str, int] = {
    # 1.6-1.8
    "1.6.1": 1, "1.6.2": 1, "1.6.4": 1,
    "1.7.2": 1, "1.7.10": 1,
    "1.8": 1, "1.8.1": 1, "1.8.9": 1,
    
    # 1.9-1.10
    "1.9": 2, "1.9.4": 2,
    "1.10": 2, "1.10.2": 2,
    
    # 1.11-1.12
    "1.11": 3, "1.11.2": 3,
    "1.12": 3, "1.12.1": 3, "1.12.2": 3,
    
    # 1.13-1.14
    "1.13": 4, "1.13.1": 4, "1.13.2": 4,
    "1.14": 4, "1.14.1": 4, "1.14.2": 4, "1.14.3": 4, "1.14.4": 4,
    
    # 1.15
    "1.15": 5, "1.15.1": 5, "1.15.2": 5,
    
    # 1.16-1.17
    "1.16": 6, "1.16.1": 6, "1.16.2": 6, "1.16.3": 6, "1.16.4": 6, "1.16.5": 6,
    "1.17": 6, "1.17.1": 6,
    
    # 1.18-1.19
    "1.18": 7, "1.18.1": 7, "1.18.2": 7,
    "1.19": 8, "1.19.1": 8, "1.19.2": 8, "1.19.3": 8, "1.19.4": 8,
    
    # 1.20+
    "1.20": 12, "1.20.1": 12,
    "1.21": 12, "1.21.1": 12,
}


@dataclass
class MinecraftVersion:
    """Represents a Minecraft release version."""
    version: str
    pack_format: int


def fetch_minecraft_releases() -> List[MinecraftVersion]:
    """
    Fetch all Minecraft Java release versions from official Mojang API.
    
    Returns:
        List of MinecraftVersion objects for release versions only.
    """
    try:
        url = "https://piston-meta.mojang.com/mc/game/version_manifest.json"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
        
        releases = []
        for version_obj in data.get("versions", []):
            if version_obj.get("type") == "release":
                version_str = version_obj.get("id")
                pack_format = MINECRAFT_VERSION_MAP.get(version_str)
                
                if pack_format is not None:
                    releases.append(MinecraftVersion(version_str, pack_format))
                else:
                    print(f"WARNING: Unknown pack_format for version {version_str}", file=sys.stderr)
        
        return releases
    
    except Exception as e:
        print(f"ERROR: Failed to fetch Minecraft releases: {e}", file=sys.stderr)
        sys.exit(1)


def fetch_modrinth_versions(project_id: str) -> Set[str]:
    """
    Fetch all Minecraft versions already uploaded to Modrinth.
    
    Args:
        project_id: Modrinth project ID (slug or UUID)
    
    Returns:
        Set of version strings already on Modrinth
    """
    try:
        url = f"https://api.modrinth.com/v2/project/{project_id}/versions"
        with urllib.request.urlopen(url, timeout=10) as response:
            versions = json.loads(response.read().decode())
        
        modrinth_versions = set()
        for version in versions:
            for game_version in version.get("game_versions", []):
                modrinth_versions.add(game_version)
        
        return modrinth_versions
    
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"WARNING: Project '{project_id}' not found on Modrinth", file=sys.stderr)
            return set()
        print(f"ERROR: Modrinth API error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to fetch Modrinth versions: {e}", file=sys.stderr)
        sys.exit(1)


def find_missing_versions(
    minecraft_releases: List[MinecraftVersion],
    modrinth_versions: Set[str]
) -> List[MinecraftVersion]:
    """
    Identify Minecraft versions not yet uploaded to Modrinth.
    
    Args:
        minecraft_releases: All available Minecraft releases
        modrinth_versions: Versions already on Modrinth
    
    Returns:
        List of versions to upload
    """
    missing = [
        release for release in minecraft_releases
        if release.version not in modrinth_versions
    ]
    
    return missing


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python3 resolve_versions.py <modrinth_project_id>", file=sys.stderr)
        sys.exit(1)
    
    project_id = sys.argv[1]
    
    print(f"[*] Fetching Minecraft releases...", file=sys.stderr)
    mc_releases = fetch_minecraft_releases()
    print(f"[+] Found {len(mc_releases)} Minecraft release versions", file=sys.stderr)
    
    print(f"[*] Fetching Modrinth versions for project '{project_id}'...", file=sys.stderr)
    modrinth_versions = fetch_modrinth_versions(project_id)
    print(f"[+] Found {len(modrinth_versions)} versions on Modrinth", file=sys.stderr)
    
    missing = find_missing_versions(mc_releases, modrinth_versions)
    
    if missing:
        print(f"[!] Found {len(missing)} missing versions:", file=sys.stderr)
        for version in missing:
            print(f"    - {version.version} (pack_format: {version.pack_format})", file=sys.stderr)
    else:
        print(f"[+] All versions are up-to-date!", file=sys.stderr)
    
    # Output JSON for workflow
    output = {
        "all_releases": [
            {"version": v.version, "pack_format": v.pack_format}
            for v in mc_releases
        ],
        "modrinth_versions": sorted(list(modrinth_versions)),
        "missing_versions": [
            {"version": v.version, "pack_format": v.pack_format}
            for v in missing
        ]
    }
    
    print(json.dumps(output))


if __name__ == "__main__":
    main()
