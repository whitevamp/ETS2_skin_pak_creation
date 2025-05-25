"""
Main mod automation script for generating ETS2/ATS paint jobs.

This script:
- Processes images
- Generates DDS textures and TOBJ files
- Creates .sii and .sui definition files for trucks and trailers
- Organizes all mod files into an SCS-compatible structure
- Optionally packages everything into a .scs file

Dependencies:
- Pillow
- texconv (external DDS converter)
"""

import os
import zipfile
#import subprocess
from pathlib import Path
#from PIL import Image
from collections import Counter
import random

# Project-specific modules
from core.tobj_writer import write_tobj
from core.sui_file_creation import create_truck_sui, create_trailer_sui
from core.sii_file_creation import create_truck_sii, create_trailer_sii
from core.trailer_models import trailer_models
from core.truck_models import truck_models
from core.create_ui_mat import create_ui_mat
from core.create_tobj import create_tobj
from core.image_utils import resize_image, convert_to_dds, create_mod_icon
from core.mod_metadata import write_manifest, write_description
from core.pack_scs import pack_to_scs


from core.config import (
    mod_name, input_folder, texconv_path, image_resolution, dds_format,
    generate_zip, output_folder, paintjob_root, def_root,
    ui_folder, mod_icon_path, temp_folder
)

# === INIT ===
# Create required folder structure
for folder in [paintjob_root, def_root, ui_folder, temp_folder]:
    folder.mkdir(parents=True, exist_ok=True)

# Gather source images
images = [f for f in os.listdir(input_folder) if f.lower().endswith((".jpg", ".png"))]

def generate_random_paint_id():
    """
    Generate a unique paint job ID in the format girlXXXX, where X is a digit.
    Ensures random and valid texture names.
    """
    digits = ''.join(str(random.randint(0, 9)) for _ in range(4))
    return f"girl{digits}"

# Generate unique paint IDs
paint_ids = set()
while len(paint_ids) < len(images):
    paint_ids.add(generate_random_paint_id())
paint_ids = list(paint_ids)

# === MAIN PROCESS ===
# Process each image to generate skins for trucks and trailers
for idx, img_file in enumerate(images):
    paint_id = paint_ids[idx]
    paint_id0 = paint_id + "_0"
    input_path = Path(input_folder) / img_file
    resized_path = temp_folder / f"{paint_id}.png"
    #resize_image(input_path, resized_path)
    resize_image(input_path, resized_path, image_resolution)

    # Generate UI texture and related files
    convert_to_dds(texconv_path, resized_path, ui_folder, dds_format)
    ui_dds = ui_folder / f"{paint_id}.DDS"
    final_ui_dds = ui_folder / f"{paint_id}.dds"
    if ui_dds.exists():
        ui_dds.rename(final_ui_dds)
    create_tobj(f"{paint_id}.dds", ui_folder / f"{paint_id}.tobj", "/material/ui/accessory", save_mode="default")
    create_ui_mat(paint_id, ui_folder)

    # === TRUCK PAINT JOBS ===
    for truck in truck_models:
        paint_folder = paintjob_root / f"truck/upgrade/paintjob/{truck}/{paint_id}"
        paint_folder.mkdir(parents=True, exist_ok=True)

        # Convert and rename texture
        convert_to_dds(texconv_path, resized_path, paint_folder, dds_format)
        dds = paint_folder / f"{paint_id}.DDS"
        dds_final = paint_folder / f"{paint_id}_0.dds"
        if dds.exists():
            dds.rename(dds_final)

        # Create TOBJ and DEF files
        create_tobj(f"{paint_id}_0..dds", paint_folder / f"{paint_id}_0.tobj", f"/vehicle/truck/upgrade/paintjob/{truck}/{paint_id}", save_mode="default")
        def_path = def_root / f"vehicle/truck/{truck}/paint_job"
        def_path.mkdir(parents=True, exist_ok=True)
        create_truck_sui(paint_id, def_path / f"{paint_id}_shared.sui", truck)
        create_truck_sii(paint_id, def_path / f"{paint_id}.sii", truck)

        # Create empty include stubs
        for suffix in ["metallic", "mask"]:
            include_path = def_path / f"{paint_id}_{suffix}.sui"
            include_path.write_text("")

    # === TRAILER PAINT JOBS ===
    for trailer in trailer_models:
        paint_folder = paintjob_root / f"trailer_owned/upgrade/paintjob/{trailer}/{paint_id}"
        paint_folder.mkdir(parents=True, exist_ok=True)

        # Convert and rename texture
        convert_to_dds(texconv_path, resized_path, paint_folder, dds_format)
        dds = paint_folder / f"{paint_id}.DDS"
        final_dds = paint_folder / f"{paint_id}_shared.dds"
        if dds.exists():
            dds.rename(final_dds)

        # Create TOBJ and DEF files
        create_tobj(f"{paint_id}_shared.dds", paint_folder / f"{paint_id}_shared.tobj", f"/vehicle/trailer_owned/upgrade/paintjob/{trailer}/{paint_id}", save_mode="default")
        def_path = def_root / f"vehicle/trailer_owned/{trailer}/paint_job"
        def_path.mkdir(parents=True, exist_ok=True)
        create_trailer_sui(paint_id, def_path / f"{paint_id}_shared.sui", trailer)
        create_trailer_sii(paint_id, def_path / f"{paint_id}.sii", trailer)

        # Create empty include stubs
        for trailer_suffix in ["metallic", "mask"]:
            include_path = def_path / f"{paint_id}_{trailer_suffix}.sui"
            include_path.write_text("")

# === MOD ICON ===
# Uses the first image to generate the mod icon if available
if images:
    create_mod_icon(Path(input_folder) / images[0], mod_icon_path)

# === Manifest & Description ===
write_manifest(output_folder, "test")
write_description(output_folder)

# === PACK TO .SCS ARCHIVE ===
if generate_zip:
    scs_file = pack_to_scs(output_folder, mod_name)
    print(f"✅ Packed mod into: {scs_file}")
else:
    print("✅ Mod files prepared (no .scs zip created)")
