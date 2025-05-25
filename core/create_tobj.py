from core.tobj_writer import write_tobj

def create_tobj(texture_name, tobj_path, virtual_path, save_mode="default"):
    """
    Creates a valid binary .tobj file using SCS Software structure.

    :param texture_name: The DDS file name (e.g., "my_skin.dds")
    :param tobj_path: Output .tobj file path
    :param virtual_path: Virtual texture path, e.g., /vehicle/trailer/my_skin
    :param save_mode: Save mode to use; one of: "default", "mode1", "mode2", "mode3"
    """
    texture_path = f"{virtual_path}/{texture_name}"
    write_tobj(tobj_path, texture_path, save_mode)
