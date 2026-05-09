# Docker Image Downloader

A Python tool for downloading Docker images from registries and exporting them as tar archives for offline use.

## Features

- Download Docker images from any registry (Docker Hub by default)
- Support for multi-architecture images (automatically selects amd64)
- Handle both image names and `docker pull` commands as input
- Export images as tar files compatible with `docker load`
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

### Generate Import Commands

After downloading images, generate docker load commands:
```bash
python generate_import_commands.py
```

This will scan the output directory and display import commands for all `.tar` files.

### Import Images

On the target machine, import the images:
```bash
docker load -i library_ubuntu.tar
```

Or with sudo:
```bash
sudo docker load -i library_ubuntu.tar
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
3. **Layer Download**: Downloads each layer blob sequentially
4. **Image Assembly**: Creates Docker-compatible tar archive with:
   - Layer files (decompressed from gzip)
   - Image configuration
   - Manifest metadata
   - Repository tags
5. **Export**: Saves final tar file to output directory

## Notes

- The tool automatically handles multi-architecture manifests and selects amd64
- Layers are downloaded with progress logging
- Temporary files are cleaned up after export
- SSL verification is disabled by default for self-signed registries

## License

MIT License
