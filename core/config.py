# config.py

from pathlib import Path

# === CONFIGURATION ===
mod_name = "girls_skin_pack"
input_folder = "skin_sources"
texconv_path = "texconv.exe"
image_resolution = (4096, 4096)
dds_format = "DXT5"
generate_zip = True

output_folder = Path(f"output_{mod_name}")
paintjob_root = output_folder / "vehicle"
def_root = output_folder / "def"
ui_folder = output_folder / "material/ui/accessory"
mod_icon_path = output_folder / "mod_icon.jpg"
temp_folder = Path("temp_resized")
