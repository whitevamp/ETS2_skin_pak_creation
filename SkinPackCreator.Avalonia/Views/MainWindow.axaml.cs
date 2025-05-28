using Avalonia.Controls;

namespace SkinPackCreator.Avalonia.Views
{
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();
            // ViewModel instantiation and setting DataContext can also be done here
            // if not handled in App.axaml.cs or by a view locator.
            // For simplicity with current setup, MainViewModel is instantiated in XAML's Design.DataContext
            // and should be instantiated by the application's startup logic (e.g., App.axaml.cs) for runtime.
        }
    }
}
