using System.IO;
using System.Text;
using System.Threading.Tasks;
using SkinPackCreator.Core.Models; // For ProjectSettings and VehicleType

namespace SkinPackCreator.Core.Builders
{
    public class SuiBuilder
    {
        // Generates content for .sui (accessory_paint_job_data) files.
        // paintJobId: The unique ID for the paint job (e.g., "skin001").
        // vehicleModelName: The internal model name of the vehicle (e.g., "scania.s_2016").
        // vehicleType: Enum to distinguish between Truck and TrailerOwned.
        // settings: ProjectSettings object to access ModName, PaintJobPrefix etc.
        public string BuildAccessoryDataSuiContent(
            string paintJobId,
            string vehicleModelName,
            VehicleType vehicleType,
            ProjectSettings settings)
        {
            if (string.IsNullOrWhiteSpace(paintJobId) || 
                string.IsNullOrWhiteSpace(vehicleModelName) || 
                settings == null)
            {
                // Consider throwing ArgumentNullException for settings or ArgumentException for strings
                return string.Empty; 
            }

            string accessoryInternalName = $"{paintJobId}.{vehicleModelName}.paint_job";
            string suitableForEntry = $""{vehicleModelName}"";
            
            // Extract the numeric/memorable part of paintJobId for UI display
            string paintIdSuffix = paintJobId.StartsWith(settings.PaintJobPrefix) && settings.PaintJobPrefix.Length < paintJobId.Length 
                                   ? paintJobId.Substring(settings.PaintJobPrefix.Length) 
                                   : paintJobId;
            string uiDisplayName = $"{settings.ModName} {paintIdSuffix.ToUpper()}";

            string vehicleTypePath = vehicleType == VehicleType.Truck ? "truck" : "trailer_owned";

            string paintjobTextureBasePath = $"/vehicle/{vehicleTypePath}/upgrade/paintjob/{vehicleModelName}/{paintJobId}/";
            string mainDdsFileName;
            if (vehicleType == VehicleType.Truck)
            {
                mainDdsFileName = $"{paintJobId}_0.dds"; // Truck convention
            }
            else // TrailerOwned
            {
                mainDdsFileName = $"{paintJobId}_shared.dds"; // Trailer convention
            }
            string mainTobjFileName = mainDdsFileName.Replace(".dds", ".tobj");
            string mainTobjPath = paintjobTextureBasePath + mainTobjFileName;

            string uiAccessoryIconPath = $"material/ui/accessory/{paintJobId}_ui_accessory"; // No extension for icon reference

            StringBuilder sb = new StringBuilder();
            sb.AppendLine($"accessory_paint_job_data : {accessoryInternalName}");
            sb.AppendLine("{");
            sb.AppendLine($"	name: "{uiDisplayName}"");
            sb.AppendLine($"	price: {settings.Price}"); // Assuming Price is added to ProjectSettings, default 0
            sb.AppendLine($"	unlock: {settings.UnlockLevel}"); // Assuming UnlockLevel is added, default 0
            sb.AppendLine($"	icon: "{uiAccessoryIconPath}"");
            sb.AppendLine($"	exterior_icon: "{uiAccessoryIconPath}""); // Python used same for both
            sb.AppendLine($"	airbrush: true");
            sb.AppendLine($"	suitable_for[]: {suitableForEntry}");
            
            sb.AppendLine($"	base_color_locked: false"); // Default from Python
            sb.AppendLine($"	base_color: (1.0, 1.0, 1.0)"); // Default white

            if (vehicleType == VehicleType.Truck)
            {
                sb.AppendLine($"	texture_frontal: "{mainTobjPath}"");
                sb.AppendLine($"	texture_frontal_low: "{mainTobjPath}"");
                sb.AppendLine($"	texture_sideral: "{mainTobjPath}"");
                sb.AppendLine($"	texture_sideral_low: "{mainTobjPath}"");
                sb.AppendLine($"	texture_rear: "{mainTobjPath}"");
                sb.AppendLine($"	texture_rear_low: "{mainTobjPath}"");
            }
            else // TrailerOwned
            {
                sb.AppendLine($"	texture: "{mainTobjPath}"");
            }

            sb.AppendLine($"	alternate_uvset: false"); // Default from Python

            // Paths for default override files (metallic, mask)
            string defaultsBasePath = $"/def/vehicle/{vehicleTypePath}/{vehicleModelName}/paint_job/";
            sb.AppendLine($"	defaults[]: "{defaultsBasePath}{paintJobId}_metallic.sui"");
            sb.AppendLine($"	defaults[]: "{defaultsBasePath}{paintJobId}_mask.sui"");

            sb.AppendLine("}");
            return sb.ToString();
        }

        // Asynchronously saves the .sui content to the specified file path.
        public async Task<bool> SaveSuiFileAsync(string suiFilePath, string content)
        {
            if (string.IsNullOrWhiteSpace(suiFilePath) || string.IsNullOrWhiteSpace(content)) return false;
            try
            {
                string? directory = Path.GetDirectoryName(suiFilePath);
                if (directory != null && !Directory.Exists(directory))
                {
                    Directory.CreateDirectory(directory);
                }
                await File.WriteAllTextAsync(suiFilePath, content, new UTF8Encoding(false)); // UTF-8 without BOM
                return true;
            }
            catch (System.Exception ex) // Log or handle ex
            {
                // It's good practice to log the exception message.
                // For now, just returning false as per the existing structure.
                // System.Console.WriteLine($"Error saving SUI file '{suiFilePath}': {ex.Message}");
                return false;
            }
        }

        // Creates empty .sui files for metallic and mask overrides.
        public async Task<bool> CreateEmptyOverrideSuiFileAsync(string suiFilePath)
        {
            if (string.IsNullOrWhiteSpace(suiFilePath)) return false;
            try
            {
                string? directory = Path.GetDirectoryName(suiFilePath);
                if (directory != null && !Directory.Exists(directory))
                {
                    Directory.CreateDirectory(directory);
                }
                // Create an empty file, or a file with a comment indicating its purpose.
                await File.WriteAllTextAsync(suiFilePath, string.Empty, new UTF8Encoding(false));
                return true;
            }
            catch (System.Exception ex) // Log or handle ex
            {
                // System.Console.WriteLine($"Error creating empty SUI file '{suiFilePath}': {ex.Message}");
                return false;
            }
        }
    }
}
