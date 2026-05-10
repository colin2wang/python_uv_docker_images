# Docker Image Downloader

A Python tool for downloading Docker images from registries and exporting them as tar archives for offline use.

[Change History](CHANGE_HISTORY.md) | [Development Guidelines](DEVELOPMENT_GUIDELINES.md)

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
1. library_redis_8.2.6_e2d3c0aeec38.tar (134.78 MB)
2. library_jenkins_2.563_f7e8d9c0b1a2.tar (681.75 MB)
----------------------------------------------------------------------
0. Exit

Enter number to import (0 to exit): 1

Importing: library_redis_8.2.6_e2d3c0aeec38.tar
----------------------------------------------------------------------
Loaded image: redis:8.2.6

✓ Successfully imported: library_redis_8.2.6_e2d3c0aeec38.tar

Delete library_redis_8.2.6_e2d3c0aeec38.tar? (Y/n, default: Y): 
✓ Deleted: library_redis_8.2.6_e2d3c0aeec38.tar
```

#### Option 2: Manual Import

On the target machine, import the images:
```bash
docker load -i library_redis_8.2.6_e2d3c0aeec38.tar
```

Or with sudo:
```bash
sudo docker load -i library_redis_8.2.6_e2d3c0aeec38.tar
```

Verify the import:
```bash
docker images
```

## Project Structure

```
python_uv_docker_images/
├── config.yml                       # Configuration file
├── docker_image_downloader.py       # Main downloader script
├── generate_import_commands.py      # Import command generator
├── import_images.sh                 # Interactive import script (Linux/Mac)
├── utils.py                         # Shared utility functions
├── logger_config.py                 # Logging configuration
├── pyproject.toml                   # Python project metadata
├── uv.lock                          # Dependency lock file
├── README.md                        # Main documentation
├── CHANGE_HISTORY.md                # Change log
├── DEVELOPMENT_GUIDELINES.md        # Development and documentation guidelines
├── images/                          # Output directory for tar files
├── tmp/                             # Temporary extraction directory
└── logs/                            # Log files
```

## How It Works

1. **Authentication**: Obtains access token from Docker registry
2. **Manifest Fetch**: Retrieves image manifest and selects appropriate architecture (amd64 by default)
3. **Digest Check**: Gets the image digest (SHA256 signature) and checks if already downloaded
4. **Layer Download**: Downloads each layer blob sequentially with progress logging (if not cached)
5. **Image Assembly**: Creates Docker-compatible tar archive with:
   - Layer files (decompressed from gzip)
   - Image configuration metadata
   - Manifest information
   - Repository tags
6. **Export**: Saves final tar file with version tag and digest in filename to output directory
7. **Cleanup**: Automatically removes temporary files after export

## Notes

- The tool automatically handles multi-architecture manifests and selects amd64
- **Tar filenames include version tag and digest** for easy identification (e.g., `library_redis_8.2.6_e2d3c0aeec38.tar`)
- **Image digest is used as a unique identifier** - prevents duplicate downloads of the same image
- If an image with the same digest exists, download is skipped automatically
- The import script (`import_images.sh`) auto-detects Docker permissions and uses sudo when necessary
- To avoid sudo prompts, add your user to the docker group: `sudo usermod -aG docker $USER`
- Layers are downloaded with progress logging to both console and log files
- Temporary files are automatically cleaned up after export
- SSL verification is disabled by default for self-signed registries
- Compatible with all Linux distributions and macOS
- All detailed logs are saved to the `logs/` directory with timestamps

## Future Enhancements

The following features are planned or under consideration for future releases:

### Remote Deployment
- **SFTP Transfer**: Automatically upload tar files to remote servers via SFTP
- **SSH Integration**: Execute `docker load` commands on remote servers via SSH
- **Multi-server Support**: Deploy images to multiple target servers simultaneously
- **Connection Profiles**: Save and manage multiple server connection configurations

### Batch Operations
- **Batch Download**: Download multiple images from a list or YAML configuration
- **Bulk Import**: Import all tar files in a directory with a single command
- **Parallel Downloads**: Download multiple images concurrently for faster processing

### Advanced Caching
- **Layer-level Caching**: Reuse layers across different images to save bandwidth
- **Local Registry**: Push downloaded images to a local Docker registry
- **Cache Management**: Tools to view, clean, and manage cached layers

### Image Management
- **Image Inspection**: Display detailed image information (size, layers, created date)
- **Tag Management**: Rename or add additional tags to imported images
- **Image Comparison**: Compare two images to see layer differences
- **Export Formats**: Support for additional export formats (OCI, compressed tar.gz)

### Automation & CI/CD
- **CI/CD Integration**: GitHub Actions or GitLab CI workflows
- **Webhook Support**: Trigger downloads based on external events
- **Schedule Downloads**: Cron-like scheduling for regular image updates
- **API Interface**: REST API for programmatic access

### Monitoring & Reporting
- **Download Statistics**: Track bandwidth usage and download times
- **Progress Dashboard**: Real-time progress visualization
- **Email Notifications**: Alert on download completion or failures
- **Audit Logs**: Comprehensive logging of all operations

### Security Enhancements
- **Image Verification**: Verify image signatures and checksums
- **Vulnerability Scanning**: Integrate with security scanners (Trivy, Clair)
- **Encrypted Storage**: Encrypt tar files for sensitive images
- **Access Control**: Role-based access for multi-user environments

### User Experience
- **GUI Application**: Desktop application with graphical interface
- **Interactive Mode**: Enhanced TUI (Terminal User Interface) with menus
- **Auto-completion**: Shell completion for commands and image names
- **Configuration Wizard**: Interactive setup for first-time users

Feel free to contribute ideas or implementations for any of these features!

## License

MIT License
