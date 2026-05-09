import os
import sys
from utils import load_config, format_file_size


def generate_docker_import_commands():
    """Generate Docker import commands for .tar files."""
    config = load_config()
    output_dir = config.get('output', {}).get('output_dir', '.')
    
    # Convert to absolute path
    if not os.path.isabs(output_dir):
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), output_dir)
    
    print("=" * 70)
    print("Docker Image Import Commands")
    print("=" * 70)
    print(f"\nScanning: {output_dir}\n")
    
    if not os.path.exists(output_dir):
        print(f"Error: Directory '{output_dir}' not found")
        sys.exit(1)
    
    tar_files = sorted([f for f in os.listdir(output_dir) if f.endswith('.tar')])
    
    if not tar_files:
        print("No .tar files found")
        return
    
    print(f"Found {len(tar_files)} image(s):\n")
    print("-" * 70)
    
    for i, tar_file in enumerate(tar_files, 1):
        full_path = os.path.join(output_dir, tar_file)
        size_str = format_file_size(os.path.getsize(full_path))
        
        print(f"{i}. {tar_file} ({size_str})")
        print(f"   docker load -i {tar_file}")
        print(f"   sudo docker load -i {tar_file}\n")
    
    print("=" * 70)
    print("Tip: Run from the directory containing .tar files")
    print("Tip: Use 'docker images' to verify after import")
    print("=" * 70)


if __name__ == "__main__":
    generate_docker_import_commands()
