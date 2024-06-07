import subprocess
import re
import shutil
import sys

def extract_dmg(download_path, extract_path):
    # Mount the DMG file and capture the output
    output = subprocess.check_output(['hdiutil', 'attach', '-nobrowse', '-readonly', download_path]).decode('utf-8')
    print(output)

    # Extract the mounted volume name from the output
    mounted_volume_name = re.search(r'/Volumes/(.+)', output).group(1)
    print(mounted_volume_name)

    # Use the mounted volume name to copy files
    shutil.copytree(f'/Volumes/{mounted_volume_name}/', extract_path)

    # Detach the volume
    subprocess.run(['hdiutil', 'detach', f'/Volumes/{mounted_volume_name}'])

# Usage

download_path = sys.argv[1]
extract_path = sys.argv[2]

extract_dmg(download_path, extract_path)

