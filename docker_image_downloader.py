import gzip
import hashlib
import json
import os
import shutil
import sys
import tarfile
import time

import requests
import urllib3
from tqdm import tqdm

from logger_config import setup_logger
from utils import load_config, get_default_docker_config, setup_proxies, parse_image_name, print_import_command, generate_import_command_log

urllib3.disable_warnings()

logger = setup_logger(__name__, level='INFO')

# Load configuration
try:
    config = load_config()
except SystemExit:
    config = get_default_docker_config()

# Setup proxies and SSL
proxies = setup_proxies(config)
ssl_verify = config.get('ssl_verify', False)
request_timeout = config.get('request_timeout', 300)
max_retries = config.get('download', {}).get('max_retries', 3)
retry_delay = config.get('download', {}).get('retry_delay', 5)
show_progress = config.get('download', {}).get('show_progress', True)

def download_with_retry(url, headers, stream=False, max_retries=3, retry_delay=5):
    """Download with retry mechanism for better stability."""
    for attempt in range(max_retries):
        try:
            resp = requests.get(
                url,
                headers=headers,
                stream=stream,
                verify=ssl_verify,
                proxies=proxies,
                timeout=request_timeout
            )
            resp.raise_for_status()
            return resp
        except (requests.exceptions.ChunkedEncodingError, 
                requests.exceptions.ConnectionError,
                urllib3.exceptions.ProtocolError,
                urllib3.exceptions.IncompleteRead) as e:
            if attempt < max_retries - 1:
                logger.warning(f"Download failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Download failed after {max_retries} attempts: {str(e)}")
                raise

def get_image_input():
    """Get image name from user input."""
    print("\n===== Docker Image Download Tool =====")
    print("Tip: Press Enter to use default value")
    print("Tip: You can paste a docker pull command\n")
    
    while True:
        try:
            default_image = f"{config['image']['default_repo']}/ubuntu:{config['image']['default_tag']}"
            image_input = input(f"Enter image name (default: {default_image}): ").strip()
            
            if not image_input:
                image_input = default_image
            
            # Validate input
            if '/' in image_input or ':' in image_input or '@' in image_input or len(image_input) > 0:
                return image_input
            else:
                logger.warning("Input cannot be empty")
        except (KeyboardInterrupt, EOFError):
            print("\n")
            logger.info("Operation cancelled")
            sys.exit(0)

# Get image information
image_string = get_image_input()

# Parse image name
registry, repository, img, tag = parse_image_name(image_string, config)
repo = repository.split('/')[0] if '/' in repository else repository
logger.info(f"Processing image: {repository}:{tag}")

# Authenticate with registry
auth_url = config['registry']['auth_url']
reg_service = config['registry']['service']
resp = requests.get(f'https://{registry}/v2/', verify=ssl_verify, proxies=proxies, timeout=request_timeout)

if resp.status_code == 401:
    auth_parts = resp.headers['WWW-Authenticate'].split(',')
    auth_url = auth_parts[0].split('"')[1]
    reg_service = auth_parts[1].split('"')[1] if len(auth_parts) > 1 else ''

resp = requests.get(
    f'{auth_url}?service={reg_service}&scope=repository:{repository}:pull',
    verify=ssl_verify,
    proxies=proxies,
    timeout=request_timeout
)
access_token = resp.json()['token']
auth_head = {
    'Authorization': f'Bearer {access_token}',
    'Accept': 'application/vnd.docker.distribution.manifest.v2+json'
}

# Fetch manifest and select amd64 architecture
manifest_url = f'https://{registry}/v2/{repository}/manifests/{tag}'
resp = requests.get(
    manifest_url,
    headers=auth_head,
    verify=ssl_verify,
    proxies=proxies,
    timeout=request_timeout
)

# Get the digest from response header (this is the image signature)
image_digest = resp.headers.get('Docker-Content-Digest', '')
if not image_digest:
    # Fallback: calculate from content
    image_digest = 'sha256:' + hashlib.sha256(resp.content).hexdigest()

logger.info(f"Image digest: {image_digest}")

# Handle multi-arch manifest list
if resp.status_code == 200 and 'manifests' in resp.json():
    logger.info("Selecting amd64 architecture...")
    for m in resp.json()['manifests']:
        if m['platform']['os'] == config['architecture']['os'] and m['platform']['architecture'] == config['architecture']['arch']:
            digest = m['digest']
            resp = requests.get(
                f'https://{registry}/v2/{repository}/manifests/{digest}',
                headers=auth_head,
                verify=ssl_verify,
                proxies=proxies,
                timeout=request_timeout
            )
            # Update digest for specific architecture
            image_digest = resp.headers.get('Docker-Content-Digest', digest)
            logger.info(f"Architecture-specific digest: {image_digest}")
            break

if resp.status_code != 200:
    logger.error(f"Failed to get manifest: {resp.status_code}")
    logger.error(resp.text)
    sys.exit(1)

layers = resp.json()['layers']

# Create output directory first
output_dir = config['output']['output_dir']
os.makedirs(output_dir, exist_ok=True)

# Generate tar filename with digest and tag for uniqueness
# Use # as separator to preserve repository path information
digest_short = image_digest.replace('sha256:', '')[:12]
tar_filename = f'{repository.replace("/", "#")}_{tag}_{digest_short}{config["output"]["tar_extension"]}'
docker_tar = os.path.join(output_dir, tar_filename)

# Check if already exists
if os.path.exists(docker_tar):
    logger.info(f"Image already exists: {docker_tar}")
    logger.info(f"Skipping download (digest: {image_digest})")
    # Log the import command info
    logger.info(f"Docker Import Command - File: {tar_filename}, Digest: {image_digest}")
    logger.info(f"Command: docker load -i {tar_filename}")
    print_import_command(tar_filename, output_dir, image_digest)
    sys.exit(0)

# Create temp directory
temp_dir = config['output']['temp_dir']
imgdir = os.path.join(temp_dir, f'{config["output"]["temp_dir_prefix"]}{img}_{tag.replace(":", "@")}')
os.makedirs(imgdir, exist_ok=True)
logger.info(f'Created temp directory: {imgdir}')

# Download image config
image_config_digest = resp.json()['config']['digest']
confresp = requests.get(
    f'https://{registry}/v2/{repository}/blobs/{image_config_digest}',
    headers=auth_head,
    verify=ssl_verify,
    proxies=proxies,
    timeout=request_timeout
)

with open(f'{imgdir}/{image_config_digest[7:]}.json', 'wb') as f:
    f.write(confresp.content)

content = [{
    'Config': f'{image_config_digest[7:]}.json',
    'RepoTags': [f'{repository}:{tag}'],
    'Layers': []
}]

empty_json = '{"created":"1970-01-01T00:00:00Z","container_config":{"Hostname":"","Domainname":"","User":"","AttachStdin":false,"AttachStdout":false,"AttachStderr":false,"Tty":false,"OpenStdin":false,"StdinOnce":false,"Env":null,"Cmd":null,"Image":"","Volumes":null,"WorkingDir":"","Entrypoint":null,"OnBuild":null,"Labels":null}}'

parentid = ''

# Check for existing layers in temp directory (resume support)
existing_layers = []
for layer_dir_name in os.listdir(imgdir):
    layer_path = os.path.join(imgdir, layer_dir_name)
    if os.path.isdir(layer_path) and os.path.exists(os.path.join(layer_path, 'layer.tar')):
        existing_layers.append(layer_dir_name)
        logger.info(f'Found existing layer: {layer_dir_name[:12]}...')

if existing_layers:
    logger.info(f'Resuming download: found {len(existing_layers)} existing layers')

total_layers = len(layers)
downloaded_count = 0
skipped_count = 0

for idx, layer in enumerate(layers, 1):
    ublob = layer['digest']
    fake_layerid = hashlib.sha256((parentid + '\n' + ublob + '\n').encode('utf-8')).hexdigest()
    layerdir = os.path.join(imgdir, fake_layerid)
    
    # Check if this layer already exists
    if os.path.exists(os.path.join(layerdir, 'layer.tar')):
        logger.info(f'Skipping existing layer {idx}/{total_layers}: {ublob[7:19]}')
        skipped_count += 1
        content[0]['Layers'].append(f'{fake_layerid}/layer.tar')
        parentid = fake_layerid
        continue
    
    os.makedirs(layerdir)

    with open(os.path.join(layerdir, 'VERSION'), 'w') as f:
        f.write('1.0')

    logger.info(f'Downloading layer {idx}/{total_layers}: {ublob[7:19]}')
    bresp = download_with_retry(
        f'https://{registry}/v2/{repository}/blobs/{ublob}',
        auth_head,
        stream=True,
        max_retries=max_retries,
        retry_delay=retry_delay
    )

    # Get content length for progress bar
    total_size = int(bresp.headers.get('content-length', 0))
    
    gz_path = os.path.join(layerdir, 'layer_gzip.tar')
    with open(gz_path, 'wb') as f:
        if show_progress:
            with tqdm(total=total_size, unit='B', unit_scale=True, desc=f'Layer {idx}/{total_layers}') as pbar:
                for chunk in bresp.iter_content(8192):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))
        else:
            for chunk in bresp.iter_content(8192):
                if chunk:
                    f.write(chunk)

    with gzip.open(gz_path, 'rb') as gz:
        with open(os.path.join(layerdir, 'layer.tar'), 'wb') as f:
            f.write(gz.read())
    os.remove(gz_path)

    content[0]['Layers'].append(f'{fake_layerid}/layer.tar')
    downloaded_count += 1

    with open(os.path.join(layerdir, 'json'), 'w') as f:
        json_obj = json.loads(empty_json)
        json_obj['id'] = fake_layerid
        if parentid:
            json_obj['parent'] = parentid
        parentid = fake_layerid
        f.write(json.dumps(json_obj))

logger.info(f'Download summary: {downloaded_count} new layers, {skipped_count} skipped (already existed)')

with open(os.path.join(imgdir, 'manifest.json'), 'w') as f:
    json.dump(content, f)

with open(os.path.join(imgdir, 'repositories'), 'w') as f:
    json.dump({repository: {tag: fake_layerid}}, f)

# Create tar file
try:
    docker_tar = os.path.join(output_dir, tar_filename)
    logger.info(f'Creating tar archive: {docker_tar}')
    with tarfile.open(docker_tar, 'w') as tar:
        tar.add(imgdir, arcname=os.path.sep)
    
    # Only remove temp directory after successful tar creation
    shutil.rmtree(imgdir)
    logger.info(f'Export completed: {docker_tar}')
    logger.info(f'Image digest: {image_digest}')
    
    # Print import command and log key info
    logger.info(f"Docker Import Command - File: {tar_filename}, Digest: {image_digest}")
    logger.info(f"Command: docker load -i {tar_filename}")
    print_import_command(tar_filename, output_dir, image_digest)
except Exception as e:
    logger.error(f'Failed to create tar archive: {str(e)}')
    logger.info(f'Temp directory preserved for recovery: {imgdir}')
    logger.info('You can re-run the script to resume from existing layers')
    sys.exit(1)