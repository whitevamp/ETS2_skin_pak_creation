import os
import zipfile
from pathlib import Path

def pack_to_scs(output_folder: Path, mod_name: str) -> Path:
    """
    Creates a .scs archive from the given output folder.

    Args:
        output_folder (Path): The directory containing all mod files.
        mod_name (str): The name for the resulting SCS file (without extension).

    Returns:
        Path: The path to the created .scs file.
    """
    scs_name = Path(f"{mod_name}.scs")

    with zipfile.ZipFile(scs_name, "w", zipfile.ZIP_DEFLATED) as scs:
        for root, _, files in os.walk(output_folder):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, output_folder)
                scs.write(full_path, rel_path)

    return scs_name
