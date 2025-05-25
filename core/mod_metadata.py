from pathlib import Path

def write_manifest(output_folder: Path, mod_name: str, version: str = "1.0", author: str = "wv"):
    """
    Writes the `manifest.sii` file for the mod.

    Args:
        output_folder (Path): Root output directory.
        mod_name (str): Display name of the mod.
        version (str): Mod version.
        author (str): Author name.
    """
    manifest_content = f"""SiiNunit
{{
	mod_package : .package_name
	{{
		package_version:	"{version}"
		display_name:		"{mod_name}"
		author:				"{author}"
		mp_mod_optional:	true

		icon: "mod_icon.jpg"
		description_file: "mod_description.txt"
		
		category[]: "paint_job"
	}}
}}"""
    (output_folder / "manifest.sii").write_text(manifest_content)


def write_description(output_folder: Path):
    """
    Writes the `mod_description.txt` for the mod.

    Args:
        output_folder (Path): Root output directory.
    """
    description = """[blue]This mod was created using Mods Studio 2
[orange]www.mods.studio[normal]

this is a mod description, text
"""
    (output_folder / "mod_description.txt").write_text(description)

