import os
import sys
import yaml


def load_config(config_file='config.yml'):
    """Load configuration from YAML file."""
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), config_file)
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file {config_path} not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)


def get_default_docker_config():
    """Return default Docker downloader configuration."""
    return {
        'proxy': {
            'enabled': True,
            'http': 'http://localhost:10808',
            'https': 'http://localhost:10808'
        },
        'registry': {
            'default': 'registry-1.docker.io',
            'auth_url': 'https://auth.docker.io/token',
            'service': 'registry.docker.io'
        },
        'image': {
            'default_repo': 'library',
            'default_tag': 'latest'
        },
        'output': {
            'temp_dir': 'tmp',
            'output_dir': '.',
            'temp_dir_prefix': 'tmp_',
            'tar_extension': '.tar'
        },
        'architecture': {
            'os': 'linux',
            'arch': 'amd64'
        },
        'ssl_verify': False,
        'request_timeout': 300
    }


def setup_proxies(config):
    """Setup proxy configuration if enabled."""
    if config.get('proxy', {}).get('enabled'):
        return {
            "http": config['proxy']['http'],
            "https": config['proxy']['https'],
        }
    return None


def parse_image_name(image_input, config):
    """Parse docker image name or pull command into components."""
    # Handle docker pull command
    if image_input.startswith('docker pull '):
        image_input = image_input[len('docker pull '):].strip()
    
    # Parse image components
    repo = config['image']['default_repo']
    tag = config['image']['default_tag']
    imgparts = image_input.split('/')
    
    # Extract image name and tag/digest
    try:
        img, tag = imgparts[-1].split('@')
    except ValueError:
        try:
            img, tag = imgparts[-1].split(':')
        except ValueError:
            img = imgparts[-1]
    
    # Determine registry and repository
    if len(imgparts) > 1 and ('.' in imgparts[0] or ':' in imgparts[0]):
        registry = imgparts[0]
        repo = '/'.join(imgparts[1:-1])
    else:
        registry = config['registry']['default']
        repo = '/'.join(imgparts[:-1]) if imgparts[:-1] else config['image']['default_repo']
    
    repository = f'{repo}/{img}'
    return registry, repository, img, tag


def format_file_size(size_bytes):
    """Convert bytes to human-readable format."""
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
