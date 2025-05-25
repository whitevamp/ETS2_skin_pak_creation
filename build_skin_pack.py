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
import sys
import zipfile
import logging
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
    ui_folder, mod_icon_path, temp_folder, paint_job_prefix,
    mod_version, mod_author, mod_description_content
)

# === LOGGING SETUP ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# === INIT ===
logging.info("Initializing script and creating base folder structure...")
# Create required folder structure
for folder in [paintjob_root, def_root, ui_folder, temp_folder]:
    folder.mkdir(parents=True, exist_ok=True)
    logging.info(f"Ensured output sub-folder exists: {folder}")

# === PRE-FLIGHT CHECKS ===
logging.info("Performing pre-flight checks...")
# Check if input folder exists
input_folder_path = Path(input_folder)
if not input_folder_path.is_dir():
    logging.error(f"Input folder '{input_folder}' not found.")
    logging.error("Please ensure the folder exists and the path is correctly set in core/config.py.")
    sys.exit(1)

# Gather source images
images = [f for f in os.listdir(input_folder) if f.lower().endswith((".jpg", ".png"))]

# Check if images were found
if not images:
    logging.error(f"No images (.jpg or .png) found in input folder '{input_folder}'.")
    logging.error("Please add your skin textures to this folder.")
    sys.exit(1)
else:
    logging.info(f"Found {len(images)} image(s) in '{input_folder}'.")


def generate_random_paint_id():
    """
    Generate a unique paint job ID in the format girlXXXX, where X is a digit.
    Ensures random and valid texture names using the prefix from config.

    Returns:
        str: A unique paint job ID string (e.g., "skin1234" if prefix is "skin").
    """
    digits = ''.join(str(random.randint(0, 9)) for _ in range(4)) # Generate 4 random digits
    return f"{paint_job_prefix}{digits}" # Combine with prefix from config

# Generate unique paint IDs for each source image.
# This loop ensures that even if random IDs collide (unlikely with enough digits),
# we generate a unique ID for every image.
paint_ids = set()
while len(paint_ids) < len(images):
    paint_ids.add(generate_random_paint_id())
paint_ids = list(paint_ids)

# === HELPER FUNCTION ===
def _process_vehicle_type(
    vehicle_type_name: str,
    vehicle_models_list: list,
    current_paint_id: str,
    source_resized_image_path: Path,
    base_paintjob_path_root: Path,
    base_def_path_root: Path,
    external_texconv_path: str,
    texture_dds_format: str,
    sii_create_function,
    sui_create_function,
):
    """
    Processes paint job generation for a specific vehicle type (e.g., truck, trailer) and all its models.

    This function orchestrates several steps for each model in the provided list:
    1.  Creates the necessary output directory structure for the paint job files.
    2.  Determines the correct DDS filename and internal TOBJ texture path based on whether
        it's a truck or a trailer (e.g., "_0.dds" for trucks, "_shared.dds" for trailers).
    3.  Calls `convert_to_dds` to convert the master resized source image to the DDS format.
    4.  Renames the converted DDS file to the game's expected naming convention.
    5.  Calls `create_tobj` to generate the texture object file that references the DDS.
    6.  Calls the provided SII and SUI creation functions to generate the main definition
        files for the paint job.
    7.  Creates empty placeholder SUI files for optional metallic and mask properties,
        allowing users to customize these later.

    Args:
        vehicle_type_name (str): Identifier for the vehicle type, typically "truck" or "trailer_owned".
        vehicle_models_list (list[str]): A list of internal game model names for this vehicle type
                                         (e.g., ["scania.s_2016", "volvo.fh16_2012"]).
        current_paint_id (str): The unique identifier for the current paint job being processed.
        source_resized_image_path (Path): Path to the (master) resized PNG image that serves as the
                                          source texture for this paint job.
        base_paintjob_path_root (Path): The root directory within the mod structure where paint job
                                        files for this vehicle type should be stored (e.g., "output_mod/vehicle/truck/upgrade/paintjob").
        base_def_path_root (Path): The root directory within the mod structure where definition
                                   files for this vehicle type should be stored (e.g., "output_mod/def/vehicle/truck").
        external_texconv_path (str): Filesystem path to the texconv.exe utility.
        texture_dds_format (str): The DDS compression format to use (e.g., "DXT5").
        sii_create_function (callable): A function (e.g., `create_truck_sii`) that will be called
                                        to generate the main .sii accessory definition file.
        sui_create_function (callable): A function (e.g., `create_truck_sui`) that will be called
                                        to generate the shared .sui accessory definition file.
    
    Raises:
        ValueError: If `vehicle_type_name` is not one of the expected values.
    """
    logging.info(f"Processing {vehicle_type_name} models for paint ID: {current_paint_id}...")
    for model in vehicle_models_list:
        logging.info(f"  Generating files for {vehicle_type_name} model: {model}, paint ID: {current_paint_id}")
        # Construct the specific output folder for this paintjob, model, and vehicle type
        paint_folder = base_paintjob_path_root / model / current_paint_id
        paint_folder.mkdir(parents=True, exist_ok=True) # Create directory if it doesn't exist
        logging.debug(f"    Ensured paint folder exists: {paint_folder}")

        # Determine target DDS filename and TOBJ texture path based on vehicle type conventions
        if vehicle_type_name == "truck":
            target_dds_filename = f"{current_paint_id}_0.dds"
            # Note: TOBJ paths for trucks often use "..dds" for one of the texture map entries
            tobj_texture_path = f"/vehicle/truck/upgrade/paintjob/{model}/{current_paint_id}/{current_paint_id}_0..dds"
        elif vehicle_type_name == "trailer_owned":
            target_dds_filename = f"{current_paint_id}_shared.dds"
            tobj_texture_path = f"/vehicle/trailer_owned/upgrade/paintjob/{model}/{current_paint_id}/{target_dds_filename}"
        else:
            # This case should ideally not be reached if called with correct parameters
            raise ValueError(f"Invalid vehicle_type_name provided: {vehicle_type_name}")

        # Convert the master resized image to DDS format for this specific model
        # The output DDS will initially be named based on current_paint_id (e.g., "paint001.DDS")
        convert_to_dds(external_texconv_path, source_resized_image_path, paint_folder, texture_dds_format)
        
        # Rename the output DDS to the specific convention required (e.g., "paint001_0.dds")
        source_dds_output_path = paint_folder / f"{current_paint_id}.DDS" # Default output name from texconv
        final_dds_path = paint_folder / target_dds_filename
        if source_dds_output_path.exists():
            source_dds_output_path.rename(final_dds_path)
        elif final_dds_path.exists(): # If texconv directly created the final name (e.g. if source was already .dds or due to other reasons)
            pass # File is already correctly named, no action needed
        else:
            # Log a warning if the expected DDS file isn't found after conversion attempt
            logging.warning(f"DDS file {source_dds_output_path} not found after conversion for model {model}, paint ID {current_paint_id}. Skipping rename.")


        # Create the TOBJ (Texture Object) file for the newly converted and renamed DDS
        # The TOBJ filename matches the DDS filename, but with a .tobj extension.
        tobj_file_path = paint_folder / target_dds_filename.replace(".dds", ".tobj")
        # The path stored inside the TOBJ is the relative path to the DDS file from the mod's root.
        # The first argument to create_tobj is just the filename part of the texture path.
        create_tobj(tobj_texture_path.split('/')[-1], tobj_file_path, "/".join(tobj_texture_path.split('/')[:-1]), save_mode="default")


        # Create definition files (.sii for main accessory, .sui for shared attributes)
        # These files tell the game how to use the paint job.
        def_path = base_def_path_root / model / "paint_job"
        def_path.mkdir(parents=True, exist_ok=True) # Ensure definition subfolder exists
        
        # Call the respective SUI and SII creation functions passed as arguments
        # These functions are specific to trucks or trailers.
        sui_create_function(current_paint_id, def_path / f"{current_paint_id}_shared.sui", model)
        sii_create_function(current_paint_id, def_path / f"{current_paint_id}.sii", model)

        # Create empty include stubs for metallic and mask SUI files.
        # These allow users to later add custom metallic/mask properties by editing these files
        # without needing to change the main SUI/SII files.
        for suffix in ["metallic", "mask"]:
            include_path = def_path / f"{current_paint_id}_{suffix}.sui"
            include_path.write_text("") # Create an empty file
        logging.debug(f"    Created definition files and stubs for {model}, paint ID {current_paint_id}")
    logging.info(f"Finished processing {vehicle_type_name} models for paint ID {current_paint_id}.\n")

# === MAIN PROCESSING LOOP ===
# Iterate over each source image found in the input folder.
# Each image will become a distinct paint job available on all specified trucks/trailers.
logging.info(f"Starting main processing for {len(images)} image(s) found in '{input_folder_path}'.")
for idx, img_file in enumerate(images):
    paint_id = paint_ids[idx] # Get the unique pre-generated ID for this image
    logging.info(f"--- Processing image {idx+1}/{len(images)}: '{img_file}' with paint_id: '{paint_id}' ---")

    input_path = Path(input_folder) / img_file
    # Define path for the master resized version of the current image (saved as PNG in a temporary folder)
    resized_path = temp_folder / f"{paint_id}.png" 
    
    # Resize the source image to the configured resolution (e.g., 4096x4096).
    # This resized PNG is then used as the single source for all subsequent DDS conversions for this paint_id.
    logging.info(f"  Resizing '{input_path}' to {image_resolution} and saving to '{resized_path}'...")
    resize_image(input_path, resized_path, image_resolution)

    # --- Generate UI (User Interface) assets for the paint job ---
    # These are icons and material files for the in-game paint job selection menu.
    logging.info(f"  Generating UI assets for '{paint_id}'...")
    # Convert the resized image to DDS format for UI purposes.
    convert_to_dds(texconv_path, resized_path, ui_folder, dds_format) 
    ui_dds_temp_name = ui_folder / f"{paint_id}.DDS" # Default output name from texconv (uppercase .DDS)
    final_ui_dds_name = ui_folder / f"{paint_id}.dds" # Desired final name (lowercase .dds)
    if ui_dds_temp_name.exists():
        ui_dds_temp_name.rename(final_ui_dds_name) # Rename to lowercase .dds for consistency
        logging.debug(f"    Renamed UI DDS to {final_ui_dds_name}")
    
    # Create TOBJ file for the UI DDS.
    create_tobj(f"{paint_id}.dds", ui_folder / f"{paint_id}.tobj", "/material/ui/accessory", save_mode="default")
    # Create the .mat (material) file for the UI, which references the UI TOBJ.
    create_ui_mat(paint_id, ui_folder)
    logging.info(f"  UI assets for '{paint_id}' generated successfully.")

    # --- Process Truck Paint Jobs ---
    # Call the helper function to generate all truck-specific files for the current paint_id.
    logging.info(f"  Starting truck paint job processing for '{paint_id}'...")
    _process_vehicle_type(
        vehicle_type_name="truck",
        vehicle_models_list=truck_models,
        current_paint_id=paint_id,
        source_resized_image_path=resized_path,
        base_paintjob_path_root=paintjob_root / "truck/upgrade/paintjob",
        base_def_path_root=def_root / "vehicle/truck",
        external_texconv_path=texconv_path,
        texture_dds_format=dds_format,
        sii_create_function=create_truck_sii,
        sui_create_function=create_truck_sui
    )

    # --- Process Trailer Paint Jobs ---
    # Call the helper function to generate all trailer-specific files for the current paint_id.
    logging.info(f"  Starting trailer paint job processing for '{paint_id}'...")
    _process_vehicle_type(
        vehicle_type_name="trailer_owned",
        vehicle_models_list=trailer_models,
        current_paint_id=paint_id,
        source_resized_image_path=resized_path,
        base_paintjob_path_root=paintjob_root / "trailer_owned/upgrade/paintjob",
        base_def_path_root=def_root / "vehicle/trailer_owned",
        external_texconv_path=texconv_path,
        texture_dds_format=dds_format,
        sii_create_function=create_trailer_sii,
        sui_create_function=create_trailer_sui
    )

    )
    logging.info(f"--- Finished processing for paint_id: '{paint_id}' ---\n")

# === FINAL STEPS ===
# These steps are performed once after all images have been processed.
logging.info("Starting final steps for mod packaging...")

# === MOD ICON ===
# Uses the first image from the input folder to generate the mod icon (mod_icon.jpg).
# This icon is displayed in the game's mod manager.
if images: # Check if there were any images to process (and thus, an images[0] exists)
    logging.info("Generating mod icon...")
    first_image_path = Path(input_folder) / images[0] # Use the first image found
    create_mod_icon(first_image_path, mod_icon_path)
    # The create_mod_icon function in image_utils already prints/logs, so no need for a duplicate message here
    # logging.info(f"Mod icon generated from '{images[0]}' and saved to '{mod_icon_path}'")
else:
    logging.warning("No images found, skipping mod icon generation.")


# === Manifest & Description Files ===
# These files provide metadata for the mod (name, author, version, description) for the game.
logging.info("Generating mod manifest and description files...")
write_manifest(output_folder, mod_name, mod_version, mod_author)
write_description(output_folder, mod_description_content)
# The write_manifest/description functions in mod_metadata already print/log
# logging.info("Mod manifest (manifest.sii) and description (mod_description.txt) generated.")

# === PACK TO .SCS ARCHIVE ===
# If generate_zip is True in the configuration, pack the entire output folder 
# into an .scs archive, which is the format mods use in the game.
if generate_zip:
    logging.info(f"Attempting to pack contents of '{output_folder}' into an .scs archive...")
    # The pack_to_scs function will typically name the archive based on mod_name.
    scs_file = pack_to_scs(output_folder, mod_name) 
    logging.info(f"Mod successfully packed into: '{scs_file}'")
else:
    # If generate_zip is False, the script will leave the generated files in the output_folder.
    # This is useful for debugging or manual adjustments before packing.
    logging.info(f"Mod files prepared in '{output_folder}'. SCS archive generation was skipped (as per config).")

logging.info("\nAll tasks completed successfully!")
