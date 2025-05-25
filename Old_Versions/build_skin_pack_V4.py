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
image_resolution = (4096, 4096)
dds_format = "DXT5"
generate_zip = True

truck_models = ["volvo.fh_2021", "volvo.fh_2024"]
trailer_models = [
    "scs.box", "scs.chemtank", "scs.dumper", "scs.foodtank",
    "scs.fueltank", "scs.gastank", "scs.livestock", "scs.silo"
]

output_folder = Path(f"output_{mod_name}")
paintjob_root = output_folder / "vehicle"
def_root = output_folder / "def"
ui_folder = output_folder / "material/ui/accessory"
mod_icon_path = output_folder / "mod_icon.jpg"
temp_folder = Path("temp_resized")

# === INIT ===
for folder in [paintjob_root, def_root, ui_folder, temp_folder]:
    folder.mkdir(parents=True, exist_ok=True)

images = [f for f in os.listdir(input_folder) if f.lower().endswith((".jpg", ".png"))]
paint_ids = [f"girl{str(i+1).zfill(2)}" for i in range(len(images))]

def convert_to_dds(src, dst_folder):
    subprocess.run([
        texconv_path, "-f", dds_format, "-m", "1", "-o", str(dst_folder), str(src)
    ], check=True)

def create_tobj(texture_name, tobj_path, virtual_path):
    content = f'shader_type : "ui"\ntexture : "{virtual_path}/{texture_name}"\n'
    with open(tobj_path, "w") as f:
        f.write(content)

def create_sii(base_name, sii_path, virtual_path, vehicle_type, model_name):
    type_str = "trailer" if vehicle_type == "trailer_owned" else "truck"
    sii = f"""accessory_paint_job_data : {base_name}.paint_job
{{
    name: "{base_name}"
    price: 1
    unlock: 0
    icon: "{base_name}"
    airbrush: true
    suitable_for[]: "{model_name}"
    paint_job_mask: "{virtual_path}"
    color: (1.0, 1.0, 1.0)
    flip_color: (0.0, 0.0, 0.0)
    base_color: (0.0, 0.0, 0.0)
}}"""
    with open(sii_path, "w") as f:
        f.write(sii)

def resize_image(src_path, dst_path, size=image_resolution):
    img = Image.open(src_path).convert("RGBA")
    img = img.resize(size, Image.LANCZOS)
    img.save(dst_path)

def create_mod_icon(image_path, dst_path):
    img = Image.open(image_path).convert("RGB")
    img = img.resize((276, 162), Image.LANCZOS)
    img.save(dst_path, "JPEG")

# === MAIN PROCESS ===
for idx, img_file in enumerate(images):
    paint_id = paint_ids[idx]
    input_path = Path(input_folder) / img_file
    resized_path = temp_folder / f"{paint_id}.png"
    resize_image(input_path, resized_path)

    # UI icon (DDS + TOBJ)
    convert_to_dds(resized_path, ui_folder)
    ui_dds_path = ui_folder / f"{paint_id}.DDS"
    ui_final_dds = ui_folder / f"{paint_id}.dds"
    if ui_dds_path.exists():
        ui_dds_path.rename(ui_final_dds)
    create_tobj(f"{paint_id}.dds", ui_folder / f"{paint_id}.tobj", "/material/ui/accessory")

    # Process trucks
    for truck in truck_models:
        paintjob_folder = paintjob_root / f"truck/upgrade/paintjob/{truck}/{paint_id}"
        paintjob_folder.mkdir(parents=True, exist_ok=True)
        convert_to_dds(resized_path, paintjob_folder)
        dds_path = paintjob_folder / f"{paint_id}.DDS"
        final_dds = paintjob_folder / f"{paint_id}.dds"
        if dds_path.exists():
            dds_path.rename(final_dds)

        create_tobj(f"{paint_id}.dds", paintjob_folder / f"{paint_id}.tobj", f"/vehicle/truck/upgrade/paintjob/{truck}/{paint_id}")

        def_path = def_root / f"vehicle/truck/{truck}/paint_job"
        def_path.mkdir(parents=True, exist_ok=True)
        create_sii(paint_id, def_path / f"{paint_id}.sii", f"/vehicle/truck/upgrade/paintjob/{truck}/{paint_id}/{paint_id}.tobj", "truck", truck)

    # Process trailers
    for trailer in trailer_models:
        paintjob_folder = paintjob_root / f"trailer_owned/upgrade/paintjob/{trailer}/{paint_id}"
        paintjob_folder.mkdir(parents=True, exist_ok=True)
        convert_to_dds(resized_path, paintjob_folder)
        dds_path = paintjob_folder / f"{paint_id}.DDS"
        final_dds = paintjob_folder / f"{paint_id}.dds"
        if dds_path.exists():
            dds_path.rename(final_dds)

        create_tobj(f"{paint_id}.dds", paintjob_folder / f"{paint_id}.tobj", f"/vehicle/trailer_owned/upgrade/paintjob/{trailer}/{paint_id}")

        def_path = def_root / f"vehicle/trailer_owned/{trailer}/paint_job"
        def_path.mkdir(parents=True, exist_ok=True)
        create_sii(paint_id, def_path / f"{paint_id}.sii", f"/vehicle/trailer_owned/upgrade/paintjob/{trailer}/{paint_id}/{paint_id}.tobj", "trailer_owned", trailer)

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
