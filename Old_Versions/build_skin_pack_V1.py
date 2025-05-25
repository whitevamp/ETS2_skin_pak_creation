import os
import zipfile
import subprocess
from pathlib import Path
from PIL import Image
import shutil
from PIL import Image, ImageDraw, ImageFont


# === CONFIGURATION ===
mod_name = "girls_skin_pack"
input_folder = "skin_sources"       # Folder containing .jpg/.png files
texconv_path = "texconv.exe"        # Path to texconv (assumes it's in PATH)
image_resolution = "4096x4096"      # Resolution for DDS (optional, just for naming)
target_truck = "all"                # "all" = all trucks, or use e.g., "scania.r"
output_folder = f"output_{mod_name}"
dds_format = "DXT5"
generate_zip = True                 # Set to False to skip packaging

# === PATHS ===
paintjob_folder = Path(output_folder) / "vehicle/truck/upgrade/paintjob" / mod_name
def_folder = Path(output_folder) / f"def/vehicle/truck/{target_truck}/paint_job"
output_zip = Path(f"{mod_name}.scs")

# === SETUP ===
paintjob_folder.mkdir(parents=True, exist_ok=True)
def_folder.mkdir(parents=True, exist_ok=True)
images = [f for f in os.listdir(input_folder) if f.lower().endswith((".jpg", ".png"))]

# === FUNCTIONS ===
def convert_to_dds(src, dst):
    subprocess.run([
        texconv_path, "-f", dds_format, "-m", "1", "-o", str(dst), str(src)
    ], check=True)

def create_tobj(dds_name, tobj_path):
    content = f"path=\"/vehicle/truck/upgrade/paintjob/{mod_name}/{dds_name}\"\n"
    with open(tobj_path, "w") as f:
        f.write(content)

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
    with open(sii_path, "w") as f:
        f.write(sii)

# === PROCESS IMAGES ===
# for idx, img_file in enumerate(images, 1):
    base_name = f"girls{idx:02d}"
    input_path = Path(input_folder) / img_file
    dds_name = f"{base_name}.dds"
    tobj_name = f"{base_name}.tobj"
    sii_name = f"{base_name}.sii"

    # # Convert image
    # # convert_to_dds(input_path, paintjob_folder)
    # # Convert image
    # convert_to_dds(input_path, paintjob_folder)

    # # Rename output .dds file
    # original_dds_name = input_path.stem + ".DDS"  # texconv outputs uppercase extension
    # original_dds_path = paintjob_folder / original_dds_name
    # new_dds_path = paintjob_folder / dds_name
    # if original_dds_path.exists():
        # original_dds_path.rename(new_dds_path)
    # else:
        # print(f"⚠️ Warning: DDS not found: {original_dds_path}")

    # # Create TOBJ and SII files
    # create_tobj(dds_name, paintjob_folder / tobj_name)
    # create_sii(base_name, def_folder / sii_name, tobj_name)
    # Image preprocessing output temp folder
    def_folder = Path("temp_resized")
    def_folder.mkdir(exist_ok=True)

def resize_image_to_valid(input_path, output_path, size=(4096, 4096)):
    img = Image.open(input_path)
    img = img.convert("RGBA")
    img = img.resize(size, Image.LANCZOS)
    img.save(output_path)
    #shutil.rmtree(def_folder)

for idx, img_file in enumerate(images, 1):
    base_name = f"girls{idx:02d}"
    input_path = Path(input_folder) / img_file
    temp_png_path = def_folder / f"{base_name}.png"
    dds_name = f"{base_name}.dds"
    tobj_name = f"{base_name}.tobj"
    sii_name = f"{base_name}.sii"

    # Resize & save to temp .png for conversion
    resize_image_to_valid(input_path, temp_png_path)

    # Convert resized image to .dds
    convert_to_dds(temp_png_path, paintjob_folder)

    # Rename DDS to match mod name
    original_dds_path = paintjob_folder / f"{base_name}.DDS"
    new_dds_path = paintjob_folder / dds_name
    if original_dds_path.exists():
        original_dds_path.rename(new_dds_path)
    else:
        print(f"⚠️ Warning: DDS not found: {original_dds_path}")

    # Create TOBJ and SII files
    create_tobj(dds_name, paintjob_folder / tobj_name)
    create_sii(base_name, def_folder / sii_name, tobj_name)
    

def create_mod_icon(path):
    size = (256, 256)
    img = Image.new("RGB", size, color=(30, 30, 30))
    draw = ImageDraw.Draw(img)
    text = "GIRLS\nSKINS"
    # Simple text centered
    font_size = 40
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    w, h = draw.multiline_text(text, font=font)
    draw.multiline_text(((size[0]-w)/2, (size[1]-h)/2), text, fill="white", font=font, align="center")
    img.save(path)

    mod_icon_path = Path(output_folder) / "mod_icon.jpg"
    if not mod_icon_path.exists():
        create_mod_icon(mod_icon_path)
    
def create_paintjob_icon(path, color=(255, 0, 0)):
    size = (256, 256)
    img = Image.new("RGBA", size, color=color)
    img.save(path)

for idx, img_file in enumerate(images, 1):
    base_name = f"girls{idx:02d}"
    icon_path = paintjob_folder / f"{base_name}.png"

    # Generate simple colored icon (random color example)
    import random
    color = tuple(random.randint(0, 255) for _ in range(3)) + (255,)
    create_paintjob_icon(icon_path, color=color)

# === ZIP TO .SCS ===
if generate_zip:
    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as scs:
        for root, _, files in os.walk(output_folder):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, output_folder)
                scs.write(full_path, rel_path)
    print(f"✅ Packed mod into: {output_zip}")
else:
    print("✅ Mod files generated. No .scs archive created.")
