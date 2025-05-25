import os
import zipfile
import subprocess
from pathlib import Path
from PIL import Image
import shutil

# === CONFIGURATION ===
mod_name = "girls_skin_pack"
input_folder = Path("skin_sources")
texconv_path = "texconv.exe"
output_folder = Path(f"output_{mod_name}")
image_resolution = (4096, 4096)
dds_format = "DXT5"
target_truck = "all"
generate_zip = True

# === PATH SETUP ===
paintjob_folder = output_folder / "vehicle/truck/upgrade/paintjob" / mod_name
def_folder = output_folder / f"def/vehicle/truck/{target_truck}/paint_job"
mod_icon_path = output_folder / "mod_icon.jpg"
output_zip = Path(f"{mod_name}.scs")

# Create required folders
paintjob_folder.mkdir(parents=True, exist_ok=True)
def_folder.mkdir(parents=True, exist_ok=True)

# === UTILITY FUNCTIONS ===
def convert_to_dds(src_path, dst_folder):
    subprocess.run([
        texconv_path, "-f", dds_format, "-m", "1", "-o", str(dst_folder), str(src_path)
    ], check=True)

def create_tobj(dds_name, tobj_path):
    content = f"path=\"/vehicle/truck/upgrade/paintjob/{mod_name}/{dds_name}\"\n"
    tobj_path.write_text(content)

def create_sii(name, sii_path, tobj_name):
    sii = f"""accessory_paint_job_data : {name}.paint_job
{{
    name: "{name}"
    price: 1
    unlock: 0
    icon: "{name}"
    airbrush: true
    suitable_for[]: "{target_truck}"
    paint_job_mask: "/vehicle/truck/upgrade/paintjob/{mod_name}/{tobj_name}"
    color: (1.0, 1.0, 1.0)
    flip_color: (0.0, 0.0, 0.0)
    base_color: (0.0, 0.0, 0.0)
}}"""
    sii_path.write_text(sii)

# def resize_image(src, dst, size=image_resolution):
    # img = Image.open(src).convert("RGBA")
    # img = img.resize(size, Image.LANCZOS)
    # img.save(dst)
def resize_image(src, dst, size=image_resolution):
    img = Image.open(src).convert("RGBA")
    img = img.resize(size, Image.LANCZOS)

    # If saving to JPG, remove alpha
    if dst.suffix.lower() in [".jpg", ".jpeg"]:
        img = img.convert("RGB")

    img.save(dst)

# === MAIN PROCESSING LOOP ===
images = [f for f in input_folder.glob("*") if f.suffix.lower() in [".png", ".jpg", ".jpeg"]]

for idx, img_path in enumerate(images, 1):
    base_name = f"girls{idx:02d}"
    temp_png = paintjob_folder / f"{base_name}_temp.png"
    dds_name = f"{base_name}.dds"
    tobj_name = f"{base_name}.tobj"
    sii_name = f"{base_name}.sii"
    icon_path = paintjob_folder / f"{base_name}.png"

    # Resize input to 4096x4096
    resize_image(img_path, temp_png)

    # Convert to DDS
    convert_to_dds(temp_png, paintjob_folder)
    temp_png.unlink()  # Remove temp PNG

    # Rename DDS file
    dds_output_path = paintjob_folder / (temp_png.stem + ".DDS")
    final_dds_path = paintjob_folder / dds_name
    if dds_output_path.exists():
        dds_output_path.rename(final_dds_path)
    else:
        print(f"⚠️ DDS not found for {base_name}")
        continue

    # Use resized input as the icon
    resize_image(img_path, icon_path, size=(256, 256))

    # Create TOBJ & SII
    create_tobj(dds_name, paintjob_folder / tobj_name)
    create_sii(base_name, def_folder / sii_name, tobj_name)

# === Create accessory icons ===
accessory_ui_folder = Path(output_folder) / "material/ui/accessory"
accessory_ui_folder.mkdir(parents=True, exist_ok=True)

for idx, img_file in enumerate(images, 1):
    base_name = f"girls{idx:02d}"
    source_icon = paintjob_folder / f"{base_name}.png"
    dst_dds = accessory_ui_folder / f"{base_name}.dds"
    dst_tobj = accessory_ui_folder / f"{base_name}.tobj"

    # Convert to DDS (icon for configurator)
    convert_to_dds(source_icon, accessory_ui_folder)

    # Rename DDS (texconv outputs .DDS)
    original_icon_dds = accessory_ui_folder / f"{base_name}.DDS"
    if original_icon_dds.exists():
        original_icon_dds.rename(dst_dds)
    else:
        print(f"⚠️ Icon DDS not found: {original_icon_dds}")

    # Create TOBJ file
    create_tobj(f"{base_name}.dds", dst_tobj)

# === MOD ICON ===
if not mod_icon_path.exists() and images:
    resize_image(images[0], mod_icon_path, size=(256, 256))

# === ZIP OUTPUT ===
if generate_zip:
    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as scs:
        for root, _, files in os.walk(output_folder):
            for file in files:
                full_path = Path(root) / file
                rel_path = full_path.relative_to(output_folder)
                scs.write(full_path, rel_path)
    print(f"✅ Mod packed into: {output_zip}")
else:
    print("✅ Files prepared in:", output_folder)
