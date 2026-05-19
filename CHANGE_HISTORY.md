# Change History

## 2026-05-19

- Modified import_images.sh to move imported images to ./imported directory instead of deleting
- Added exclusion rule to prevent scanning files in ./imported directory
- Enhanced user interaction with clear prompts for file management after import
- Added download progress bar using tqdm library for better user experience
- Implemented resume download functionality to recover from network interruptions
- Added retry mechanism with configurable max retries and delay for failed downloads
- Enhanced error handling to preserve temp directory on failure for recovery
- Added configuration options for download settings (max_retries, retry_delay, show_progress)
- Added resume support configuration (enabled, auto_cleanup)
- Updated dependencies to include tqdm>=4.67.1

## 2026-05-11

- Changed tar filename format to use `#` as separator for repository path (e.g., `serjs#go-socks5-proxy_latest_847fa485f52f.tar`)
- Fixed RepoTags in manifest.json to preserve full repository path (e.g., `serjs/go-socks5-proxy:latest`)
- Enhanced import_images.sh to parse and display repository information from filenames
- Added expected image name display after successful import

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
