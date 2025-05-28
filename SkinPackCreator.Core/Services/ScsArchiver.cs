using System.IO;
using System.IO.Compression; // For ZipFile, CompressionLevel
using System.Threading.Tasks;

namespace SkinPackCreator.Core.Services
{
    public class ScsArchiver
    {
        // Asynchronously creates an SCS (which is essentially a zip) archive from a source directory.
        // sourceDirectoryPath: The directory containing all mod files to be packed (e.g., "output_mod/my_mod_name/").
        //                      The contents of this directory will be at the root of the archive.
        // outputDirectory: The directory where the .scs file will be saved (e.g., "C:\MyMods").
        // scsFileName: The name of the .scs file (e.g., "MySkinPack.scs").
        // compressionLevel: The compression level to use.
        public async Task<(bool Success, string Message, string? OutputFilePath)> PackDirectoryToScsAsync(
            string sourceDirectoryPath,
            string outputDirectory, // Directory to save the SCS file
            string scsFileName,     // Name of the SCS file
            CompressionLevel compressionLevel = CompressionLevel.Optimal)
        {
            if (string.IsNullOrWhiteSpace(sourceDirectoryPath))
                return (false, "Source directory for SCS packaging is not specified.", null);
            if (!Directory.Exists(sourceDirectoryPath))
                return (false, $"Source directory not found: {sourceDirectoryPath}", null);
            if (string.IsNullOrWhiteSpace(outputDirectory))
                return (false, "Output directory for SCS file not specified.", null);
            if (string.IsNullOrWhiteSpace(scsFileName))
                return (false, "SCS file name not specified.", null);
            if (!scsFileName.EndsWith(".scs", System.StringComparison.OrdinalIgnoreCase))
                scsFileName += ".scs"; // Ensure .scs extension


            string fullOutputScsFilePath = Path.Combine(outputDirectory, scsFileName);

            try
            {
                // Ensure the output directory for the SCS file exists
                if (!Directory.Exists(outputDirectory))
                {
                    Directory.CreateDirectory(outputDirectory);
                }

                // Delete the target SCS file if it already exists to prevent errors.
                if (File.Exists(fullOutputScsFilePath))
                {
                    File.Delete(fullOutputScsFilePath);
                }

                // Create the zip file. Using Task.Run to offload the blocking I/O.
                // ZipFile.CreateFromDirectory includes the source directory's name as a root folder in the zip.
                // To match the Python script's behavior (files at the root of the zip),
                // we need to iterate and add files or use a different approach if CreateFromDirectory
                // cannot place files at the root directly without the base folder.
                // However, the standard for SCS mods is often that the *contents* of a folder (like "my_mod_name")
                // are zipped, not the folder "my_mod_name" itself.
                // The Python's "pack_to_scs" iterates through "output_folder" (which is "output_mod/my_mod_name" effectively)
                // and adds files relative to this "output_folder", achieving a flat structure of "def/", "material/", etc. at zip root.
                // ZipFile.CreateFromDirectory(source, dest, level, false) where 'false' is includeBaseDirectory
                // is the correct way to achieve this.
                
                await Task.Run(() =>
                {
                    ZipFile.CreateFromDirectory(
                        sourceDirectoryPath,    // e.g., "output_mod/my_mod_name/"
                        fullOutputScsFilePath,  // e.g., "C:/User/Mods/my_mod_name.scs"
                        compressionLevel,
                        false); // includeBaseDirectory = false: Contents of sourceDirectoryPath become root items in zip.
                });

                return (true, $"Successfully created SCS archive: {fullOutputScsFilePath}", fullOutputScsFilePath);
            }
            catch (System.Exception ex)
            {
                return (false, $"Error creating SCS archive '{fullOutputScsFilePath}': {ex.Message}", null);
            }
        }
    }
}
