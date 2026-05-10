# Change History

## 2026-05-10

- Added version tag to tar filename for better image identification (e.g., `library_ubuntu_22.04_a1b2c3d4e5f6.tar`)
- Created DEVELOPMENT_GUIDELINES.md with comprehensive code and documentation standards
- Enhanced README.md with corrected information and Future Enhancements section
- Added Chinese documentation (README_zh.md) with full translation
- Improved documentation accuracy and completeness

## 2026-05-09

- Added interactive import script (`import_images.sh`) with auto-cleanup
- Implemented digest-based caching to skip duplicate downloads
- Refactored code into modular structure (`utils.py`)
- Removed AI-generated verbose comments
- Fixed variable errors and improved logging

## Initial Release

- Docker image downloader with multi-arch support
- Export images as tar files for offline use
- Configurable proxy and registry settings
- Logging system and YAML configuration
