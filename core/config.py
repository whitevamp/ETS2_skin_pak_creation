 #config.py

from pathlib import Path

# === CONFIGURATION ===
# TODO: Customize these values
mod_name = "MySkinPack"
# TODO: Customize these values
mod_version = "1.0.0"
# TODO: Customize these values
mod_author = "Your Name"
# TODO: Customize these values
paint_job_prefix = "skin"
# TODO: Customize these values
mod_description_content = """\
    My awesome skin pack!
    - Skin 1
    - Skin 2
    Created with the ETS2/ATS Skin Pack Builder.
    """
input_folder = "skin_sources"
texconv_path = "Externals/texconv.exe"
image_resolution = (4096, 4096)
ui_accessory_resolution = (256, 54) # Resolution for UI accessory icons
dds_format = "DXT5"
create_mask_sui = True
create_metallic_sui = True
generate_zip = True

output_folder = Path(f"output_{mod_name}")
paintjob_root = output_folder / "vehicle"
def_root = output_folder / "def"
ui_folder = output_folder / "material/ui/accessory"
mod_icon_path = output_folder / "mod_icon.jpg"
temp_folder = Path("temp_resized")

