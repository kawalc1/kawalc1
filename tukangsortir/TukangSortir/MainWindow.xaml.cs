using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;
using System.IO;
using Path = System.IO.Path;

namespace TukangSortir
{

    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        public static int NumberOfNumbers = 12;
        private String enteredKey;
        private MainModel model = new MainModel();
        static EventWaitHandle _waitKeyHandle = new AutoResetEvent(false);

        private string sourceDir = "resources";
        private string targetDir = "numbers";
        private string processedScans = "processed";
        private string specialScans = "special";

        public MainWindow()
        {
            InitializeComponent();
            DataContext = model;
            model.NumberClassified = 0;
       }


        private void windowLoaded(object sender, RoutedEventArgs e)
        {
            this.KeyDown += new KeyEventHandler(KeyPressed);
            doNext();
        }

        private void doNext() {
            string[] filePaths = Directory.GetFiles(sourceDir+"/", "*.jpg");
            if (filePaths.Length == 0) {
                MessageBox.Show("Empty/Habis/Opperdepop! Request another batch");
                Application.Current.Shutdown();
                Environment.Exit(0);
            }
            string currentfile = filePaths[0];
            model.SetImageData(currentfile);
            AdornNumber(model.NumberClassified);
            File.Move(currentfile, System.IO.Path.Combine(processedScans, System.IO.Path.GetFileName(currentfile)));
        }

        private void KeyPressed(object sender, KeyEventArgs e)
        {
            enteredKey = e.Key.ToString();
            int enteredNumber;
            if (int.TryParse(enteredKey.Substring(enteredKey.Length - 1, 1), out enteredNumber))
            {
                MoveNumber("" + enteredNumber);
            }
            else if (enteredKey == "W" || enteredKey == "X" || enteredKey == "D" || enteredKey == "S")
            {
                MoveNumber(enteredKey);
            }
            else
            {
                return;
            }

            model.NumberClassified += 1;
            if (model.NumberClassified % NumberOfNumbers == 0)
            {
                doNext();
            }
            AdornNumber(model.NumberClassified);
        }

        private void MoveNumber(string pressedKey)
        {
            if (pressedKey == "S")
            {
                StatusBar.Content = "Skipped.";
                return;
            }
            string currentTif = model.getTif(model.NumberClassified);
            string classifiedTif = Path.GetFileNameWithoutExtension(currentTif) + "~class~" + pressedKey + Path.GetExtension(currentTif);
            StatusBar.Content = "Moving to: '" + pressedKey + "' folder";
            if (File.Exists(currentTif))
            {
                var destination = System.IO.Path.Combine(targetDir, pressedKey.ToLower(), Path.GetFileName(classifiedTif));
                File.Move(currentTif, destination);
                File.SetCreationTime(destination, DateTime.Now);
                File.SetLastWriteTime(destination, DateTime.Now);
                File.SetLastWriteTime(destination, DateTime.Now);
            }
        }

        private void AdornNumber(int num)
        {
            int ord = num % 12;
            var element = GetElement(ord);
            element.Stroke = new SolidColorBrush(Colors.Red);

            if (num == 0)
            {
                return;
            }
            int previousOrd = (num - 1) % 12;
            var previousElement = GetElement(previousOrd);
            previousElement.Stroke = new SolidColorBrush(Colors.Transparent);
            
        }

        private Rectangle GetElement(int ord)
        {
            return (Rectangle)ImageGrid.Children.Cast<UIElement>().Single<UIElement>(i => Grid.GetRow(i) == ord / 3 && Grid.GetColumn(i) == ord % 3);
        }

        private void SpecialButton_Click(object sender, RoutedEventArgs e)
        {
            string fileName = System.IO.Path.GetFileName(model.CurrentJpeg);
            File.Copy(System.IO.Path.Combine(processedScans, fileName), System.IO.Path.Combine(specialScans, fileName));
            MessageBox.Show("Special case has been saved!");
        }

        private void Show_Instructions_Click(object sender, RoutedEventArgs e)
        {
            var window = new Instructions();
            window.Show();
        }

    }
    class MainModel : INotifyPropertyChanged
    {
        public event PropertyChangedEventHandler PropertyChanged;
        private ImageSource _formImage;
        private List<NumberImageType> _numberImages;
        private int _numberClassified;

        public void SetImageData(String path)
        {
            CurrentJpeg = path;

            var image = LoadImage(new Uri(path, UriKind.Relative));;

            FormImage = new CroppedBitmap(image, new Int32Rect(0, 0, (int)image.Width, (int)image.Height / 2));

            var numImages = new List<NumberImageType>();
            for (int i = 0; i < MainWindow.NumberOfNumbers; i++)
            {
                ImageSource numberImage;
                if (!File.Exists(getTif(i)))
                {
                    numberImage = BitmapImage.Create(2,2,96,96,PixelFormats.Indexed1,new BitmapPalette(new List<Color> { Colors.Transparent }),new byte[] { 0, 0, 0, 0 },1);
                }
                else { 
                    numberImage = LoadImage(new Uri(getTif(i), UriKind.Relative));
                }
                var imageType = new NumberImageType();
                imageType.NumberImage = numberImage;
                imageType.Title = "" + i;
                numImages.Add(imageType);
            }
            Numbers = numImages;
        }

        private static BitmapImage LoadImage(Uri path)
        {
            BitmapImage im = new BitmapImage();
            im.BeginInit();
            im.UriSource = path;
            im.CacheOption = BitmapCacheOption.OnLoad;
            im.EndInit();
            return im;
        }

        public string CurrentJpeg { get; set; }

        public string getTif(int i)
        {
            return CurrentJpeg.Replace(".jpg", "") + "~" + (i % MainWindow.NumberOfNumbers) + ".tif";
        }

        public ImageSource FormImage
        {
            get { 
                return _formImage; 
            }
            set
            {
                _formImage = value;
                OnPropertyChanged("FormImage");
            }
        }

        public double FormImageHeight
        {
            get
            {
                if (FormImage == null)
                {
                    return 0.0;
                }
                return FormImage.Height / 2.0;
            }
        }

        public double FormImageWidth
        {
            get
            {
                if (FormImage == null)
                {
                    return 0.0;
                }
                return FormImage.Width;
            }
        }

        public List<NumberImageType> Numbers
        {
            get { return _numberImages; }
            set
            {
                _numberImages = value;
                OnPropertyChanged("Numbers");
            }
        }

        public int NumberClassified
        {
            get { return _numberClassified; }
            set
            {
                _numberClassified = value;
                OnPropertyChanged("NumberClassified");
            }
        }

        protected void OnPropertyChanged(string name)
        {
            var handler = PropertyChanged;
            if (null != handler)
            {
                handler(this, new PropertyChangedEventArgs(name));
            }
        }
    }
    public class NumberImageType
    {
        public ImageSource NumberImage { get; set; }



        public string Title { get; set; }
    }
}
