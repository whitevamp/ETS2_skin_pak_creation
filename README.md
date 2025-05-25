# ETS2/ATS Skin Pack Builder

This Python script automates the creation of truck and trailer skin packs for Euro Truck Simulator 2 (ETS2) and American Truck Simulator (ATS). It processes your source images, converts them to the required DDS texture format, generates necessary definition files (.sii, .sui, .tobj, .mat), and structures them into a mod package.

## Features

*   Processes multiple input images (PNG, JPG) into individual paint jobs.
*   Generates paint jobs for a predefined list of trucks and trailers.
*   Creates UI assets for the paint jobs.
*   Generates necessary `.tobj` (texture object) and material (`.mat`) files.
*   Creates `.sii` and `.sui` definition files for paint job accessories.
*   Generates a `manifest.sii` and `mod_description.txt` for the mod.
*   Optionally packages the mod into an `.scs` archive.
*   Customizable via `core/config.py`.

## Prerequisites

1.  **Python 3:** Ensure you have Python 3 installed (version 3.7+ recommended). You can download it from [python.org](https://www.python.org/).
2.  **Pillow Library:** This script uses the Pillow library for image manipulation. Install it via pip:
    ```bash
    pip install Pillow
    ```
3.  **`texconv.exe`:** This is a command-line tool from Microsoft for converting textures to `.DDS` format.
    *   It's part of the DirectXTex library. You can find releases or compile it from source here: [DirectXTex GitHub](https://github.com/Microsoft/DirectXTex)
    *   Download `texconv.exe` and place it either in the same directory as `build_skin_pack.py` or in a directory included in your system's PATH environment variable. Alternatively, you can specify the full path to `texconv.exe` in `core/config.py`.

## How to Use

1.  **Configure Your Mod:**
    *   Open `core/config.py` in a text editor.
    *   **Crucial:** Update `mod_name`, `mod_version`, `mod_author`, and `mod_description_content` to reflect your mod's details.
    *   Set `input_folder` to the directory containing your source skin images (e.g., "skin_sources").
    *   Verify `texconv_path`. If `texconv.exe` is not in your PATH, set this to its full path (e.g., `"C:/Tools/texconv.exe"`).
    *   Adjust `image_resolution` (default is 4096x4096) and `dds_format` (default is "DXT5") if needed.
    *   Set `paint_job_prefix` (default "skin") for generated paint job internal names (e.g., "skin0001").
    *   Set `generate_zip` to `True` to automatically create an `.scs` archive, or `False` to only generate the file structure.

2.  **Add Source Images:**
    *   Place your skin textures (PNG or JPG format) into the folder specified by `input_folder` in `core/config.py`.

3.  **Run the Script:**
    *   Open a terminal or command prompt in the script's main directory.
    *   Execute the script:
        ```bash
        python build_skin_pack.py
        ```

4.  **Output:**
    *   The generated mod files will be in the `output_[mod_name]` directory.
    *   If `generate_zip` was `True`, an `.scs` file will also be created in the root directory.

## Customizing Truck and Trailer Lists

You can modify the lists of trucks and trailers the script generates skins for:

*   **Trucks:** Edit the `truck_models` list in `core/truck_models.py`.
*   **Trailers:** Edit the `trailer_models` list in `core/trailer_models.py`.

Use the game's internal model names.

## Troubleshooting

*   **`texconv.exe` not found:**
    *   Ensure `texconv.exe` is in your system PATH, in the script directory, or that `texconv_path` in `core/config.py` points to the correct location.
*   **Pillow not installed:**
    *   Run `pip install Pillow`.
*   **Permission errors:**
    *   Ensure the script has write permissions for the output and temporary directories.
*   **Image conversion issues:**
    *   Make sure your source images are valid PNG or JPG files.
    *   If DDS conversion fails, check the console output from `texconv.exe` for specific errors.

## Contributing (Example - can be removed or expanded)

Contributions are welcome! If you have improvements or bug fixes, please feel free to fork the repository and submit a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
