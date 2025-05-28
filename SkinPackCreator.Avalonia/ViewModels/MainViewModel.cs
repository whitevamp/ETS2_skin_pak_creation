using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
// using System.Windows.Input; // No longer strictly needed as RelayCommand is used
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Avalonia; // Added
using Avalonia.Controls.ApplicationLifetimes; // Added
using Avalonia.Platform.Storage; // Added
using SkinPackCreator.Core;
using SkinPackCreator.Core.Models;
using SkinPackCreator.Core.Services;
using SkinPackCreator.Core.Builders;
// Avalonia specific dialogs will be handled by the View layer or a dedicated dialog service later.

namespace SkinPackCreator.Avalonia.ViewModels
{
    // Small ViewModel for displaying vehicles in lists with selection
    public partial class VehicleViewModel : ObservableObject
    {
        private readonly VehicleDefinition _definition;

        public string InternalName => _definition.InternalName;
        public string DisplayName => _definition.DisplayName;
        public VehicleType Type => _definition.Type;

        [ObservableProperty]
        private bool _isSelected;

        public VehicleViewModel(VehicleDefinition definition)
        {
            _definition = definition ?? throw new ArgumentNullException(nameof(definition));
            _isSelected = false; // Default to not selected
        }
    }

    public partial class MainViewModel : ObservableObject
    {
        [ObservableProperty]
        [NotifyCanExecuteChangedFor(nameof(GenerateModCommand))]
        private string? _inputImagePath;

        [ObservableProperty]
        [NotifyCanExecuteChangedFor(nameof(GenerateModCommand))]
        private string? _outputDirectory;

        [ObservableProperty]
        [NotifyCanExecuteChangedFor(nameof(GenerateModCommand))]
        private string? _texconvPath;

        [ObservableProperty]
        private string _modName = "My Custom Skin";

        [ObservableProperty]
        private string _modAuthor = "Skin Creator User";

        [ObservableProperty]
        private string _modVersion = "1.0";

        [ObservableProperty]
        private string _modDescription = "A cool skin pack.";
        
        [ObservableProperty]
        private string _paintJobPrefix = "skin";

        [ObservableProperty]
        private bool _packToScsArchive = true;

        [ObservableProperty]
        private string _ddsFormat = "DXT5";

        [ObservableProperty]
        private int _mainImageWidth = 4096;
        [ObservableProperty]
        private int _mainImageHeight = 4096;

        [ObservableProperty]
        private int _uiAccessoryWidth = 256;
        [ObservableProperty]
        private int _uiAccessoryHeight = 256;
        
        [ObservableProperty]
        private int _price = 0;

        [ObservableProperty]
        private int _unlockLevel = 0;

        [ObservableProperty]
        private string _logOutput = string.Empty;

        [ObservableProperty]
        [NotifyCanExecuteChangedFor(nameof(GenerateModCommand))]
        private bool _isBusy = false;

        public ObservableCollection<VehicleViewModel> AllTrucks { get; } = new();
        public ObservableCollection<VehicleViewModel> AllTrailers { get; } = new();

        private readonly ModProcessor _modProcessor;
        // Placeholder for a dialog service, to be implemented/injected later
        // public IUIDialogService DialogService { get; set; }
        
        // Helper method to get TopLevel for StorageProvider
        private TopLevel? GetTopLevel()
        {
            if (Application.Current?.ApplicationLifetime is IClassicDesktopStyleApplicationLifetime desktopApp)
            {
                return desktopApp.MainWindow; // Or desktopApp.Windows.FirstOrDefault(w => w.IsActive);
            }
            // Handle other lifetimes or return null if not found
            // For ISingleViewApplicationLifetime, it might be (Application.Current.ApplicationLifetime as ISingleViewApplicationLifetime)?.MainView as TopLevel
            return null;
        }

        public IAsyncRelayCommand SelectInputImagePathCommand { get; }
        public IAsyncRelayCommand SelectOutputDirectoryCommand { get; }
        public IAsyncRelayCommand SelectTexconvPathCommand { get; }
        public IAsyncRelayCommand GenerateModCommand { get; }

        public MainViewModel() // Dependencies like dialog service would be injected here
        {
            LoadVehicleLists();

            SelectInputImagePathCommand = new AsyncRelayCommand(SelectInputImagePathAsync);
            SelectOutputDirectoryCommand = new AsyncRelayCommand(SelectOutputDirectoryAsync);
            SelectTexconvPathCommand = new AsyncRelayCommand(SelectTexconvPathAsync);
            GenerateModCommand = new AsyncRelayCommand(GenerateModAsyncExecute, CanGenerateMod);

            // Simplified DI for now: direct instantiation of core services and processor
            var texconvService = new TexconvService();
            var imageService = new ImageService(texconvService);
            var tobjBuilder = new TobjBuilder();
            var matBuilder = new MatBuilder();
            var suiBuilder = new SuiBuilder();
            var siiBuilder = new SiiBuilder();
            var metadataGenerator = new MetadataGenerator();
            var scsArchiver = new ScsArchiver();
            
            _modProcessor = new ModProcessor(imageService, tobjBuilder, matBuilder, suiBuilder, siiBuilder, metadataGenerator, scsArchiver);
        }

        private void LoadVehicleLists()
        {
            AllTrucks.Clear();
            DefaultVehicles.AllTrucks.ForEach(truck => AllTrucks.Add(new VehicleViewModel(truck)));
            AllTrailers.Clear();
            DefaultVehicles.AllTrailers.ForEach(trailer => AllTrailers.Add(new VehicleViewModel(trailer)));
        }
        
        // --- Command Implementations (Dialogs are placeholders) ---
        private async Task SelectInputImagePathAsync()
        {
            var topLevel = GetTopLevel();
            if (topLevel == null) { LogOutput += "Error: Could not get TopLevel for dialog.\n"; return; }

            var files = await topLevel.StorageProvider.OpenFilePickerAsync(new FilePickerOpenOptions
            {
                Title = "Select Input Image",
                AllowMultiple = false,
                FileTypeFilter = new[] { FilePickerFileTypes.ImagePng, FilePickerFileTypes.ImageJpg }
            });

            if (files.Any() && files[0].TryGetLocalPath() is string path)
            {
                InputImagePath = path;
                LogOutput += $"Input image selected: {InputImagePath}\n";
            }
            else
            {
                LogOutput += "No input image selected.\n";
            }
        }

        private async Task SelectOutputDirectoryAsync()
        {
            var topLevel = GetTopLevel();
            if (topLevel == null) { LogOutput += "Error: Could not get TopLevel for dialog.\n"; return; }

            var folders = await topLevel.StorageProvider.OpenFolderPickerAsync(new FolderPickerOpenOptions
            {
                Title = "Select Output Directory",
                AllowMultiple = false
            });

            if (folders.Any() && folders[0].TryGetLocalPath() is string path)
            {
                OutputDirectory = path;
                LogOutput += $"Output directory selected: {OutputDirectory}\n";
            }
            else
            {
                LogOutput += "No output directory selected.\n";
            }
        }

        private async Task SelectTexconvPathAsync()
        {
            var topLevel = GetTopLevel();
            if (topLevel == null) { LogOutput += "Error: Could not get TopLevel for dialog.\n"; return; }
            
            var files = await topLevel.StorageProvider.OpenFilePickerAsync(new FilePickerOpenOptions
            {
                Title = "Select texconv.exe",
                AllowMultiple = false,
                FileTypeFilter = new[]
                {
                    new FilePickerFileType("Executable") { Patterns = new[] { "*.exe" } },
                    FilePickerFileTypes.All // Allow all if user needs to select it without extension on some OS
                }
            });

            if (files.Any() && files[0].TryGetLocalPath() is string path)
            {
                TexconvPath = path;
                LogOutput += $"texconv.exe selected: {TexconvPath}\n";
            }
            else
            {
                LogOutput += "No texconv.exe selected.\n";
            }
        }

        private bool CanGenerateMod()
        {
            return !IsBusy &&
                   !string.IsNullOrWhiteSpace(InputImagePath) && 
                   File.Exists(InputImagePath) && // Check if file actually exists
                   !string.IsNullOrWhiteSpace(OutputDirectory) &&
                   Directory.Exists(OutputDirectory) && // Check if directory actually exists
                   !string.IsNullOrWhiteSpace(TexconvPath) &&
                   File.Exists(TexconvPath); // Crucial check
        }

        private async Task GenerateModAsyncExecute()
        {
            LogOutput = string.Empty; // Clear logs
            IsBusy = true;
            LogOutput += "Starting mod generation...\n";

            var settings = new ProjectSettings
            {
                InputImagePath = this.InputImagePath, // Assuming single image path from UI
                OutputDirectory = this.OutputDirectory,
                TexconvPath = this.TexconvPath,
                ModName = this.ModName,
                ModAuthor = this.ModAuthor,
                ModVersion = this.ModVersion,
                ModDescription = this.ModDescription,
                PaintJobPrefix = this.PaintJobPrefix,
                PackToScsArchive = this.PackToScsArchive,
                DdsFormat = this.DdsFormat,
                MainImageResolution = (this.MainImageWidth, this.MainImageHeight),
                UiAccessoryResolution = (this.UiAccessoryWidth, this.UiAccessoryHeight),
                Price = this.Price,
                UnlockLevel = this.UnlockLevel,
                SelectedTrucks = AllTrucks.Where(v => v.IsSelected).Select(v => v.InternalName).ToList(),
                SelectedTrailers = AllTrailers.Where(v => v.IsSelected).Select(v => v.InternalName).ToList(),
                ModIconFileName = "mod_icon.png" // Defaulting to PNG. If ImageService changes to save icon as JPG, update this.
            };
            
            // Validate paths before proceeding
            if (string.IsNullOrWhiteSpace(settings.InputImagePath) || !File.Exists(settings.InputImagePath))
            {
                LogOutput += "Error: Input image path is invalid or file does not exist. Please select a valid image.\n";
                IsBusy = false;
                return;
            }
            if (string.IsNullOrWhiteSpace(settings.OutputDirectory) || !Directory.Exists(settings.OutputDirectory))
            {
                LogOutput += "Error: Output directory is invalid or does not exist. Please select a valid directory.\n";
                IsBusy = false;
                return;
            }
             if (string.IsNullOrWhiteSpace(settings.TexconvPath) || !File.Exists(settings.TexconvPath))
            {
                LogOutput += "Error: Texconv path is invalid or file does not exist. Please select a valid texconv.exe.\n";
                IsBusy = false;
                return;
            }

            var imagePaths = new List<string> { settings.InputImagePath }; // Already validated

            var (success, logs) = await _modProcessor.GenerateModAsync(settings, imagePaths);

            foreach (var log in logs) { LogOutput += $"{log}\n"; }
            LogOutput += success ? "Mod generation process completed successfully!\n" : "Mod generation process finished with errors or warnings (check log).\n";
            IsBusy = false;
        }
    }
}
