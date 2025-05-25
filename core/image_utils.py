"""
Core image manipulation utilities for the ETS2/ATS Skin Pack Builder.

This module provides functions for:
- Resizing images using the Pillow library.
- Converting images to DDS (DirectDraw Surface) texture format using the
  external `texconv.exe` tool.
- Creating a standardized mod icon from a source image.
"""
from PIL import Image
import subprocess
from pathlib import Path
import sys # Imported for sys.exit in case of critical errors (though not used directly here now)

def resize_image(src_path: Path, dst_path: Path, resolution: tuple[int, int] = (4096, 4096)) -> None:
    """
    Resizes an image to the specified resolution and saves it to the destination path.

    The image is converted to RGBA format before resizing to ensure compatibility
    and handle transparency if present. LANCZOS resampling is used for high-quality results.

    Args:
        src_path (Path): Path to the source image file.
        dst_path (Path): Path where the resized image will be saved (typically as PNG).
        resolution (tuple[int, int]): Target resolution as a (width, height) tuple.
                                      Defaults to (4096, 4096).
    
    Raises:
        FileNotFoundError: If the source image `src_path` does not exist.
        IOError: If there are issues opening or saving the image.
    """
    try:
        # Open the source image and convert to RGBA
        # RGBA conversion helps maintain consistency, especially with PNGs that might have transparency.
        with Image.open(src_path) as img:
            img = img.convert("RGBA")
            # Resize the image using LANCZOS filter for best quality downscaling/upscaling
            img_resized = img.resize(resolution, Image.Resampling.LANCZOS)
            # Save the resized image to the destination path
            img_resized.save(dst_path)
            print(f"    Resized '{src_path.name}' to {resolution} and saved to '{dst_path}'.")
    except FileNotFoundError:
        print(f"❌ Error: Source image not found at '{src_path}'. Cannot resize.")
        raise # Re-raise the exception to be handled by the caller
    except IOError as e:
        print(f"❌ Error: Could not open or save image. Path: '{src_path}' or '{dst_path}'. Details: {e}")
        raise # Re-raise

def convert_to_dds(texconv_path: str, src: Path, dst_folder: Path, dds_format: str = "DXT5") -> None:
    """
    Converts an image to DDS (DirectDraw Surface) format using the `texconv.exe` command-line tool.

    This function invokes `texconv.exe` as a subprocess. It includes error handling
    for cases where `texconv.exe` is not found or if it returns an error during conversion.

    Args:
        texconv_path (str): Full path to the `texconv.exe` executable.
        src (Path): Path to the source image file (typically a PNG).
        dst_folder (Path): The directory where the converted .DDS file will be saved.
                           `texconv.exe` will use the source image's name for the output DDS file.
        dds_format (str): The DDS compression format to use (e.g., "DXT1", "DXT5", "BC7_UNORM").
                          Defaults to "DXT5".
    
    Raises:
        FileNotFoundError: If `texconv_path` is incorrect or `texconv.exe` is not found.
                           Also if `src` image path is not found.
        subprocess.CalledProcessError: If `texconv.exe` returns a non-zero exit code,
                                       indicating a conversion error.
    """
    if not Path(texconv_path).is_file():
        print(f"❌ Error: texconv executable not found at '{texconv_path}'.")
        print("Please ensure it's installed, the path is correctly set in core/config.py, or texconv.exe is in your system PATH.")
        # Raising FileNotFoundError here to be consistent with the subprocess error for missing texconv
        raise FileNotFoundError(f"texconv.exe not found at specified path: {texconv_path}")

    if not src.is_file():
        print(f"❌ Error: Source image for DDS conversion not found at '{src}'.")
        raise FileNotFoundError(f"Source image {src} not found for DDS conversion.")

    # Arguments for texconv:
    # -f <format>: Specify texture format (e.g., DXT5)
    # -m <n>: Number of mipmaps to generate (1 means no extra mipmaps beyond the base level)
    # -o <path>: Output directory
    # <src>: Source file path
    command = [
        texconv_path,
        "-f", dds_format,
        "-m", "1", # Generate 1 mipmap level (the base image itself)
        "-o", str(dst_folder),
        str(src)
    ]
    
    print(f"    Converting '{src.name}' to DDS format '{dds_format}' in '{dst_folder}'...")
    try:
        # Execute texconv.exe
        process = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"      texconv output: {process.stdout.strip() if process.stdout else 'No output'}")
        print(f"    Successfully converted '{src.name}' to DDS.")
    except FileNotFoundError:
        # This specific block might be redundant if texconv_path is checked above,
        # but kept for robustness in case subprocess.run has other ways to trigger it.
        print(f"❌ Error: texconv executable not found at '{texconv_path}' during subprocess run.")
        print("Please ensure it's installed and the path is correctly set in core/config.py, or that texconv.exe is in your system PATH.")
        raise
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: texconv failed to convert '{src}'.")
        print(f"  Command: {' '.join(command)}")
        print(f"  Return code: {e.returncode}")
        if e.stdout:
            print(f"  Stdout: {e.stdout.strip()}")
        if e.stderr:
            print(f"  Stderr: {e.stderr.strip()}")
        print("  Please check the texconv output above for more details (e.g., unsupported format, file issues).")
        raise # Re-raise the exception to halt execution or be handled by caller

def create_mod_icon(image_path: Path, dst_path: Path) -> None:
    """
    Creates a standardized mod icon from a source image.

    The icon is resized to 276x162 pixels, converted to RGB format (dropping alpha),
    and saved as a JPEG file. This is a common format for mod icons in ETS2/ATS.

    Args:
        image_path (Path): Path to the source image file.
        dst_path (Path): Path where the generated .jpg mod icon will be saved.
    
    Raises:
        FileNotFoundError: If the source `image_path` does not exist.
        IOError: If there are issues opening or saving the image.
    """
    try:
        # Open the source image
        with Image.open(image_path) as img:
            # Convert to RGB (removes alpha channel, necessary for JPEG)
            img_rgb = img.convert("RGB")
            # Resize to standard mod icon dimensions using LANCZOS filter
            img_resized = img_rgb.resize((276, 162), Image.Resampling.LANCZOS)
            # Save as JPEG
            img_resized.save(dst_path, "JPEG")
            print(f"    Mod icon created from '{image_path.name}' and saved to '{dst_path}'.")
    except FileNotFoundError:
        print(f"❌ Error: Source image for mod icon not found at '{image_path}'. Cannot create icon.")
        raise
    except IOError as e:
        print(f"❌ Error: Could not open or save image for mod icon. Path: '{image_path}' or '{dst_path}'. Details: {e}")
        raise
