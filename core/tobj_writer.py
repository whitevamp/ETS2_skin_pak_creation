"""
Handles the creation of binary .tobj (Texture Object) files for ETS2/ATS.

.tobj files are used by the game engine to reference texture files (usually .dds)
and define certain properties related to how textures are loaded and used.
The exact meaning of many bytes in the .tobj format is not officially documented
and has been determined through community reverse-engineering and tools like
Mods Studio 2.
"""
from pathlib import Path
import sys

def write_tobj(tobj_filepath: Path, texture_path_in_mod: str, save_mode: str = "default") -> None:
    """
    Writes a binary .tobj file, which is a small metadata file pointing to a texture (DDS).

    The .tobj file format contains a header and the path to the texture.
    Different `save_mode` options alter specific bytes in the header, potentially
    affecting texture properties like mipmapping or filtering, though the exact
    effects are often empirical.

    Args:
        tobj_filepath (Path): The full path where the output .tobj file will be saved.
        texture_path_in_mod (str): The relative path to the texture file (e.g., .dds)
                                   as it will be structured within the mod archive.
                                   Example: "/vehicle/truck/upgrade/paintjob/my_truck/skin01/texture.dds"
        save_mode (str): A string key representing different byte configurations for the .tobj header.
                         Valid modes are "default", "mode1", "mode2", "mode3".
                         Defaults to "default".
    """
    # Base byte array for a .tobj file. The first few bytes are a header/magic number.
    # The specific values are based on typical .tobj files.
    # Offset 0-3: Magic number/version (e.g., 01 0A B1 70)
    # Offset 4-19: Seemingly null or reserved bytes.
    # Offset 20-39: Various flags and parameters. Some are modified by 'save_mode'.
    # Offset 40: Length of the texture path string that follows.
    # After this header, the texture path string itself is appended.
    default_bytes = bytearray([
        0x01, 0x0A, 0xB1, 0x70, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, # 0-11
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x02, 0x00, # 12-23 (Flags related to texture type/usage)
        0x02, 0x00, 0x03, 0x03, 0x03, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, # 24-35 (Clamping, filtering, mipmaps flags)
        0x00, 0x01, 0x00, 0x00, 0x35, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00  # 36-47 (Last byte at index 40 is path length, rest can be padding/other data)
    ])

    # These byte sequences are applied at specific offsets based on the save_mode.
    # The exact meaning of these modes and bytes is often not fully clear without
    # extensive testing in-game or disassembling game resources.
    # They likely control texture parameters like wrap modes (clamp/repeat),
    # filtering options, or mipmap levels/biases.
    save_mode_byte_settings = {
        # "default" mode uses the initial values in default_bytes for these specific indices.
        "default":     [0x02, 0x00, 0x03, 0x03, 0x03], # Corresponds to default_bytes[22], [28], [30], [31], [33]
        "mode1":       [0x02, 0x03, 0x00, 0x00, 0x00], # Example: Clamps U, Repeats V/W
        "mode2":       [0x00, 0x03, 0x02, 0x02, 0x00], # Example: Repeats U, Clamps V/W
        "mode3":       [0x00, 0x02, 0x02, 0x02, 0x01], # Example: Repeats U/V/W
    }

    # Apply byte modifications if a non-default save_mode is specified
    if save_mode in save_mode_byte_settings and save_mode != "default":
        mode_specific_bytes = save_mode_byte_settings[save_mode]
        default_bytes[22] = mode_specific_bytes[0] # Affects a flag, possibly related to texture type/channel
        default_bytes[28] = mode_specific_bytes[1] # U-Wrap mode (e.g., 0x03 for REPEAT, 0x02 for CLAMP_TO_EDGE)
        # default_bytes[29] is often 0x00
        default_bytes[30] = mode_specific_bytes[2] # V-Wrap mode
        default_bytes[31] = mode_specific_bytes[3] # W-Wrap mode (for 3D textures, less common for skins)
        # default_bytes[32] is often 0x00
        default_bytes[33] = mode_specific_bytes[4] # Mipmap/filtering related flag
    
    # Encode the texture path string to UTF-8 bytes
    texture_path_bytes = texture_path_in_mod.encode('utf-8')
    
    # Set the byte at offset 40 to the length of the texture path string.
    # The .tobj format requires this length to know how many bytes to read for the path.
    if len(texture_path_bytes) > 255:
        # This is a safeguard; TOBJ paths are typically not this long.
        # The byte at offset 40 is usually a single byte for length.
        # Longer paths might be possible if other parts of the header change,
        # but this writer assumes a single byte length field.
        print(f"Warning: Texture path for TOBJ '{texture_path_in_mod}' is very long ({len(texture_path_bytes)} bytes). This may cause issues.")
    default_bytes[40] = len(texture_path_bytes) # This assumes length fits in one byte.

    # Concatenate the header bytes with the texture path bytes
    full_tobj_data = default_bytes + texture_path_bytes

    # Write the complete byte array to the output .tobj file in binary mode
    try:
        with open(tobj_filepath, 'wb') as f:
            f.write(full_tobj_data)
        print(f"    Successfully created TOBJ: {tobj_filepath} (mode: {save_mode})")
    except IOError as e:
        print(f"❌ Error writing TOBJ file '{tobj_filepath}': {e}")
        raise


if __name__ == "__main__":
    # This section allows the script to be run directly from the command line
    # for creating a single .tobj file, useful for testing or manual creation.
    if len(sys.argv) < 3:
        print("Usage: python tobj_writer.py <output_filename.tobj> <texture_path_in_mod> [save_mode]")
        print("  save_mode can be: default, mode1, mode2, mode3 (optional, defaults to 'default')")
        sys.exit(1)

    output_file = Path(sys.argv[1])
    texture_path_arg = sys.argv[2]
    save_mode_arg = sys.argv[3] if len(sys.argv) > 3 else "default"

    # Basic validation for save_mode argument
    if save_mode_arg not in ["default", "mode1", "mode2", "mode3"]:
        print(f"Error: Invalid save_mode '{save_mode_arg}'. Must be one of: default, mode1, mode2, mode3.")
        sys.exit(1)

    try:
        write_tobj(output_file, texture_path_arg, save_mode_arg)
        print(f"Successfully wrote {output_file} for texture '{texture_path_arg}' with save mode '{save_mode_arg}'.")
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
