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
    # 1.0-1.5 (pack_format 1)
    "1.0": 1, "1.1": 1,
    "1.2.1": 1, "1.2.2": 1, "1.2.3": 1, "1.2.4": 1, "1.2.5": 1,
    "1.3.1": 1, "1.3.2": 1,
    "1.4.2": 1, "1.4.4": 1, "1.4.5": 1, "1.4.6": 1, "1.4.7": 1,
    "1.5.1": 1, "1.5.2": 1,
    
    # 1.6-1.8 (pack_format 1)
    "1.6.1": 1, "1.6.2": 1, "1.6.4": 1,
    "1.7.2": 1, "1.7.3": 1, "1.7.4": 1, "1.7.5": 1, "1.7.6": 1, "1.7.7": 1, "1.7.8": 1, "1.7.9": 1, "1.7.10": 1,
    "1.8": 1, "1.8.1": 1, "1.8.2": 1, "1.8.3": 1, "1.8.4": 1, "1.8.5": 1, "1.8.6": 1, "1.8.7": 1, "1.8.8": 1, "1.8.9": 1,
    
    # 1.9-1.10 (pack_format 2)
    "1.9": 2, "1.9.1": 2, "1.9.2": 2, "1.9.3": 2, "1.9.4": 2,
    "1.10": 2, "1.10.1": 2, "1.10.2": 2,
    
    # 1.11-1.12 (pack_format 3)
    "1.11": 3, "1.11.1": 3, "1.11.2": 3,
    "1.12": 3, "1.12.1": 3, "1.12.2": 3,
    
    # 1.13-1.14 (pack_format 4)
    "1.13": 4, "1.13.1": 4, "1.13.2": 4,
    "1.14": 4, "1.14.1": 4, "1.14.2": 4, "1.14.3": 4, "1.14.4": 4,
    
    # 1.15 (pack_format 5)
    "1.15": 5, "1.15.1": 5, "1.15.2": 5,
    
    # 1.16-1.17 (pack_format 6)
    "1.16": 6, "1.16.1": 6, "1.16.2": 6, "1.16.3": 6, "1.16.4": 6, "1.16.5": 6,
    "1.17": 6, "1.17.1": 6,
    
    # 1.18 (pack_format 7)
    "1.18": 7, "1.18.1": 7, "1.18.2": 7,
    
    # 1.19 (pack_format 8)
    "1.19": 8, "1.19.1": 8, "1.19.2": 8, "1.19.3": 8, "1.19.4": 8,
    
    # 1.20 (pack_format 12)
    "1.20": 12, "1.20.1": 12, "1.20.2": 12, "1.20.3": 12, "1.20.4": 12, "1.20.5": 12, "1.20.6": 12,
    
    # 1.21 (pack_format 12 - future versions included for forward compatibility)
    "1.21": 12, "1.21.1": 12, "1.21.2": 12, "1.21.3": 12, "1.21.4": 12, "1.21.5": 12, 
    "1.21.6": 12, "1.21.7": 12, "1.21.8": 12, "1.21.9": 12, "1.21.10": 12, "1.21.11": 12,
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


def group_by_pack_format(
    minecraft_releases: List[MinecraftVersion],
    modrinth_versions: Set[str]
) -> dict:
    """
    Group Minecraft versions by pack_format and identify which groups need uploading.
    
    Args:
        minecraft_releases: All available Minecraft releases
        modrinth_versions: Versions already on Modrinth
    
    Returns:
        Dict with pack_format groups, each containing version info and missing status
    """
    # Group all versions by pack_format
    format_groups = {}
    for release in minecraft_releases:
        pf = release.pack_format
        if pf not in format_groups:
            format_groups[pf] = {
                "pack_format": pf,
                "versions": [],
                "all_versions": [],
                "missing_versions": [],
                "has_missing": False
            }
        
        format_groups[pf]["all_versions"].append(release.version)
        
        # Check if this specific version is missing
        if release.version not in modrinth_versions:
            format_groups[pf]["missing_versions"].append(release.version)
            format_groups[pf]["has_missing"] = True
    
    # For each group, determine version range and representative version
    for pf, group in format_groups.items():
        versions = group["all_versions"]
        
        # Sort versions (simple string sort works for most cases)
        versions.sort()
        
        # Create version range string
        if len(versions) == 1:
            version_range = versions[0]
        else:
            version_range = f"{versions[0]}-{versions[-1]}"
        
        group["version_range"] = version_range
        group["version_number"] = f"pack-format-{pf}"
        group["display_name"] = f"Pack Format {pf} ({version_range})"
    
    return format_groups


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
    
    # Group by pack_format
    format_groups = group_by_pack_format(mc_releases, modrinth_versions)
    
    # Filter to only groups with missing versions
    groups_to_upload = {
        pf: group for pf, group in format_groups.items()
        if group["has_missing"]
    }
    
    if groups_to_upload:
        print(f"[!] Found {len(groups_to_upload)} pack format groups to upload:", file=sys.stderr)
        for pf, group in sorted(groups_to_upload.items(), reverse=True):
            print(f"    - Pack Format {pf}: {len(group['missing_versions'])} missing versions ({group['version_range']})", file=sys.stderr)
    else:
        print(f"[+] All pack formats are up-to-date!", file=sys.stderr)
    
    # Output JSON for workflow
    output = {
        "all_groups": list(format_groups.values()),
        "groups_to_upload": [
            group for group in format_groups.values()
            if group["has_missing"]
        ],
        "modrinth_versions": sorted(list(modrinth_versions)),
    }
    
    print(json.dumps(output))


if __name__ == "__main__":
    main()
