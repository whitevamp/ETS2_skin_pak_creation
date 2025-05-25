import os
import zipfile
import subprocess
from pathlib import Path
from PIL import Image
import shutil

# === CONFIGURATION ===
mod_name = "girls_skin_pack"
input_folder = "skin_sources"
texconv_path = "texconv.exe"
image_resolution = "4096x4096"
target_truck = "all"
output_folder = Path(f"output_{mod_name}")
dds_format = "DXT5"
generate_zip = True

# === PATH SETUP ===
paintjob_folder = output_folder / "vehicle/truck/upgrade/paintjob" / mod_name
def_folder = output_folder / f"def/vehicle/truck/{target_truck}/paint_job"
ui_folder = output_folder / "material/ui/accessory"
mod_icon_path = output_folder / "mod_icon.jpg"
temp_folder = Path("temp_resized")

# === INIT ===
for folder in [paintjob_folder, def_folder, ui_folder, temp_folder]:
    folder.mkdir(parents=True, exist_ok=True)

images = [f for f in os.listdir(input_folder) if f.lower().endswith((".jpg", ".png"))]

def convert_to_dds(src, dst_folder):
    subprocess.run([
        texconv_path, "-f", dds_format, "-m", "1", "-o", str(dst_folder), str(src)
    ], check=True)

def create_tobj(texture_name, tobj_path, virtual_path):
    content = f'shader_type : "ui"\ntexture : "{virtual_path}/{texture_name}"\n'
    with open(tobj_path, "w") as f:
        f.write(content)

def create_sii(base_name, sii_path, texture_path):
    sii = f"""accessory_paint_job_data : {base_name}.paint_job
{{
    name: "{base_name}"
    price: 1
    unlock: 0
    icon: "{base_name}"
    airbrush: true
    suitable_for[]: "{target_truck}"
    paint_job_mask: "/vehicle/truck/upgrade/paintjob/{mod_name}/{texture_path}"
    color: (1.0, 1.0, 1.0)
    flip_color: (0.0, 0.0, 0.0)
    base_color: (0.0, 0.0, 0.0)
}}"""
    with open(sii_path, "w") as f:
        f.write(sii)

def resize_image(src_path, dst_path, size=(4096, 4096)):
    img = Image.open(src_path).convert("RGBA")
    img = img.resize(size, Image.LANCZOS)
    img.save(dst_path)

def create_mod_icon(image_path, dst_path):
    img = Image.open(image_path).convert("RGB")
    img = img.resize((276, 162), Image.LANCZOS)
    img.save(dst_path, "JPEG")

# === MAIN PROCESS ===
for idx, img_file in enumerate(images, 1):
    base_name = f"girls{idx:02d}"
    input_path = Path(input_folder) / img_file
    resized_path = temp_folder / f"{base_name}.png"

    # Resize
    resize_image(input_path, resized_path)

    # Convert to DDS (paintjob)
    convert_to_dds(resized_path, paintjob_folder)
    paintjob_dds_original = paintjob_folder / f"{base_name}.DDS"
    paintjob_dds_final = paintjob_folder / f"{base_name}.dds"
    if paintjob_dds_original.exists():
        paintjob_dds_original.rename(paintjob_dds_final)

    # Create TOBJ (paintjob)
    paintjob_tobj = paintjob_folder / f"{base_name}.tobj"
    create_tobj(f"{base_name}.dds", paintjob_tobj, f"/vehicle/truck/upgrade/paintjob/{mod_name}")

    # Create SII
    sii_path = def_folder / f"{base_name}.sii"
    create_sii(base_name, sii_path, f"{base_name}.tobj")

    # UI icon (DDS + TOBJ)
    convert_to_dds(resized_path, ui_folder)
    ui_dds_original = ui_folder / f"{base_name}.DDS"
    ui_dds_final = ui_folder / f"{base_name}.dds"
    if ui_dds_original.exists():
        ui_dds_original.rename(ui_dds_final)

    ui_tobj = ui_folder / f"{base_name}.tobj"
    create_tobj(f"{base_name}.dds", ui_tobj, "/material/ui/accessory")

# === Mod icon ===
if images:
    create_mod_icon(Path(input_folder) / images[0], mod_icon_path)

# === PACK TO SCS ===
if generate_zip:
    scs_name = Path(f"{mod_name}.scs")
    with zipfile.ZipFile(scs_name, "w", zipfile.ZIP_DEFLATED) as scs:
        for root, _, files in os.walk(output_folder):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, output_folder)
                scs.write(full_path, rel_path)
    print(f"✅ Packed mod into: {scs_name}")
else:
    print("✅ Mod files prepared (no .scs zip created)")
