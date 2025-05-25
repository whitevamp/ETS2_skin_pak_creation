import os
import zipfile
import subprocess
from pathlib import Path
from PIL import Image
from collections import Counter
import random
from core.tobj_writer import write_tobj
from core.sui_file_creation import create_truck_sui, create_trailer_sui
from core.sii_file_creation import create_truck_sii, create_trailer_sii
from core.trailer_models import trailer_models
from core.truck_models import truck_models
from core.create_ui_mat import create_ui_mat
from core.create_tobj import create_tobj
from core.config import (
    mod_name, input_folder, texconv_path, image_resolution, dds_format,
    generate_zip, output_folder, paintjob_root, def_root,
    ui_folder, mod_icon_path, temp_folder
)

# === CONFIGURATION ===
# mod_name = "girls_skin_pack"
# input_folder = "skin_sources"
# texconv_path = "texconv.exe"
# image_resolution = (4096, 4096)
# dds_format = "DXT5"
# generate_zip = True

# output_folder = Path(f"output_{mod_name}")
# paintjob_root = output_folder / "vehicle"
# def_root = output_folder / "def"
# ui_folder = output_folder / "material/ui/accessory"
# mod_icon_path = output_folder / "mod_icon.jpg"
# temp_folder = Path("temp_resized")

# === INIT ===
for folder in [paintjob_root, def_root, ui_folder, temp_folder]:
    folder.mkdir(parents=True, exist_ok=True)

images = [f for f in os.listdir(input_folder) if f.lower().endswith((".jpg", ".png"))]
# paint_ids = [f"girl{str(i+1).zfill(2)}" for i in range(len(images))]

#completly random hole name
# # Base paint IDs (without extension)
# base_names = [Path(f).stem.lower().replace(" ", "_") for f in images]
# name_counts = Counter()
# paint_ids = []

# for name in base_names:
    # # Clean name, limit length, replace bad chars
    # cleaned = ''.join(c for c in name if c.isalnum() or c == '_')[:10]  # max 10 to leave room for suffix
    # if cleaned.count('_') > 1:
        # cleaned = cleaned.replace('_', '', cleaned.count('_') - 1)  # allow max 1 underscore
    # name_counts[cleaned] += 1
    # suffix = f"_{name_counts[cleaned]-1}" if name_counts[cleaned] > 1 else ""
    # paint_id = (cleaned + suffix)[:12]
    # paint_ids.append(paint_id)

def generate_random_paint_id():
    digits = ''.join(str(random.randint(0, 9)) for _ in range(4))
    # return f"girl({digits[0]})({digits[1]})({digits[2]})({digits[3]})"
    return f"girl{digits}"
    
#paint_ids = [generate_random_paint_id() for _ in images]

paint_ids = set()
while len(paint_ids) < len(images):
    paint_ids.add(generate_random_paint_id())
paint_ids = list(paint_ids)

def convert_to_dds(src, dst_folder):
    subprocess.run([
        texconv_path, "-f", dds_format, "-m", "1", "-o", str(dst_folder), str(src)
    ], check=True)

# def create_tobj(texture_name, tobj_path, virtual_path):
    # content = f'shader_type : "ui"\ntexture : "{virtual_path}/{texture_name}"\n'
    # with open(tobj_path, "w") as f:
        # f.write(content)

def resize_image(src_path, dst_path):
    img = Image.open(src_path).convert("RGBA")
    img = img.resize(image_resolution, Image.LANCZOS)
    img.save(dst_path)

def create_mod_icon(image_path, dst_path):
    img = Image.open(image_path).convert("RGB")
    img = img.resize((276, 162), Image.LANCZOS)
    img.save(dst_path, "JPEG")

# === MAIN PROCESS ===
for idx, img_file in enumerate(images):
    paint_id = paint_ids[idx]
    paint_id0 = paint_id + "_0"
    input_path = Path(input_folder) / img_file
    resized_path = temp_folder / f"{paint_id}.png"
    resize_image(input_path, resized_path)

    # UI DDS + TOBJ
    convert_to_dds(resized_path, ui_folder)
    ui_dds = ui_folder / f"{paint_id}.DDS"
    final_ui_dds = ui_folder / f"{paint_id}.dds"
    if ui_dds.exists():
        ui_dds.rename(final_ui_dds)
    create_tobj(f"{paint_id}.dds", ui_folder / f"{paint_id}.tobj", "/material/ui/accessory", save_mode="default")
    create_ui_mat(paint_id, ui_folder)

    # Trucks
    for truck in truck_models:
        paint_folder = paintjob_root / f"truck/upgrade/paintjob/{truck}/{paint_id}"
        paint_folder.mkdir(parents=True, exist_ok=True)
        convert_to_dds(resized_path, paint_folder)
        dds = paint_folder / f"{paint_id}.DDS"
        dds_final = paint_folder / f"{paint_id}_0.dds"
        if dds.exists():
            dds.rename(dds_final)
        # create_tobj(f"{paint_id}_0.dds", paint_folder / f"{paint_id}_0.tobj", f"/vehicle/truck/upgrade/paintjob/{truck}/{paint_id}")
        create_tobj(f"{paint_id}_0..dds", paint_folder / f"{paint_id}_0.tobj", f"/vehicle/truck/upgrade/paintjob/{truck}/{paint_id}", save_mode="default")


        def_path = def_root / f"vehicle/truck/{truck}/paint_job"
        def_path.mkdir(parents=True, exist_ok=True)
        create_truck_sui(paint_id, def_path / f"{paint_id}_shared.sui", truck)
        create_truck_sii(paint_id, def_path / f"{paint_id}.sii", truck)

        # Create shared includes
        for suffix in ["metallic", "mask"]:
            include_path = def_path / f"{paint_id}_{suffix}.sui"
            include_path.write_text("")

    # Trailers
    for trailer in trailer_models:
        paint_folder = paintjob_root / f"trailer_owned/upgrade/paintjob/{trailer}/{paint_id}"
        paint_folder.mkdir(parents=True, exist_ok=True)
        convert_to_dds(resized_path, paint_folder)
        dds = paint_folder / f"{paint_id}.DDS"
        final_dds = paint_folder / f"{paint_id}_shared.dds"
        if dds.exists():
            dds.rename(final_dds)
        # create_tobj(f"{paint_id}_shared.dds", paint_folder / f"{paint_id}_shared.tobj", f"/vehicle/trailer_owned/upgrade/paintjob/{trailer}/{paint_id}")
        create_tobj(f"{paint_id}_shared.dds", paint_folder / f"{paint_id}_shared.tobj", f"/vehicle/trailer_owned/upgrade/paintjob/{trailer}/{paint_id}", save_mode="default")


        def_path = def_root / f"vehicle/trailer_owned/{trailer}/paint_job"
        def_path.mkdir(parents=True, exist_ok=True)
        create_trailer_sui(paint_id, def_path / f"{paint_id}_shared.sui", trailer)
        create_trailer_sii(paint_id, def_path / f"{paint_id}.sii", trailer)
        
        # Create shared Trailer includes
        for trailer_suffix in ["metallic", "mask"]:
            include_path = def_path / f"{paint_id}_{trailer_suffix}.sui"
            include_path.write_text("")

# === Mod icon ===
if images:
    create_mod_icon(Path(input_folder) / images[0], mod_icon_path)

# === Manifest & Description ===
(output_folder / "manifest.sii").write_text(f"""SiiNunit
{{
	mod_package : .package_name
	{{
		package_version:	"1.0"
		display_name:		"test"
		author:				"wv"
		mp_mod_optional:	true

		icon: "mod_icon.jpg"
		description_file: "mod_description.txt"
		
		category[]: "paint_job"
	}}
}}""")

(output_folder / "mod_description.txt").write_text("""[blue]This mod was created using Mods Studio 2
[orange]www.mods.studio[normal]

this is a mod description, text
""")

# === Pack to SCS ===
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
