using System.Diagnostics;
using System.IO;
using System.Threading.Tasks; // For async operations

namespace SkinPackCreator.Core.Services
{
    public class TexconvService
    {
        // Runs texconv.exe to convert an image to DDS format.
        // texconvPath: Full path to texconv.exe
        // inputFile: Path to the source image (e.g., PNG)
        // outputDirectory: Directory where the .DDS file will be saved. texconv names the output DDS based on the input file name.
        // ddsFormat: The DDS format (e.g., DXT5, BC7_UNORM)
        // arguments: Optional additional arguments for texconv.
        // Returns a tuple: (bool Success, string OutputMessage with combined stdout/stderr)
        public async Task<(bool Success, string OutputMessage)> RunTexconvAsync(
            string texconvPath, 
            string inputFile, 
            string outputDirectory, 
            string ddsFormat, 
            string? extraArguments = null) // Renamed from 'arguments' to 'extraArguments' for clarity
        {
            if (string.IsNullOrWhiteSpace(texconvPath))
            {
                return (false, "Texconv path is not specified.");
            }
            if (!File.Exists(texconvPath))
            {
                return (false, $"Texconv executable not found at: {texconvPath}");
            }
            if (string.IsNullOrWhiteSpace(inputFile))
            {
                return (false, "Input file for texconv is not specified.");
            }
            if (!File.Exists(inputFile))
            {
                return (false, $"Input file for texconv not found: {inputFile}");
            }
            if (string.IsNullOrWhiteSpace(outputDirectory))
            {
                return (false, "Output directory for texconv is not specified.");
            }

            try
            {
                // Ensure the output directory exists
                if (!Directory.Exists(outputDirectory))
                {
                    Directory.CreateDirectory(outputDirectory);
                }
            }
            catch (System.Exception ex)
            {
                return (false, $"Failed to create or access output directory '{outputDirectory}'. Error: {ex.Message}");
            }

            // Construct arguments for texconv.exe
            // -f <format>: Specify texture format (e.g., DXT5)
            // -m 1: Number of mipmaps to generate (1 means no extra mipmaps beyond the base level, matching Python script)
            // -o <path>: Output directory. texconv will use the source image's name for the output DDS file.
            // -y: Overwrite existing files without prompting.
            // Ensure paths with spaces are quoted.
            string commandArgs = $"-f {ddsFormat} -m 1 -y -o "{outputDirectory}" "{inputFile}"";
            if (!string.IsNullOrWhiteSpace(extraArguments))
            {
                commandArgs += $" {extraArguments}";
            }

            ProcessStartInfo startInfo = new ProcessStartInfo
            {
                FileName = texconvPath,
                Arguments = commandArgs,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true,
                WorkingDirectory = Path.GetDirectoryName(texconvPath) ?? string.Empty // Set working directory if texconv needs related files
            };

            using (Process process = new Process())
            {
                process.StartInfo = startInfo;
                
                try
                {
                    process.Start();
                }
                catch (System.Exception ex)
                {
                    return (false, $"Failed to start texconv process. Path: {texconvPath}. Error: {ex.Message}");
                }

                // Asynchronously read the output and error streams.
                // Use Task.WhenAll to wait for both to complete to avoid deadlocks.
                Task<string> outputReader = process.StandardOutput.ReadToEndAsync();
                Task<string> errorReader = process.StandardError.ReadToEndAsync();
                
                await Task.WhenAll(outputReader, errorReader);
                
                await process.WaitForExitAsync(); // Asynchronously wait for the process to exit.

                string output = outputReader.Result; // Get result after completion
                string error = errorReader.Result;   // Get result after completion

                string messageBuilder = "";

                if (process.ExitCode == 0)
                {
                    messageBuilder = $"Texconv conversion successful for '{Path.GetFileName(inputFile)}'.";
                    if (!string.IsNullOrWhiteSpace(output))
                    {
                        messageBuilder += $"
Output:
{output.Trim()}";
                    }
                    return (true, messageBuilder.Trim());
                }
                else
                {
                    messageBuilder = $"Texconv conversion failed for '{Path.GetFileName(inputFile)}' with exit code {process.ExitCode}.";
                    if (!string.IsNullOrWhiteSpace(output))
                    {
                        messageBuilder += $"
Output:
{output.Trim()}";
                    }
                    if (!string.IsNullOrWhiteSpace(error))
                    {
                        messageBuilder += $"
Errors:
{error.Trim()}";
                    }
                    return (false, messageBuilder.Trim());
                }
            }
        }
    }
}
