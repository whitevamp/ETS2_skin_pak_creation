using SixLabors.ImageSharp; // For Image, Size
using SixLabors.ImageSharp.Processing; // For Mutate, ResizeOptions, ResizeMode
using SixLabors.ImageSharp.Formats.Png; // For SaveAsPngAsync
using SixLabors.ImageSharp.Formats.Jpeg; // Added for JPEG support
using System.IO;
using System.Threading.Tasks;
// No direct dependency on ProjectSettings here, pass necessary parameters.

namespace SkinPackCreator.Core.Services
{
    public class ImageService
    {
        private readonly TexconvService _texconvService;

        public ImageService(TexconvService texconvService)
        {
            _texconvService = texconvService ?? throw new System.ArgumentNullException(nameof(texconvService));
        }

        // Resizes an image and saves it.
        // sourceImagePath: Full path to the source image.
        // outputDirectory: Directory to save the resized image.
        // outputFileNameWithExtension: Name of the resized file, including desired extension (e.g., "icon.jpg", "temp_image.png").
        // resolution: Tuple (Width, Height) for target resolution.
        // Returns: (bool Success, string Message, string? OutputPath)
        public async Task<(bool Success, string Message, string? OutputPath)> ResizeImageAsync(
            string sourceImagePath,
            string outputDirectory,
            string outputFileNameWithExtension, // e.g., "icon.jpg" or "temp_image.png"
            (int Width, int Height) resolution)
        {
            if (string.IsNullOrWhiteSpace(sourceImagePath))
                return (false, "Source image path is not specified.", null);
            if (!File.Exists(sourceImagePath))
                return (false, $"Source image not found: {sourceImagePath}", null);
            if (string.IsNullOrWhiteSpace(outputDirectory))
                return (false, "Output directory for resized image not specified.", null);
            if (string.IsNullOrWhiteSpace(outputFileNameWithExtension))
                return (false, "Output file name for resized image not specified.", null);
            if (resolution.Width <= 0 || resolution.Height <= 0)
                return (false, "Invalid image resolution specified.", null);


            string fullOutputResizedPath = Path.Combine(outputDirectory, outputFileNameWithExtension);

            try
            {
                if (!Directory.Exists(outputDirectory))
                {
                    Directory.CreateDirectory(outputDirectory);
                }

                using (Image image = await Image.LoadAsync(sourceImagePath))
                {
                    image.Mutate(ctx => ctx.Resize(new ResizeOptions
                    {
                        Size = new Size(resolution.Width, resolution.Height),
                        // Consider LanczosResample for high quality. Stretch is used for simplicity
                        // if aspect ratio doesn't need to be strictly preserved or if original aspect is unknown.
                        Mode = ResizeMode.Stretch 
                    }));

                    string extension = Path.GetExtension(outputFileNameWithExtension).ToLowerInvariant();
                    if (extension == ".jpg" || extension == ".jpeg")
                    {
                        await image.SaveAsJpegAsync(fullOutputResizedPath, new JpegEncoder { Quality = 90 }); // Example quality
                    }
                    else // Default to PNG
                    {
                        await image.SaveAsPngAsync(fullOutputResizedPath, new PngEncoder { CompressionLevel = PngCompressionLevel.DefaultCompression });
                    }
                }
                return (true, $"Image '{Path.GetFileName(sourceImagePath)}' processed as '{outputFileNameWithExtension}' to {resolution.Width}x{resolution.Height} and saved to '{fullOutputResizedPath}'.", fullOutputResizedPath);
            }
            catch (System.Exception ex)
            {
                return (false, $"Error processing image '{Path.GetFileName(sourceImagePath)}' to '{outputFileNameWithExtension}': {ex.Message}", null);
            }
        }

        // Converts a source image (typically PNG) to DDS using TexconvService.
        // sourcePngPath: Path to the (possibly resized) PNG input.
        // outputDdsDirectory: Directory where the DDS should be placed.
        // texconvPath: Full path to texconv.exe.
        // ddsFormat: DDS format string (e.g., "DXT5").
        // ensureLowercaseExtension: If true, renames .DDS to .dds if necessary.
        // Returns: (bool Success, string Message, string? DdsPath)
        public async Task<(bool Success, string Message, string? DdsPath)> ConvertToDdsAsync(
            string sourcePngPath,
            string outputDdsDirectory,
            string texconvPath,
            string ddsFormat,
            bool ensureLowercaseExtension = false)
        {
            if (string.IsNullOrWhiteSpace(sourcePngPath))
                return (false, "Source PNG for DDS conversion is not specified.", null);
            if (!File.Exists(sourcePngPath))
                return (false, $"Source PNG for DDS conversion not found: {sourcePngPath}", null);
            if (string.IsNullOrWhiteSpace(outputDdsDirectory))
                return (false, "Output directory for DDS file not specified.", null);
            if (string.IsNullOrWhiteSpace(texconvPath))
                 return (false, "Texconv path not specified for DDS conversion.", null);
            if (string.IsNullOrWhiteSpace(ddsFormat))
                 return (false, "DDS format not specified for DDS conversion.", null);
            
            // Output DDS filename will be based on the source PNG filename
            string baseFileName = Path.GetFileNameWithoutExtension(sourcePngPath);
            string ddsFileNameWithUppercaseExt = baseFileName + ".DDS"; // Default expected output from some texconv versions
            string ddsFileNameWithLowercaseExt = baseFileName + ".dds"; // Desired final name if ensureLowercaseExtension is true

            // Texconv will place the file in outputDdsDirectory.
            // The actual name (case of extension) might vary.
            var (texconvSuccess, texconvMessage) = await _texconvService.RunTexconvAsync(
                texconvPath,
                sourcePngPath,
                outputDdsDirectory,
                ddsFormat);

            if (!texconvSuccess)
            {
                return (false, $"DDS conversion failed. Texconv output: {texconvMessage}", null);
            }
            
            // Determine the actual path of the output file from texconv
            string createdDdsPathOriginalCase = Path.Combine(outputDdsDirectory, ddsFileNameWithUppercaseExt);
            string createdDdsPathLowercase = Path.Combine(outputDdsDirectory, ddsFileNameWithLowercaseExt);
            string actualCreatedDdsPath = "";

            if (File.Exists(createdDdsPathOriginalCase)) 
            {
                actualCreatedDdsPath = createdDdsPathOriginalCase;
            } 
            else if (File.Exists(createdDdsPathLowercase)) 
            {
                actualCreatedDdsPath = createdDdsPathLowercase;
            }

            if (string.IsNullOrEmpty(actualCreatedDdsPath))
            {
                 return (false, $"DDS conversion by texconv seemed to succeed, but the output file (expected {ddsFileNameWithUppercaseExt} or {ddsFileNameWithLowercaseExt}) was not found in '{outputDdsDirectory}'. Texconv message: {texconvMessage}", null);
            }

            // If lowercase extension is required and the file isn't already lowercase
            if (ensureLowercaseExtension && Path.GetExtension(actualCreatedDdsPath).Equals(".DDS", System.StringComparison.Ordinal))
            {
                string targetLowercasePath = Path.Combine(outputDdsDirectory, ddsFileNameWithLowercaseExt);
                try
                {
                    File.Move(actualCreatedDdsPath, targetLowercasePath, true); // Overwrite if target exists (e.g. case-insensitive FS)
                    return (true, $"DDS successfully created and renamed to lowercase extension: {targetLowercasePath}. Texconv: {texconvMessage}", targetLowercasePath);
                }
                catch (IOException ex)
                {
                    // If rename fails, still return success but with the original path and an error message for the rename.
                    return (true, $"DDS created at '{actualCreatedDdsPath}', but failed to rename to lowercase extension: {ex.Message}. Texconv: {texconvMessage}", actualCreatedDdsPath);
                }
            }

            // If no rename was needed or ensureLowercaseExtension was false
            return (true, $"DDS successfully created: {actualCreatedDdsPath}. Texconv: {texconvMessage}", actualCreatedDdsPath);
        }
    }
}
