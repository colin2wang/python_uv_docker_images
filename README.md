# Docker Image Downloader

A Python tool for downloading Docker images from registries and exporting them as tar archives for offline use.

[Change History](CHANGE_HISTORY.md)

## Features

- Download Docker images from any registry (Docker Hub by default)
- Support for multi-architecture images (automatically selects amd64)
- Handle both image names and `docker pull` commands as input
- Export images as tar files compatible with `docker load`
- **Smart caching**: Uses image digest to skip already downloaded images
- **Interactive import**: Bash script for easy image import with auto-cleanup
- Configurable proxy support
- Customizable output directory

## Requirements

- Python 3.7+
- Dependencies managed by [uv](https://github.com/astral-sh/uv)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd python_uv_docker_images
```

2. Install dependencies using uv:
```bash
uv sync
```

Or install manually:
```bash
pip install requests pyyaml urllib3
```

## Configuration

Edit `config.yml` to customize settings:

```yaml
# Proxy settings
proxy:
  enabled: true
  http: "http://localhost:10808"
  https: "http://localhost:10808"

# Docker Registry
registry:
  default: "registry-1.docker.io"
  auth_url: "https://auth.docker.io/token"
  service: "registry.docker.io"

# Output settings
output:
  temp_dir: "tmp"
  output_dir: "images"
  tar_extension: ".tar"

# Architecture selection
architecture:
  os: "linux"
  arch: "amd64"

# SSL verification
ssl_verify: false

# Request timeout (seconds)
request_timeout: 300
```

## Usage

### Download Docker Images

Run the downloader:
```bash
python docker_image_downloader.py
```

You'll be prompted to enter an image name. You can use:
- Simple image name: `ubuntu:latest`
- Full image path: `library/ubuntu:22.04`
- Docker pull command: `docker pull jenkins/jenkins:2.563`
- Custom registry: `myregistry.com/myimage:v1.0`

The downloaded tar file will be saved to the configured output directory.

**Smart Caching**: The tool uses Docker image digests (SHA256 signatures) to identify unique images. If an image with the same digest already exists, it will skip the download and immediately show the import command.

### Generate Import Commands

After downloading images, generate docker load commands:
```bash
python generate_import_commands.py
```

This will scan the output directory and display import commands for all `.tar` files.

### Import Images

#### Option 1: Using the Interactive Script (Recommended)

The interactive script provides a user-friendly way to import multiple images:

```bash
# Make executable (first time only)
chmod +x import_images.sh

# Run the script
./import_images.sh
```

**Features:**
- Automatically scans current directory for `.tar` files
- Displays numbered menu with file sizes
- Select images by number to import
- Auto-detects Docker permissions (uses sudo if needed)
- Prompts to delete tar file after successful import (default: Yes)
- Refreshes file list after each operation
- Continues until all images imported or user exits

**Example:**
```
======================================================================
  Docker Image Import Tool
======================================================================

Found 2 Docker image archive(s):
----------------------------------------------------------------------
1. library_redis_e2d3c0aeec38.tar (134.78 MB)
2. library_jenkins_f7e8d9c0b1a2.tar (681.75 MB)
----------------------------------------------------------------------
0. Exit

Enter number to import (0 to exit): 1

Importing: library_redis_e2d3c0aeec38.tar
----------------------------------------------------------------------
Loaded image: redis:8.2.6

✓ Successfully imported: library_redis_e2d3c0aeec38.tar

Delete library_redis_e2d3c0aeec38.tar? (Y/n, default: Y): 
✓ Deleted: library_redis_e2d3c0aeec38.tar
```

#### Option 2: Manual Import

On the target machine, import the images:
```bash
docker load -i library_redis_e2d3c0aeec38.tar
```

Or with sudo:
```bash
sudo docker load -i library_redis_e2d3c0aeec38.tar
```

Verify the import:
```bash
docker images
```

## Project Structure

```
python_uv_docker_images/
├── config.yml                    # Configuration file
├── docker_image_downloader.py    # Main downloader script
├── generate_import_commands.py   # Import command generator
├── import_images.sh              # Interactive import script (Linux/Mac)
├── utils.py                      # Shared utility functions
├── logger_config.py              # Logging configuration
├── pyproject.toml                # Python project metadata
├── uv.lock                       # Dependency lock file
├── images/                       # Output directory for tar files
├── tmp/                          # Temporary extraction directory
└── logs/                         # Log files
```

## How It Works

1. **Authentication**: Obtains access token from Docker registry
2. **Manifest Fetch**: Retrieves image manifest and selects appropriate architecture
3. **Digest Check**: Gets the image digest (SHA256 signature) and checks if already downloaded
4. **Layer Download**: Downloads each layer blob sequentially (if not cached)
5. **Image Assembly**: Creates Docker-compatible tar archive with:
   - Layer files (decompressed from gzip)
   - Image configuration
   - Manifest metadata
   - Repository tags
6. **Export**: Saves final tar file with digest in filename to output directory

## Notes

- The tool automatically handles multi-architecture manifests and selects amd64
- **Image digest is used as a unique identifier** - tar files include the first 12 characters of the digest (e.g., `library_redis_e2d3c0aeec38.tar`)
- If an image with the same digest exists, download is skipped automatically
- The import script (`import_images.sh`) auto-detects Docker permissions and uses sudo when necessary
- To avoid sudo prompts, add your user to the docker group: `sudo usermod -aG docker $USER`
- Layers are downloaded with progress logging
- Temporary files are cleaned up after export
- SSL verification is disabled by default for self-signed registries
- Compatible with all Linux distributions and macOS

## License

MIT License
