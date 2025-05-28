using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography; // For RandomNumberGenerator
using System.Text;
using System.Threading.Tasks;
using SkinPackCreator.Core.Models;
using SkinPackCreator.Core.Services;
using SkinPackCreator.Core.Builders;

namespace SkinPackCreator.Core
{
    public class ModProcessor
    {
        private readonly ImageService _imageService;
        private readonly TobjBuilder _tobjBuilder;
        private readonly MatBuilder _matBuilder;
        private readonly SuiBuilder _suiBuilder;
        private readonly SiiBuilder _siiBuilder;
        private readonly MetadataGenerator _metadataGenerator;
        private readonly ScsArchiver _scsArchiver;

        public ModProcessor(
            ImageService imageService,
            TobjBuilder tobjBuilder,
            MatBuilder matBuilder,
            SuiBuilder suiBuilder,
            SiiBuilder siiBuilder,
            MetadataGenerator metadataGenerator,
            ScsArchiver scsArchiver)
        {
            _imageService = imageService ?? throw new ArgumentNullException(nameof(imageService));
            _tobjBuilder = tobjBuilder ?? throw new ArgumentNullException(nameof(tobjBuilder));
            _matBuilder = matBuilder ?? throw new ArgumentNullException(nameof(matBuilder));
            _suiBuilder = suiBuilder ?? throw new ArgumentNullException(nameof(suiBuilder));
            _siiBuilder = siiBuilder ?? throw new ArgumentNullException(nameof(siiBuilder));
            _metadataGenerator = metadataGenerator ?? throw new ArgumentNullException(nameof(metadataGenerator));
            _scsArchiver = scsArchiver ?? throw new ArgumentNullException(nameof(scsArchiver));
        }

        private string GenerateUniquePaintId(ProjectSettings settings, HashSet<string> existingIds)
        {
            string id;
            int attempts = 0; // Prevent infinite loop in extremely unlikely scenario
            do
            {
                byte[] randomBytes = new byte[2]; // For up to 65535
                RandomNumberGenerator.GetBytes(randomBytes);
                int randomNumber = BitConverter.ToUInt16(randomBytes, 0) % 10000; // 0-9999
                id = $"{settings.PaintJobPrefix}{randomNumber:D4}"; // e.g., skin0000
                attempts++;
            } while (existingIds.Contains(id) && attempts < 100000); // Allow many attempts

            if (existingIds.Contains(id)) // Highly unlikely if prefix unique enough or few items
            {
                // Fallback if somehow still colliding after many attempts
                id = $"{settings.PaintJobPrefix}{Guid.NewGuid().ToString().Substring(0, 4)}";
            }
            existingIds.Add(id);
            return id;
        }

        public async Task<(bool Success, List<string> LogMessages)> GenerateModAsync(ProjectSettings settings, List<string> sourceImagePaths)
        {
            var logMessages = new List<string>();

            // --- Initial Validations ---
            if (settings == null) { logMessages.Add("Error: Project settings are null."); return (false, logMessages); }
            if (string.IsNullOrWhiteSpace(settings.OutputDirectory)) { logMessages.Add("Error: Output directory is not set."); return (false, logMessages); }
            if (string.IsNullOrWhiteSpace(settings.TexconvPath)) { logMessages.Add("Error: Texconv path is not set."); return (false, logMessages); }
            if (!File.Exists(settings.TexconvPath)) { logMessages.Add($"Error: texconv.exe not found at '{settings.TexconvPath}'."); return (false, logMessages); }
            if (sourceImagePaths == null || !sourceImagePaths.Any() || sourceImagePaths.All(string.IsNullOrWhiteSpace)) { logMessages.Add("Error: No valid source images provided."); return (false, logMessages); }

            logMessages.Add("Mod generation process started...");
            try { settings.CreateOutputDirectories(); }
            catch (Exception ex) { logMessages.Add($"Error creating output directories: {ex.Message}"); return (false, logMessages); }
            logMessages.Add($"Base output structure at: {settings.FullOutputDirectoryPath}");
            logMessages.Add($"Temporary files in: {settings.TempDirectoryPath}");

            var generatedPaintIds = new HashSet<string>();

            // --- 1. Process each source image ---
            foreach (string sourceImagePath in sourceImagePaths.Where(p => !string.IsNullOrWhiteSpace(p)))
            {
                if (!File.Exists(sourceImagePath)) { logMessages.Add($"Warning: Source image '{sourceImagePath}' not found. Skipping."); continue; }

                string paintId = GenerateUniquePaintId(settings, generatedPaintIds);
                logMessages.Add($"--- Processing image '{Path.GetFileName(sourceImagePath)}' as Paint ID: '{paintId}' ---");

                // 1a. Resize master image (PNG for DDS source)
                string resizedMasterImageName = $"{paintId}.png";
                var (resizeMasterOk, resizeMasterMsg, resizedMasterPath) = await _imageService.ResizeImageAsync(sourceImagePath, settings.TempDirectoryPath, resizedMasterImageName, settings.MainImageResolution);
                logMessages.Add($"  {resizeMasterMsg}");
                if (!resizeMasterOk || resizedMasterPath == null) { logMessages.Add($"  Skipping '{paintId}' due to master resize failure."); continue; }

                // 1b. UI Accessory Assets
                logMessages.Add($"  Generating UI assets for '{paintId}'...");
                string uiAccessoryBaseName = $"{paintId}_ui_accessory";
                string uiAccessoryResizedPngName = $"{uiAccessoryBaseName}.png";
                var (resizeUiOk, resizeUiMsg, resizedUiPngPath) = await _imageService.ResizeImageAsync(resizedMasterPath, settings.TempDirectoryPath, uiAccessoryResizedPngName, settings.UiAccessoryResolution);
                logMessages.Add($"    {resizeUiMsg}");
                if (!resizeUiOk || resizedUiPngPath == null) { logMessages.Add($"    Skipping UI assets for '{paintId}' due to UI resize failure."); continue; }

                var (uiDdsOk, uiDdsMsg, uiDdsPath) = await _imageService.ConvertToDdsAsync(resizedUiPngPath, settings.UiAccessoryMaterialPath, settings.TexconvPath, settings.DdsFormat, true);
                logMessages.Add($"    {uiDdsMsg}");
                if (!uiDdsOk || uiDdsPath == null) { logMessages.Add($"    Skipping UI assets for '{paintId}' due to DDS conversion failure."); continue; }

                string uiTobjContent = _tobjBuilder.BuildTobjContent($"/material/ui/accessory/{Path.GetFileName(uiDdsPath)}"); // Game path
                if (!await _tobjBuilder.SaveTobjFileAsync(Path.Combine(settings.UiAccessoryMaterialPath, $"{uiAccessoryBaseName}.tobj"), uiTobjContent)) { logMessages.Add($"    Error: Failed to save UI TOBJ for {uiAccessoryBaseName}. Skipping further UI assets."); continue; }
                logMessages.Add($"    UI TOBJ for '{uiAccessoryBaseName}' created.");
                
                string uiMatContent = _matBuilder.BuildUiMatContent(uiAccessoryBaseName);
                if (!await _matBuilder.SaveMatFileAsync(Path.Combine(settings.UiAccessoryMaterialPath, $"{uiAccessoryBaseName}.mat"), uiMatContent)) { logMessages.Add($"    Error: Failed to save UI MAT for {uiAccessoryBaseName}."); continue; }
                logMessages.Add($"    UI MAT for '{uiAccessoryBaseName}' created.");

                // 1c. Process Vehicles
                var vehiclesToProcess = settings.SelectedTrucks.Select(vt => DefaultVehicles.AllTrucks.FirstOrDefault(t => t.InternalName == vt && t.Type == VehicleType.Truck))
                    .Concat(settings.SelectedTrailers.Select(vtr => DefaultVehicles.AllTrailers.FirstOrDefault(tr => tr.InternalName == vtr && tr.Type == VehicleType.TrailerOwned)))
                    .Where(v => v != null).Distinct().ToList(); // Added Distinct()
                
                if (!vehiclesToProcess.Any()) logMessages.Add($"  Warning: No valid trucks or trailers selected/found for '{paintId}'.");

                foreach (var vehicleDef in vehiclesToProcess)
                {
                    logMessages.Add($"    Processing for vehicle: {vehicleDef.DisplayName} ({vehicleDef.InternalName})");
                    string vehiclePaintJobDir = Path.Combine(vehicleDef.Type == VehicleType.Truck ? settings.TruckPaintJobBasePath : settings.TrailerPaintJobBasePath, vehicleDef.InternalName, paintId);
                    string vehicleDefDir = Path.Combine(vehicleDef.Type == VehicleType.Truck ? settings.TruckDefBasePath : settings.TrailerDefBasePath, vehicleDef.InternalName, "paint_job");
                    Directory.CreateDirectory(vehiclePaintJobDir); // Ensure specific model/paintId subfolder exists
                    Directory.CreateDirectory(vehicleDefDir);    // Ensure specific model/paint_job subfolder exists

                    string ddsBaseFileNameOnDisk = vehicleDef.Type == VehicleType.Truck ? $"{paintId}_0" : $"{paintId}_shared";
                    string ddsFileNameOnDisk = ddsBaseFileNameOnDisk + ".dds";
                    string tobjFileNameOnDisk = ddsBaseFileNameOnDisk + ".tobj";
                    
                    // Path for TOBJ's internal texture reference
                    string ddsTexturePathInTobj = $"/vehicle/{(vehicleDef.Type == VehicleType.Truck ? "truck" : "trailer_owned")}/upgrade/paintjob/{vehicleDef.InternalName}/{paintId}/{(vehicleDef.Type == VehicleType.Truck ? $"{paintId}_0..dds" : ddsFileNameOnDisk)}";
                    
                    var (vehDdsOk, vehDdsMsg, vehDdsDiskPath) = await _imageService.ConvertToDdsAsync(resizedMasterPath, vehiclePaintJobDir, settings.TexconvPath, settings.DdsFormat, false);
                    logMessages.Add($"      {vehDdsMsg}");
                    if (!vehDdsOk || vehDdsDiskPath == null) { logMessages.Add($"      Skipping DDS for {vehicleDef.InternalName}/{paintId}."); continue; }

                    // Rename if texconv output name (e.g. paintId.DDS) differs from desired disk name (e.g. paintId_0.dds)
                    string finalDdsPathOnDisk = Path.Combine(vehiclePaintJobDir, ddsFileNameOnDisk);
                    if (Path.GetFullPath(vehDdsDiskPath) != Path.GetFullPath(finalDdsPathOnDisk) && File.Exists(vehDdsDiskPath)) {
                        try { File.Move(vehDdsDiskPath, finalDdsPathOnDisk, true); logMessages.Add($"      Renamed '{Path.GetFileName(vehDdsDiskPath)}' to '{ddsFileNameOnDisk}'."); vehDdsDiskPath = finalDdsPathOnDisk; }
                        catch (IOException ex) { logMessages.Add($"      Warning: Could not rename '{Path.GetFileName(vehDdsDiskPath)}' to '{ddsFileNameOnDisk}': {ex.Message}"); }
                    }
                    
                    string vehTobjContent = _tobjBuilder.BuildTobjContent(ddsTexturePathInTobj);
                    if (!await _tobjBuilder.SaveTobjFileAsync(Path.Combine(vehiclePaintJobDir, tobjFileNameOnDisk), vehTobjContent)) { logMessages.Add($"      Error: Failed to save TOBJ for {vehicleDef.InternalName}/{paintId}."); continue; }
                    logMessages.Add($"      TOBJ for {vehicleDef.InternalName}/{paintId} created.");

                    string suiContent = _suiBuilder.BuildAccessoryDataSuiContent(paintId, vehicleDef.InternalName, vehicleDef.Type, settings);
                    if (!await _suiBuilder.SaveSuiFileAsync(Path.Combine(vehicleDefDir, $"{paintId}_shared.sui"), suiContent)) { logMessages.Add($"      Error: Failed to save _shared.sui for {vehicleDef.InternalName}/{paintId}."); continue; }
                    logMessages.Add($"      _shared.sui for {vehicleDef.InternalName}/{paintId} created.");

                    string siiContent = _siiBuilder.BuildAccessoryAddonDataSiiContent(paintId, vehicleDef.InternalName, vehicleDef.Type, settings);
                    if (!await _siiBuilder.SaveSiiFileAsync(Path.Combine(vehicleDefDir, $"{paintId}.sii"), siiContent)) { logMessages.Add($"      Error: Failed to save .sii for {vehicleDef.InternalName}/{paintId}."); continue; }
                    logMessages.Add($"      .sii for {vehicleDef.InternalName}/{paintId} created.");

                    await _suiBuilder.CreateEmptyOverrideSuiFileAsync(Path.Combine(vehicleDefDir, $"{paintId}_metallic.sui"));
                    await _suiBuilder.CreateEmptyOverrideSuiFileAsync(Path.Combine(vehicleDefDir, $"{paintId}_mask.sui"));
                    logMessages.Add($"      Empty metallic/mask SUI stubs for {vehicleDef.InternalName}/{paintId} created.");
                }
                logMessages.Add($"--- Finished processing for Paint ID: '{paintId}' ---");
            }

            // --- 2. Generate Mod Icon ---
            var firstValidSourceImage = sourceImagePaths.FirstOrDefault(p => !string.IsNullOrWhiteSpace(p) && File.Exists(p));
            if (firstValidSourceImage != null)
            {
                logMessages.Add("Generating mod icon...");
                // Assuming ModIconFileName in settings is e.g. "mod_icon.jpg" or "mod_icon.png"
                // ResizeImageAsync saves as PNG. If JPG is needed, ImageService needs adjustment or a different method.
                var (iconOk, iconMsg, iconPath) = await _imageService.ResizeImageAsync(firstValidSourceImage, settings.RootModFilesPath, settings.ModIconFileName, (276, 162));
                logMessages.Add($"  {iconMsg}");
                if (!iconOk) logMessages.Add("  Warning: Mod icon generation failed.");
                // If ImageService saves as PNG, and ModIconFileName is .jpg, this will be problematic.
                // For now, assuming ModIconFileName matches ImageService output type (PNG) or ImageService is flexible.
            } else { logMessages.Add("Skipping mod icon generation (no valid source image)."); }

            // --- 3. Generate Manifest and Description ---
            logMessages.Add("Generating manifest.sii and mod_description.txt...");
            string manifestContent = _metadataGenerator.BuildManifestSiiContent(settings);
            await _metadataGenerator.SaveManifestFileAsync(Path.Combine(settings.RootModFilesPath, "manifest.sii"), manifestContent);
            string descContent = _metadataGenerator.BuildModDescriptionContent(settings);
            await _metadataGenerator.SaveDescriptionFileAsync(Path.Combine(settings.RootModFilesPath, "mod_description.txt"), descContent);
            logMessages.Add("Manifest and description files generated.");

            // --- 4. Pack to SCS archive (if requested) ---
            if (settings.PackToScsArchive)
            {
                string scsFileName = settings.OutputModFolderName + ".scs";
                logMessages.Add($"Packaging mod into SCS archive: {scsFileName}");
                var (packOk, packMsg, scsPath) = await _scsArchiver.PackDirectoryToScsAsync(settings.FullOutputDirectoryPath, settings.OutputDirectory, scsFileName);
                logMessages.Add($"  {packMsg}");
                if(packOk) logMessages.Add($"  SCS Archive created at: {scsPath}"); else logMessages.Add("  Error: SCS packaging failed.");
            } else { logMessages.Add("SCS archive generation skipped as per settings."); }

            logMessages.Add("Mod generation process finished.");
            return (true, logMessages); // Overall success true, errors are in logs. Could refine to return false if critical errors.
        }
    }
}
