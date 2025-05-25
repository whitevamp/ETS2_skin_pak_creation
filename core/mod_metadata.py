"""
Handles the creation of mod metadata files for ETS2/ATS.

This module is responsible for generating:
- `manifest.sii`: Contains essential mod information like name, version, author,
  icon, description file reference, and category.
- `mod_description.txt`: A user-facing description of the mod, often displayed
  in the game's mod manager.
"""
from pathlib import Path

def write_manifest(output_folder: Path, mod_name: str, version: str = "1.0.0", author: str = "Your Name") -> None:
    """
    Writes the `manifest.sii` file for the mod.

    This file is crucial for the game to recognize and display the mod correctly.
    It includes metadata such as the mod's version, display name, author,
    and references to its icon and description file.

    Args:
        output_folder (Path): The root directory of the mod output where `manifest.sii` will be saved.
        mod_name (str): The display name of the mod (e.g., "My Awesome Skin Pack").
        version (str): The version string for the mod (e.g., "1.0.0").
        author (str): The name of the mod author.
    """
    # Define the content of the manifest.sii file using SiiNunit format
    # .package_name is a convention, the actual name is defined by display_name.
    manifest_content = f"""SiiNunit
{{
mod_package : .package_name
{{
	package_version:	"{version}"
	display_name:		"{mod_name}"
	author:				"{author}"

	# Indicates if the mod is optional for multiplayer sessions
	mp_mod_optional:	true

	# References to other files within the mod structure
	icon:				"mod_icon.jpg"          # Path to the mod's icon (276x162 JPG)
	description_file:	"mod_description.txt"   # Path to the mod's description text file

	# Category of the mod, helps in organizing within the game's mod manager
	category[]:			"paint_job"
}}
}}"""
    # Construct the full path to the manifest file and write the content
    manifest_file_path = output_folder / "manifest.sii"
    with open(manifest_file_path, "w", encoding="utf-8") as f:
        f.write(manifest_content)
    print(f"    Successfully created manifest: {manifest_file_path}")


def write_description(output_folder: Path, description_content: str) -> None:
    """
    Writes the `mod_description.txt` file for the mod.

    This file contains the textual description of the mod that is typically
    displayed to the user in the game's mod manager.

    Args:
        output_folder (Path): The root directory of the mod output where
                              `mod_description.txt` will be saved.
        description_content (str): The string content for the mod description.
                                   This can be multi-line.
    """
    # Construct the full path to the description file and write the content
    description_file_path = output_folder / "mod_description.txt"
    with open(description_file_path, "w", encoding="utf-8") as f:
        f.write(description_content)
    print(f"    Successfully created mod description: {description_file_path}")

