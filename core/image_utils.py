# core/image_utils.py
from PIL import Image
import subprocess
from pathlib import Path

def resize_image(src_path: Path, dst_path: Path, resolution=(4096, 4096)):
    """Resize an image to the given resolution and save it to the destination path."""
    img = Image.open(src_path).convert("RGBA")
    img = img.resize(resolution, Image.LANCZOS)
    img.save(dst_path)

# def convert_to_dds(src: Path, dst_folder: Path, texconv_path: str, dds_format: str):
    # """Convert an image to DDS format using texconv."""
    # subprocess.run([
        # texconv_path, "-f", dds_format, "-m", "1", "-o", str(dst_folder), str(src)
    # ], check=True)
def convert_to_dds(texconv_path: str, src: Path, dst_folder: Path, dds_format: str = "DXT5") -> None:
    """
    Convert an image to DDS format using texconv.

    Args:
        texconv_path (str): Path to the texconv executable.
        src (Path): Path to the input image.
        dst_folder (Path): Folder where the DDS will be saved.
        dds_format (str): Format of the DDS texture (default is DXT5).
    """
    subprocess.run([
        texconv_path, "-f", dds_format, "-m", "1", "-o", str(dst_folder), str(src)
    ], check=True)


def create_mod_icon(image_path: Path, dst_path: Path):
    """Create a JPEG mod icon resized to 276x162."""
    img = Image.open(image_path).convert("RGB")
    img = img.resize((276, 162), Image.LANCZOS)
    img.save(dst_path, "JPEG")
