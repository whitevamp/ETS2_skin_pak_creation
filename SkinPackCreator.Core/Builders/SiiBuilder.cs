using System.IO;
using System.Text;
using System.Threading.Tasks;
using SkinPackCreator.Core.Models; // For ProjectSettings and VehicleType

namespace SkinPackCreator.Core.Builders
{
    public class SiiBuilder
    {
        // Generates content for .sii (accessory_addon_data) files.
        // paintJobId: The unique ID for the paint job (e.g., "skin001").
        // vehicleModelName: The internal model name of the vehicle (e.g., "scania.s_2016").
        // vehicleType: Enum to distinguish between Truck and TrailerOwned.
        // settings: ProjectSettings object (currently not directly used for Sii content but good practice for consistency).
        public string BuildAccessoryAddonDataSiiContent(
            string paintJobId,
            string vehicleModelName,
            VehicleType vehicleType,
            ProjectSettings settings) // settings might be used for future extensions
        {
            if (string.IsNullOrWhiteSpace(paintJobId) ||
                string.IsNullOrWhiteSpace(vehicleModelName) ||
                settings == null) // Added null check for settings
            {
                // Consider throwing ArgumentNullException or ArgumentException
                return string.Empty; 
            }

            string accessoryNameFormat = $"{paintJobId}.{vehicleModelName}.paint_job"; 
            string vehicleTypePathString = vehicleType == VehicleType.Truck ? "truck" : "trailer_owned";
            
            // 'look' and 'conflict' names are typically based on the paintjob ID itself.
            string lookIdentifier = paintJobId; 
            string conflictIdentifier = paintJobId;

            string exteriorModelPath;
            if (vehicleType == VehicleType.Truck)
            {
                exteriorModelPath = ""/vehicle/truck/upgrade/paintjob/paintjob.pmd"";
            }
            else // TrailerOwned
            {
                // Simplified logic for trailer exterior models based on keywords in vehicleModelName,
                // mimicking the Python script's conditional assignments.
                if (vehicleModelName.Contains("cistern") || vehicleModelName.Contains("foodtank") || 
                    vehicleModelName.Contains("chemtank") || vehicleModelName.Contains("fueltank") || 
                    vehicleModelName.Contains("gastank") || vehicleModelName.Contains("silo"))
                {
                    exteriorModelPath = ""/vehicle/trailer_owned/upgrade/paintjob/paintjob_cistern.pmd"";
                }
                else if (vehicleModelName.Contains("feldbinder") || vehicleModelName.Contains("eut") || 
                         vehicleModelName.Contains("kip") || vehicleModelName.Contains("tsalm") || 
                         vehicleModelName.Contains("tsaadr"))
                {
                    exteriorModelPath = ""/vehicle/trailer_owned/upgrade/paintjob/paintjob_feldbinder.pmd"";
                }
                else // Default for other ownable trailers (box, curtain, flatbed etc.)
                {
                    exteriorModelPath = ""/vehicle/trailer_owned/upgrade/paintjob/paintjob.pmd"";
                }
            }
            
            string interiorModelPath = "null"; // Paintjobs typically don't have a distinct interior model.

            StringBuilder sb = new StringBuilder();
            sb.AppendLine($"accessory_addon_data : {accessoryNameFormat}");
            sb.AppendLine("{");
            sb.AppendLine($"	look: {lookIdentifier}");
            sb.AppendLine($"	exterior_model: {exteriorModelPath}");
            sb.AppendLine($"	interior_model: {interiorModelPath}");
            
            // The original Python script sometimes adds all *other* paint job IDs as conflicts.
            // For simplicity, and matching one path in the Python script, we make it conflict with itself.
            // This can help group skins or ensure only one from a "set" is chosen if 'look' is shared.
            sb.AppendLine($"	conflicts_with[]: {conflictIdentifier}");

            // Link to the shared .sui file which contains most of the paint job's details.
            string sharedSuiFilePath = $"/def/vehicle/{vehicleTypePathString}/{vehicleModelName}/paint_job/{paintJobId}_shared.sui";
            sb.AppendLine($"	data_path: "{sharedSuiFilePath}"");
            sb.AppendLine("}");

            return sb.ToString();
        }

        // Asynchronously saves the .sii content to the specified file path.
        public async Task<bool> SaveSiiFileAsync(string siiFilePath, string content)
        {
            if (string.IsNullOrWhiteSpace(siiFilePath) || string.IsNullOrWhiteSpace(content)) return false;
            try
            {
                string? directory = Path.GetDirectoryName(siiFilePath);
                if (directory != null && !Directory.Exists(directory))
                {
                    Directory.CreateDirectory(directory);
                }
                await File.WriteAllTextAsync(siiFilePath, content, new UTF8Encoding(false)); // UTF-8 without BOM
                return true;
            }
            catch (System.Exception ex) // Log or handle ex
            {
                return false;
            }
        }
    }
}
