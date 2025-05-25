"""
Provides a higher-level function to create .tobj (Texture Object) files.

This module uses the lower-level `tobj_writer.write_tobj` function to generate
.tobj files by constructing the full virtual texture path before calling the writer.
"""
from pathlib import Path
from core.tobj_writer import write_tobj

def create_tobj(texture_filename: str, tobj_output_path: Path, virtual_base_path: str, save_mode: str = "default") -> None:
    """
    Creates a binary .tobj file that points to a given texture file.

    This function constructs the full internal texture path required by the .tobj file
    (e.g., "/vehicle/trailer_owned/upgrade/paintjob/my_trailer/skin_01.dds")
    and then calls `write_tobj` to generate the actual .tobj file.

    Args:
        texture_filename (str): The filename of the texture (e.g., "my_skin.dds", "ui_icon.dds").
        tobj_output_path (Path): The complete filesystem path where the .tobj file will be saved.
        virtual_base_path (str): The virtual base path within the mod where the texture is located
                                 (e.g., "/material/ui/accessory", 
                                 "/vehicle/truck/upgrade/paintjob/scania_s_2016/cool_skin").
        save_mode (str): The save mode for `tobj_writer.write_tobj`, influencing
                         certain bytes in the .tobj header.
                         Options: "default", "mode1", "mode2", "mode3".
                         Defaults to "default".
    """
    # Construct the full virtual path that will be embedded within the .tobj file.
    # This path tells the game where to find the actual texture (.dds file).
    full_virtual_texture_path = f"{virtual_base_path}/{texture_filename}"
    
    # Call the low-level TOBJ writer function
    write_tobj(tobj_output_path, full_virtual_texture_path, save_mode)
    # A print statement confirming creation is typically in write_tobj itself.
    # If not, or if more specific context is needed here, it could be added:
    # print(f"    TOBJ creation request for: {tobj_output_path} -> {full_virtual_texture_path}")
