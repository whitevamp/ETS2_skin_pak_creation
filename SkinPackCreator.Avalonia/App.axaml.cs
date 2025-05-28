using Avalonia;
using Avalonia.Controls.ApplicationLifetimes;
using Avalonia.Markup.Xaml;
using SkinPackCreator.Avalonia.ViewModels; // Required for MainViewModel
using SkinPackCreator.Avalonia.Views;   // Required for MainWindow

namespace SkinPackCreator.Avalonia
{
    public partial class App : Application
    {
        public override void Initialize()
        {
            AvaloniaXamlLoader.Load(this);
        }

        public override void OnFrameworkInitializationCompleted()
        {
            if (ApplicationLifetime is IClassicDesktopStyleApplicationLifetime desktop)
            {
                desktop.MainWindow = new MainWindow
                {
                    // Create and assign the MainViewModel to the DataContext of MainWindow
                    DataContext = new MainViewModel() 
                };
            }
            else if (ApplicationLifetime is ISingleViewApplicationLifetime singleViewPlatform)
            {
                // This part is for mobile or single-view platforms.
                // While not the primary target, it's good practice to include the structure.
                singleViewPlatform.MainView = new MainWindow // Or potentially a different main view for mobile
                {
                    DataContext = new MainViewModel()
                };
            }
            base.OnFrameworkInitializationCompleted();
        }
    }
}
