# XYZ: Classic Panorama

Replace your menu background with the original one from before 1.13.

## 🤖 Automated Updates

This resource pack uses **GitHub Actions** to automatically stay up-to-date on Modrinth.

- ✅ **Daily checks** for new Minecraft releases
- ✅ **Auto-uploads** missing versions
- ✅ **Zero manual work** required
- ✅ **Smart pack_format** mapping (compatible with all versions)

### Setup Instructions

**⚠️ Important**: Before using this repository, you must:

1. **Configure GitHub Secrets** in your fork:
   - Go to: `Settings → Secrets and variables → Actions`
   - Add `MODRINTH_API_TOKEN` (from https://modrinth.com/settings/account)
   - Add `MODRINTH_PROJECT_ID` (your Modrinth project slug or UUID)

2. **Add your resource pack files** to `assets/` directory

3. **Start the workflow**: Go to `Actions` tab and trigger "Auto-Update Minecraft Resource Pack"

See [SETUP_CHECKLIST.md](SETUP_CHECKLIST.md) for complete step-by-step guide.

## 📁 Repository Structure

```
.
├── .github/workflows/
│   └── auto-update.yml          GitHub Actions workflow (runs daily)
├── scripts/
│   ├── resolve_versions.py      Fetches Minecraft & Modrinth versions
│   ├── update_pack.py           Updates pack.mcmeta per version
│   └── upload_modrinth.py       Uploads to Modrinth API
├── assets/                      Your resource pack files (textures, etc.)
├── pack.mcmeta                  Minecraft pack metadata (auto-updated)
├── SETUP_CHECKLIST.md           ← START HERE for setup
├── AUTOMATION.md                Complete automation documentation
└── verify_setup.py              Validation script
```

## 🚀 How It Works

1. **Daily Schedule** (3 AM UTC): GitHub Actions triggers automatically
2. **Version Check**: Fetches all Minecraft releases from Mojang
3. **Modrinth Check**: Compares against versions already uploaded
4. **Auto-Upload**: For each missing version:
   - Updates `pack.mcmeta` with correct `pack_format`
   - Zips `assets/` and `pack.mcmeta`
   - Uploads to Modrinth with proper metadata
5. **Reporting**: Logs all actions and errors

## 📚 Documentation

- [SETUP_CHECKLIST.md](SETUP_CHECKLIST.md) - **Start here!** Complete setup guide
- [AUTOMATION.md](AUTOMATION.md) - Full documentation, customization, troubleshooting
- Inline comments in all Python scripts

## ⚙️ Customization

### Change Update Schedule

Edit `.github/workflows/auto-update.yml`:
```yaml
schedule:
  - cron: '0 3 * * *'  # Change timing here (cron format)
```

### Change Pack Description

Edit `.github/workflows/auto-update.yml` in the upload step to customize the base description that gets added to all versions.

### Add Unsupported Minecraft Versions

Edit `scripts/resolve_versions.py` and add entries to `MINECRAFT_VERSION_MAP`:
```python
"1.21": 12,  # Add new versions here
```
