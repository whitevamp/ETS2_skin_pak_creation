# tobj_writer.py

def write_tobj(filename, texture_path, save_mode="default"):
    """
    Writes a binary .tobj file for SCS Software modding.
    
    :param filename: Output .tobj file path
    :param texture_path: Relative texture path (e.g., /vehicle/.../file.dds)
    :param save_mode: One of: "default", "mode1", "mode2", "mode3"
    """
    default_bytes = bytearray([
        0x01, 0x0A, 0xB1, 0x70, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x02, 0x00,
        0x02, 0x00, 0x03, 0x03, 0x03, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00,
        0x00, 0x01, 0x00, 0x00, 0x35, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ])

    save_mode_bytes = {
        "default":     [0x02, 0x00, 0x03, 0x03, 0x03],
        "mode1":       [0x02, 0x03, 0x00, 0x00, 0x00],
        "mode2":       [0x00, 0x03, 0x02, 0x02, 0x00],
        "mode3":       [0x00, 0x02, 0x02, 0x02, 0x01],
    }

    if save_mode in save_mode_bytes and save_mode != "default":
        default_bytes[22] = save_mode_bytes[save_mode][0]
        default_bytes[28] = save_mode_bytes[save_mode][1]
        default_bytes[30] = save_mode_bytes[save_mode][2]
        default_bytes[31] = save_mode_bytes[save_mode][3]
        default_bytes[33] = save_mode_bytes[save_mode][4]

    texture_bytes = texture_path.encode('utf-8')
    default_bytes[40] = len(texture_bytes)

    full_data = default_bytes + texture_bytes

    with open(filename, 'wb') as f:
        f.write(full_data)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python tobj_writer.py <output.tobj> <texture.dds path> [save_mode]")
        sys.exit(1)

    filename = sys.argv[1]
    texture_path = sys.argv[2]
    save_mode = sys.argv[3] if len(sys.argv) > 3 else "default"

    write_tobj(filename, texture_path, save_mode)
    print(f"Wrote {filename} for {texture_path} with mode {save_mode}")
