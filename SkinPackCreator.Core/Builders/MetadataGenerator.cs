using System.IO;
using System.Text;
using System.Threading.Tasks;
using SkinPackCreator.Core.Models; // For ProjectSettings

namespace SkinPackCreator.Core.Builders
{
    public class MetadataGenerator
    {
        // Generates the content for the manifest.sii file.
        // Uses properties from ProjectSettings like ModName, ModVersion, ModAuthor, and ModIconFileName.
        public string BuildManifestSiiContent(ProjectSettings settings)
        {
            if (settings == null)
            {
                // Consider throwing ArgumentNullException for settings
                return string.Empty; 
            }

            StringBuilder sb = new StringBuilder();
            sb.AppendLine("SiiNunit"); // Standard SII file header
            sb.AppendLine("{");
            // The ".package_name" is a placeholder that the game replaces or uses internally.
            sb.AppendLine("mod_package : .package_name"); 
            sb.AppendLine("{");
            sb.AppendLine($"	display_name: "{settings.ModName}"");
            sb.AppendLine($"	version: "{settings.ModVersion}"");
            sb.AppendLine($"	author: "{settings.ModAuthor}"");
            sb.AppendLine("	category: "paint_job""); // Fixed category for skin/paint job mods
            sb.AppendLine("	description: "mod_description.txt""); // Standard link to the description file
            sb.AppendLine($"	icon: "{settings.ModIconFileName}""); // e.g., "mod_icon.jpg", located at mod root

            // Optional: Multiplayer compatibility flag.
            // 1 = Not compatible with multiplayer
            // 2 = Compatible with multiplayer (Convoy mode)
            // Not explicitly in original Python, but good to be aware of. Defaulting to not include.
            // sb.AppendLine("	mp_compatibility: 2"); 

            sb.AppendLine("}");
            sb.AppendLine("}");

            return sb.ToString();
        }

        // Generates the content for the mod_description.txt file.
        // This is simply the ModDescription string from ProjectSettings.
        public string BuildModDescriptionContent(ProjectSettings settings)
        {
            if (settings == null)
            {
                // Consider throwing ArgumentNullException
                return string.Empty;
            }
            return settings.ModDescription; // Direct content from settings
        }

        // Asynchronously saves the manifest.sii file to the specified path.
        public async Task<bool> SaveManifestFileAsync(string manifestFilePath, string content)
        {
            if (string.IsNullOrWhiteSpace(manifestFilePath) || content == null) return false;
            try
            {
                string? directory = Path.GetDirectoryName(manifestFilePath);
                if (directory != null && !Directory.Exists(directory))
                {
                    Directory.CreateDirectory(directory);
                }
                // manifest.sii files are typically UTF-8 without BOM.
                await File.WriteAllTextAsync(manifestFilePath, content, new UTF8Encoding(false));
                return true;
            }
            catch (System.Exception ex) // Log ex
            {
                return false;
            }
        }

        // Asynchronously saves the mod_description.txt file to the specified path.
        public async Task<bool> SaveDescriptionFileAsync(string descriptionFilePath, string content)
        {
            if (string.IsNullOrWhiteSpace(descriptionFilePath) || content == null) return false;
            try
            {
                string? directory = Path.GetDirectoryName(descriptionFilePath);
                if (directory != null && !Directory.Exists(directory))
                {
                    Directory.CreateDirectory(directory);
                }
                // .txt files are often best saved as UTF-8 with BOM for wider editor compatibility.
                await File.WriteAllTextAsync(descriptionFilePath, content, new UTF8Encoding(true));
                return true;
            }
            catch (System.Exception ex) // Log ex
            {
                return false;
            }
        }
    }
}
