# Automated Cellpose-SAM Segmentation

## 🧬 Advanced Multi-Image Cellular Segmentation with AI

![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Cellpose](https://img.shields.io/badge/cellpose-4.0%2B-green.svg)
![License](https://img.shields.io/badge/license-BSD--3--Clause-orange.svg)
![Windows](https://img.shields.io/badge/platform-Windows-lightgrey.svg)

An automated batch processing system for cellular segmentation using **Cellpose-SAM** (Segment Anything Model), designed for high-throughput microscopy image analysis.

---

## 🌟 Key Features

### 🚀 **Full Automation**
- **One-click batch processing** of multiple .tif/.tiff images
- **Intelligent folder selection** with GUI-based file management
- **Automated model loading** and GPU acceleration detection
- **Basic error handling** for improved processing stability

### 📊 **Advanced Progress Tracking**
- **Real-time progress bar** with percentage completion
- **Current file status** display during processing
- **Detailed logging** with timestamps and processing statistics
- **Multi-threaded processing** for responsive UI

### 🎛️ **Flexible Output Control**
- **Selectable output formats:**
  - ✅ Segmentation masks (.tif)
  - ✅ Flow fields (.tif) 
  - ✅ Cell probability maps (.tif)
  - ✅ Cell outlines (.tif)
  - ✅ Flow RGB visualizations (.png)
  - ✅ Colored mask visualizations (.png)

### ⚙️ **Smart Data Handling**
- **Automatic data type conversion** (uint8/uint16/uint32)
- **Label remapping** for compatibility
- **Memory-efficient processing** of large image sets
- **Fallback saving methods** for improved compatibility

---

## 🔬 Based on Cellpose

This project is built upon the outstanding work of the **Cellpose** team:

> **Cellpose**: A generalist algorithm for cellular segmentation with human-in-the-loop capabilities
> 
> 📖 **Official Repository**: [https://github.com/MouseLand/cellpose](https://github.com/MouseLand/cellpose)  
> 🌐 **Website**: [https://www.cellpose.org](https://www.cellpose.org)  
> 🤗 **HuggingFace Demo**: [https://huggingface.co/spaces/mouseland/cellpose](https://huggingface.co/spaces/mouseland/cellpose)

### 📚 **Citation Requirements**

If you use this tool in any publication, please cite the original Cellpose papers as required by the [Cellpose repository](https://github.com/MouseLand/cellpose):

```
Stringer, C., Wang, T., Michaelos, M., & Pachitariu, M. (2021). 
Cellpose: a generalist algorithm for cellular segmentation. 
Nature methods, 18(1), 100-106.

Pachitariu, M. & Stringer, C. (2022). 
Cellpose 2.0: how to train your own model. 
Nature methods, 19(12), 1634-1641.
```

---

## 🛠️ Installation

### Prerequisites

- **Windows 10/11** (tested platform)
- **Python 3.8+** (Python 3.13 recommended)
- **NVIDIA GPU** with CUDA support (recommended for performance)

### Quick Setup

1. **Clone this repository:**
   ```bash
   git clone https://github.com/TheRaiGames/AutomaticCellposeSAM2.git
   cd AutomaticCellposeSAM2
   ```

2. **Run the setup script:**
   ```batch
   setup_environment.bat
   ```

3. **Test your installation:**
   ```batch
   quick_start.bat
   ```

### Manual Installation

If you prefer manual setup:

```bash
# Install core dependencies
pip install cellpose[gui] tifffile pillow numpy

# For GPU support (Windows/Linux with CUDA)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

---

## 🚀 Quick Start

### Option 1: Enhanced GUI (Recommended)
```batch
run_enhanced_cellpose.bat
```

**Features:**
- ✨ Modern interface with progress tracking
- 🎯 Selectable output file types  
- 📊 Real-time processing statistics
- 📝 Integrated logging display
- 🚪 Safe exit functionality with processing protection

### Option 2: Basic GUI
```batch
run_automated_cellpose.bat
```

**Features:**
- 🖱️ Simple folder selection interface
- ⚡ Direct processing with default settings
- 📋 Console logging output

### Option 3: Command Line
```batch
run_cellpose_cmdline.bat "C:\path\to\input" "C:\path\to\output"
```

---

## 📋 Usage Guide

### 1. **Prepare Your Images**
- Place .tif or .tiff images in a dedicated input folder
- Images should be properly formatted (RGB or grayscale)
- Optimal cell size: <100 pixels across for best performance

### 2. **Launch the Application**
- Run `run_enhanced_cellpose.bat` for the full-featured interface
- Select your input folder containing images
- Choose output folder for results

### 3. **Configure Settings**
- **Model Selection**: `cpsam` (default), `cyto`, `cyto2`, `cyto3`, or `nuclei`
- **Cell Diameter**: `Auto` (recommended) or manual size in pixels
- **Output Selection**: Choose which file types to generate

### 4. **Start Processing**
- Click "Start Processing" to begin batch analysis
- Monitor progress in real-time with the progress bar
- View detailed logs in the integrated log display
- Use "Exit" button to safely close the application (with processing protection)

### 5. **Review Results**
Each processed image generates multiple output files:
```
output_folder/
├── image1_masks.tif           # Segmentation masks
├── image1_flows.tif           # Flow field data  
├── image1_cellprob.tif        # Cell probability map
├── image1_outlines.tif        # Cell boundaries
├── image1_flows_rgb.png       # Flow visualization
└── image1_masks.png           # Colored mask overlay
```

---

## 🎯 Example Workflow

### Input Images
- **A1_10x.tif** (1038×1388, 3-channel)
- **A2_10x.tif** (1038×1388, 3-channel)

### Processing Output
```
✅ A1_10x.tif → 316 cells detected
   ├── A1_10x_masks.tif (2.7MB)
   ├── A1_10x_flows.tif (11MB)  
   ├── A1_10x_cellprob.tif (5.5MB)
   └── A1_10x_outlines.tif (1.4MB)

✅ A2_10x.tif → 202 cells detected  
   ├── A2_10x_masks.tif (2.7MB)
   ├── A2_10x_flows.tif (11MB)
   ├── A2_10x_cellprob.tif (5.5MB)  
   └── A2_10x_outlines.tif (1.4MB)
```

### Performance Metrics
- **Processing Speed**: ~10 seconds per image (GPU)
- **Memory Usage**: Efficient handling of large datasets
- **Success Rate**: High with error recovery

---

## ⚙️ Technical Details

### Architecture Overview
```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   GUI Interface     │───▶│  Processing Engine   │───▶│   Output Manager    │
│ - Folder Selection  │    │ - Cellpose-SAM       │    │ - Multi-format Save │
│ - Progress Tracking │    │ - GPU Acceleration   │    │ - Data Type Handling│
│ - Output Selection  │    │ - Error Recovery     │    │ - Quality Control   │
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘
```

### Key Components

**1. Core Processing (`automated_cellpose_segmentation.py`)**
- Cellpose-SAM model initialization and management
- Batch image processing with error handling  
- Advanced data type conversion and compatibility
- Multi-format output generation

**2. Enhanced GUI (`automated_cellpose_enhanced_gui.py`)**
- Modern tkinter interface with progress tracking
- Multi-threaded processing for responsive UI
- Configurable output selection
- Integrated logging and error display

**3. Batch Scripts**
- `run_enhanced_cellpose.bat` - Enhanced GUI launcher
- `run_automated_cellpose.bat` - Basic GUI launcher  
- `setup_environment.bat` - Automated dependency installation
- `quick_start.bat` - Interactive setup guide

### Data Flow Pipeline
```
Input Images (.tif) → Image Loading → Cellpose-SAM Processing → 
Data Type Conversion → Multi-format Output Generation → 
Quality Validation → Results Saved
```

---

## 🔧 Advanced Configuration

### Model Parameters
- **diameter**: Cell size in pixels (None for auto-detection)
- **flow_threshold**: Flow error threshold (default: 0.4)
- **cellprob_threshold**: Cell probability threshold (default: 0.0)
- **channels**: Channel configuration ([0,0] for grayscale)

### Performance Optimization
- **GPU Usage**: Automatically detected and utilized
- **Memory Management**: Efficient handling of large image batches
- **Processing Speed**: ~10x faster with CUDA acceleration
- **Error Recovery**: Robust fallback mechanisms

### Output Customization
```python
# Example: Custom output selection
output_options = {
    'save_masks': True,        # Essential segmentation masks
    'save_flows': True,        # Flow field analysis
    'save_cellprob': False,    # Skip probability maps
    'save_outlines': True,     # Cell boundary detection
    'save_flow_rgb': False,    # Skip RGB visualizations
    'save_png_masks': True     # Generate PNG overlays
}
```

---

## 🐛 Troubleshooting

### Common Issues

**❌ "Python integer 65535 out of bounds for uint8"**
- ✅ **Fixed**: Automatic data type conversion implemented
- Labels exceeding uint8 range are automatically remapped

**❌ GPU not detected**
- Check NVIDIA drivers and CUDA installation
- Verify PyTorch CUDA support: `python -c "import torch; print(torch.cuda.is_available())"`

**❌ Import errors**
- Run `setup_environment.bat` to install all dependencies  
- Python 3.8+ should be installed

**❌ Processing hangs or crashes**
- Check available memory (images >2GB may require 16GB+ RAM)
- Reduce batch size for very large images
- Enable detailed logging for diagnosis

### Performance Tips
- **Resize large images** to <2048×2048 for optimal speed
- **Use SSD storage** for faster I/O operations  
- **Close other applications** to free up GPU memory
- **Process in smaller batches** for memory-constrained systems

---

## 🤝 Contributing

We welcome contributions to improve this automated segmentation tool!

### Development Setup
```bash
git clone https://github.com/TheRaiGames/AutomaticCellposeSAM2.git
cd AutomaticCellposeSAM2
pip install -e .
```

### Contribution Guidelines
- Follow Python PEP 8 style guidelines
- Add comprehensive docstrings and comments
- Include test cases for new features  
- Update documentation for any interface changes

---

## 🏗️ Development Credits

**Primary Development:**
- Developed using **Python** programming language
- Built with **Cursor** code editor
- AI assistance provided by **Claude-4-Sonnet** (Anthropic)

**Core Dependencies:**
- **[Cellpose](https://github.com/MouseLand/cellpose)** - Stringer et al., Nature Methods
- **PyTorch** - Deep learning framework
- **NumPy** - Numerical computing
- **Pillow** - Image processing
- **tifffile** - TIFF file handling
- **tkinter** - GUI framework

---

## 📄 License

This project is licensed under the **BSD 3-Clause License** - see the [LICENSE](LICENSE) file for details.

### Third-Party Licenses
- **Cellpose**: BSD 3-Clause License
- **PyTorch**: BSD-style License  
- **NumPy**: BSD License
- **Pillow**: HPND License

---

## 🙏 Acknowledgments

Special thanks to:
- **Cellpose team** (Stringer, Pachitariu et al.) for the foundational segmentation algorithm
- **PyTorch team** for the deep learning framework
- **Scientific Python community** for the ecosystem of tools
- **Cursor and Anthropic** for AI-assisted development tools

---

## 📞 Support

For Cellpose-specific questions, refer to the [official repository](https://github.com/MouseLand/cellpose).

### 🔧 Development Status

**Please note**: I am not a professional programmer and rely on AI tools (like Claude-4-Sonnet) for proper debugging and development. Updates to this tool will be done sporadically when time and resources allow.

### 🤝 Community Development

I hope this tool will be helpful for the scientific community! If you are programming-capable, please feel free to use this project as a starting point for further development. The codebase is designed to be modular and extensible, making it suitable for community contributions and improvements.

---

## 🔄 Updates

### Recent Updates
- ✅ Enhanced GUI with progress tracking
- ✅ Selectable output file formats  
- ✅ Robust data type handling
- ✅ Multi-threaded processing
- ✅ Basic error recovery

---

*Last updated: January 2025*

**⭐ If this tool is useful for your research, please consider starring the repository and citing the original Cellpose papers!**