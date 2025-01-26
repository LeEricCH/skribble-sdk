import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command: str, cwd: str | None = None) -> bool:
    """Run a shell command and return whether it succeeded."""
    try:
        subprocess.run(command, shell=True, check=True, cwd=cwd)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command '{command}': {e}")
        return False

def publish_sdk():
    """Build and publish the Python SDK to PyPI."""
    # Get the absolute path to the py-sdk directory
    script_dir = Path(__file__).resolve().parent
    sdk_dir = script_dir.parent.parent / "sdks" / "python"
    
    if not sdk_dir.exists():
        print(f"Error: SDK directory not found at {sdk_dir}")
        sys.exit(1)

    # Change to the SDK directory
    os.chdir(sdk_dir)
    print(f"Changed directory to {sdk_dir}")

    # Clean previous builds
    print("\nCleaning previous builds...")
    build_dir = sdk_dir / "build"
    dist_dir = sdk_dir / "dist"
    egg_info_dir = next(sdk_dir.glob("*.egg-info"), None)

    if build_dir.exists():
        shutil.rmtree(build_dir)
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    if egg_info_dir:
        shutil.rmtree(egg_info_dir)

    # Build the package
    print("\nBuilding package...")
    if not run_command("python -m build"):
        sys.exit(1)

    # Check the distribution
    print("\nChecking distribution...")
    if not run_command("python -m twine check dist/*"):
        sys.exit(1)

    # Upload to PyPI
    print("\nUploading to PyPI...")
    if not run_command("python -m twine upload dist/*"):
        sys.exit(1)

    print("\nPackage successfully published to PyPI!")

if __name__ == "__main__":
    publish_sdk() 