#!/usr/bin/env python3
"""
Enhanced Automated Cellpose Segmentation with Progress Bar and Output Selection

This script provides an enhanced GUI for automated batch processing of microscopy images
using Cellpose-SAM, with progress tracking and selectable output formats.

Features:
- Interactive folder selection for input and output
- Checkbox selection for different output file types
- Real-time progress bar with percentage completion
- Detailed logging and error handling
- Support for .tif and .tiff image formats

Authors: Developed using Python with Cursor and Claude-4-Sonnet AI assistant
Based on: Cellpose by Stringer et al. (https://github.com/MouseLand/cellpose)
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import logging
import threading
from datetime import datetime
import glob
import numpy as np

# Import Cellpose components
try:
    from cellpose import models, io, utils
    from cellpose.io import logger_setup
    import tifffile
    from PIL import Image
except ImportError as e:
    print(f"Error importing required packages: {e}")
    print("Please install cellpose and required dependencies:")
    print("pip install cellpose[gui] tifffile pillow")
    sys.exit(1)

class EnhancedCellposeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Automated Cellpose Segmentation")
        self.root.geometry("800x900")
        
        # Configure window close event
        self.root.protocol("WM_DELETE_WINDOW", self.exit_application)
        
        # Variables
        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.model_var = tk.StringVar(value="cpsam")
        self.diameter_var = tk.StringVar(value="Auto")
        
        # Output selection variables
        self.save_masks = tk.BooleanVar(value=True)
        self.save_flows = tk.BooleanVar(value=True)
        self.save_cellprob = tk.BooleanVar(value=True)
        self.save_outlines = tk.BooleanVar(value=True)
        self.save_flow_rgb = tk.BooleanVar(value=False)
        self.save_png_masks = tk.BooleanVar(value=False)
        
        # Progress variables
        self.progress_var = tk.DoubleVar()
        self.current_file_var = tk.StringVar(value="Ready to start...")
        self.total_files = 0
        self.processed_files = 0
        
        # Processing state
        self.is_processing = False
        self.processing_thread = None
        
        self.setup_gui()
        self.setup_logging()
        
    def setup_gui(self):
        """Setup the enhanced GUI interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Title
        title_label = ttk.Label(main_frame, text="Enhanced Automated Cellpose Segmentation", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=row, column=0, columnspan=3, pady=(0, 20))
        row += 1
        
        # Folder Selection Section
        folder_frame = ttk.LabelFrame(main_frame, text="Folder Selection", padding="10")
        folder_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        folder_frame.columnconfigure(1, weight=1)
        row += 1
        
        # Input folder
        ttk.Label(folder_frame, text="Input Folder:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(folder_frame, textvariable=self.input_folder, width=60).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        ttk.Button(folder_frame, text="Browse", command=self.select_input_folder).grid(row=0, column=2, padx=(5, 0))
        
        # Output folder
        ttk.Label(folder_frame, text="Output Folder:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(folder_frame, textvariable=self.output_folder, width=60).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        ttk.Button(folder_frame, text="Browse", command=self.select_output_folder).grid(row=1, column=2, padx=(5, 0))
        
        # Model Settings Section
        model_frame = ttk.LabelFrame(main_frame, text="Model Settings", padding="10")
        model_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        row += 1
        
        # Model selection
        ttk.Label(model_frame, text="Model:").grid(row=0, column=0, sticky=tk.W, pady=2)
        model_combo = ttk.Combobox(model_frame, textvariable=self.model_var, 
                                  values=["cpsam", "cyto", "cyto2", "cyto3", "nuclei"], state="readonly")
        model_combo.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        # Diameter setting
        ttk.Label(model_frame, text="Cell Diameter:").grid(row=0, column=2, sticky=tk.W, padx=(20, 5), pady=2)
        diameter_combo = ttk.Combobox(model_frame, textvariable=self.diameter_var, 
                                    values=["Auto", "10", "15", "20", "25", "30", "35", "40"], state="readonly")
        diameter_combo.grid(row=0, column=3, sticky=tk.W, padx=(5, 0))
        
        # Output Selection Section
        output_frame = ttk.LabelFrame(main_frame, text="Output File Selection", padding="10")
        output_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        row += 1
        
        # Create checkboxes in two columns
        checkbox_frame1 = ttk.Frame(output_frame)
        checkbox_frame1.grid(row=0, column=0, sticky=(tk.W, tk.N))
        
        checkbox_frame2 = ttk.Frame(output_frame)
        checkbox_frame2.grid(row=0, column=1, sticky=(tk.W, tk.N), padx=(40, 0))
        
        # Column 1 checkboxes
        ttk.Checkbutton(checkbox_frame1, text="Segmentation Masks (.tif)", 
                       variable=self.save_masks).grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(checkbox_frame1, text="Flow Fields (.tif)", 
                       variable=self.save_flows).grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(checkbox_frame1, text="Cell Probability (.tif)", 
                       variable=self.save_cellprob).grid(row=2, column=0, sticky=tk.W, pady=2)
        
        # Column 2 checkboxes
        ttk.Checkbutton(checkbox_frame2, text="Cell Outlines (.tif)", 
                       variable=self.save_outlines).grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(checkbox_frame2, text="Flow RGB Visualization (.png)", 
                       variable=self.save_flow_rgb).grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(checkbox_frame2, text="PNG Mask Visualizations (.png)", 
                       variable=self.save_png_masks).grid(row=2, column=0, sticky=tk.W, pady=2)
        
        # Progress Section
        progress_frame = ttk.LabelFrame(main_frame, text="Processing Progress", padding="10")
        progress_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        row += 1
        
        # Current file label
        self.current_file_label = ttk.Label(progress_frame, textvariable=self.current_file_var)
        self.current_file_label.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                          maximum=100, length=400, mode='determinate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Progress percentage label
        self.progress_label = ttk.Label(progress_frame, text="0%")
        self.progress_label.grid(row=2, column=0, sticky=tk.W)
        
        # Control Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=(10, 0))
        row += 1
        
        self.start_button = ttk.Button(button_frame, text="Start Processing", 
                                     command=self.start_processing, style="Accent.TButton")
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="Stop Processing", 
                                    command=self.stop_processing, state="disabled")
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Clear Log", command=self.clear_log).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Exit", command=self.exit_application).pack(side=tk.LEFT)
        
        # Log Section
        log_frame = ttk.LabelFrame(main_frame, text="Processing Log", padding="10")
        log_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(row, weight=1)
        
        # Log text area with scrollbar
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def setup_logging(self):
        """Setup logging to display in GUI"""
        self.logger = logging.getLogger('enhanced_cellpose_gui')
        self.logger.setLevel(logging.INFO)
        
        # Create handler for GUI log display
        self.gui_handler = GUILogHandler(self.log_text)
        self.gui_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', 
                                    datefmt='%H:%M:%S')
        self.gui_handler.setFormatter(formatter)
        self.logger.addHandler(self.gui_handler)
        
        # Welcome message
        self.logger.info("Enhanced Automated Cellpose Segmentation - Ready")
        self.logger.info("Select input/output folders and configure settings to begin")
        
    def select_input_folder(self):
        """Select input folder containing .tif images"""
        folder = filedialog.askdirectory(title="Select Input Folder with .tif Images")
        if folder:
            self.input_folder.set(folder)
            # Count .tif files
            tif_files = self.get_tif_files(folder)
            self.logger.info(f"Selected input folder: {folder}")
            self.logger.info(f"Found {len(tif_files)} .tif/.tiff files")
            
    def select_output_folder(self):
        """Select output folder for results"""
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder.set(folder)
            self.logger.info(f"Selected output folder: {folder}")
            
    def get_tif_files(self, input_folder):
        """Get all .tif and .tiff files from the input folder"""
        tif_patterns = ['*.tif', '*.tiff', '*.TIF', '*.TIFF']
        tif_files = []
        
        for pattern in tif_patterns:
            tif_files.extend(glob.glob(os.path.join(input_folder, pattern)))
        
        # Remove duplicates and sort
        return sorted(list(set(tif_files)))
        
    def update_progress(self, current, total, current_file=""):
        """Update progress bar and labels"""
        if total > 0:
            percentage = (current / total) * 100
            self.progress_var.set(percentage)
            self.progress_label.config(text=f"{current}/{total} ({percentage:.1f}%)")
            
            if current_file:
                self.current_file_var.set(f"Processing: {os.path.basename(current_file)}")
            elif current >= total:
                self.current_file_var.set("Processing completed!")
                
        self.root.update_idletasks()
        
    def start_processing(self):
        """Start the batch processing in a separate thread"""
        if not self.input_folder.get() or not self.output_folder.get():
            messagebox.showerror("Error", "Please select both input and output folders")
            return
            
        # Check if at least one output type is selected
        if not any([self.save_masks.get(), self.save_flows.get(), self.save_cellprob.get(), 
                   self.save_outlines.get(), self.save_flow_rgb.get(), self.save_png_masks.get()]):
            messagebox.showerror("Error", "Please select at least one output file type")
            return
            
        # Disable start button, enable stop button
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.is_processing = True
        
        # Reset progress
        self.progress_var.set(0)
        self.processed_files = 0
        
        # Start processing thread
        self.processing_thread = threading.Thread(target=self.run_processing)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        
    def stop_processing(self):
        """Stop the batch processing"""
        self.is_processing = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.current_file_var.set("Processing stopped by user")
        self.logger.warning("Processing stopped by user")
        
    def clear_log(self):
        """Clear the log text area"""
        self.log_text.delete(1.0, tk.END)
        
    def exit_application(self):
        """Exit the application safely"""
        if self.is_processing:
            # Ask user confirmation if processing is running
            if messagebox.askyesno("Exit Confirmation", 
                                 "Processing is currently running. Do you want to stop and exit?"):
                self.stop_processing()
                self.logger.info("Application closing - processing stopped by user")
                self.root.quit()
                self.root.destroy()
        else:
            self.logger.info("Application closing")
            self.root.quit()
            self.root.destroy()
        
    def run_processing(self):
        """Main processing function running in separate thread"""
        try:
            input_folder = self.input_folder.get()
            output_folder = self.output_folder.get()
            model_name = self.model_var.get()
            diameter_str = self.diameter_var.get()
            
            # Parse diameter
            diameter = None if diameter_str == "Auto" else float(diameter_str)
            
            # Get output options
            output_options = {
                'save_masks': self.save_masks.get(),
                'save_flows': self.save_flows.get(),
                'save_cellprob': self.save_cellprob.get(),
                'save_outlines': self.save_outlines.get(),
                'save_flow_rgb': self.save_flow_rgb.get(),
                'save_png_masks': self.save_png_masks.get()
            }
            
            self.logger.info("Starting batch processing...")
            self.logger.info(f"Input folder: {input_folder}")
            self.logger.info(f"Output folder: {output_folder}")
            self.logger.info(f"Model: {model_name}")
            self.logger.info(f"Diameter: {diameter_str}")
            self.logger.info(f"Output options: {[k for k, v in output_options.items() if v]}")
            
            # Get list of files
            tif_files = self.get_tif_files(input_folder)
            self.total_files = len(tif_files)
            
            if self.total_files == 0:
                self.logger.error("No .tif/.tiff files found in input folder")
                return
                
            self.logger.info(f"Found {self.total_files} files to process")
            
            # Initialize model
            self.logger.info(f"Loading Cellpose model: {model_name}")
            model_instance = models.CellposeModel(gpu=True, pretrained_model=model_name)
            
            # Process each file
            success_count = 0
            for i, tif_file in enumerate(tif_files):
                if not self.is_processing:
                    break
                    
                try:
                    self.update_progress(i, self.total_files, tif_file)
                    self.logger.info(f"Processing file {i+1}/{self.total_files}: {os.path.basename(tif_file)}")
                    
                    # Load image
                    img = io.imread(tif_file)
                    
                    # Run segmentation
                    result = model_instance.eval(
                        img, 
                        diameter=diameter,
                        flow_threshold=0.4,
                        cellprob_threshold=0.0
                    )
                    
                    # Handle variable return values
                    if len(result) == 4:
                        masks, flows, styles, diams = result
                    elif len(result) == 3:
                        masks, flows, styles = result
                        diams = None
                    else:
                        raise ValueError(f"Unexpected eval return format: {len(result)} values")
                    
                    # Count cells
                    if isinstance(masks, list):
                        cell_count = len(masks) if masks else 0
                    else:
                        cell_count = len(np.unique(masks)) - 1 if 0 in np.unique(masks) else len(np.unique(masks))
                    
                    self.logger.info(f"Segmentation completed - found {cell_count} cells")
                    
                    # Save outputs based on selection
                    self.save_outputs(tif_file, img, masks, flows, output_folder, output_options)
                    
                    success_count += 1
                    self.processed_files += 1
                    
                except Exception as e:
                    self.logger.error(f"Error processing {os.path.basename(tif_file)}: {str(e)}")
                    continue
            
            # Final update
            self.update_progress(self.total_files, self.total_files)
            self.logger.info(f"Batch processing completed! Successfully processed: {success_count}/{self.total_files} files")
            
        except Exception as e:
            self.logger.error(f"Processing error: {str(e)}")
        finally:
            # Re-enable buttons
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
            self.is_processing = False
            
    def save_outputs(self, tif_file, img, masks, flows, output_folder, options):
        """Save selected output files"""
        base_name = os.path.splitext(os.path.basename(tif_file))[0]
        
        # Preprocess masks for compatibility
        processed_masks = self.preprocess_masks(masks)
        
        try:
            # Try standard save_masks if basic outputs are selected
            if options['save_masks'] and options['save_flows'] and not any([
                options['save_cellprob'], options['save_flow_rgb'], options['save_png_masks']]):
                
                io.save_masks(
                    img, 
                    processed_masks, 
                    flows, 
                    tif_file, 
                    savedir=output_folder,
                    save_flows=True,
                    save_outlines=options['save_outlines']
                )
                self.logger.info("Saved using standard method")
                return
        except Exception as e:
            self.logger.warning(f"Standard save failed: {e}, using custom save method")
        
        # Custom save for selected outputs
        if options['save_masks']:
            mask_file = os.path.join(output_folder, f"{base_name}_masks.tif")
            tifffile.imwrite(mask_file, processed_masks.astype(np.uint16))
            self.logger.info(f"Saved masks: {os.path.basename(mask_file)}")
            
        if options['save_flows'] and flows and len(flows) > 1 and flows[1] is not None:
            flows_file = os.path.join(output_folder, f"{base_name}_flows.tif")
            tifffile.imwrite(flows_file, flows[1].astype(np.float32))
            self.logger.info(f"Saved flows: {os.path.basename(flows_file)}")
            
        if options['save_cellprob'] and flows and len(flows) > 2 and flows[2] is not None:
            cellprob_file = os.path.join(output_folder, f"{base_name}_cellprob.tif")
            tifffile.imwrite(cellprob_file, flows[2].astype(np.float32))
            self.logger.info(f"Saved cellprob: {os.path.basename(cellprob_file)}")
            
        if options['save_outlines']:
            outlines = utils.masks_to_outlines(processed_masks)
            outline_file = os.path.join(output_folder, f"{base_name}_outlines.tif")
            tifffile.imwrite(outline_file, outlines.astype(np.uint8))
            self.logger.info(f"Saved outlines: {os.path.basename(outline_file)}")
            
        if options['save_flow_rgb'] and flows and len(flows) > 0 and flows[0] is not None:
            flow_rgb_file = os.path.join(output_folder, f"{base_name}_flows_rgb.png")
            Image.fromarray(flows[0].astype(np.uint8)).save(flow_rgb_file)
            self.logger.info(f"Saved flow RGB: {os.path.basename(flow_rgb_file)}")
            
        if options['save_png_masks']:
            # Create colored mask visualization
            mask_png_file = os.path.join(output_folder, f"{base_name}_masks.png")
            mask_rgb = self.create_mask_visualization(processed_masks)
            Image.fromarray(mask_rgb).save(mask_png_file)
            self.logger.info(f"Saved mask PNG: {os.path.basename(mask_png_file)}")
            
    def preprocess_masks(self, masks):
        """Preprocess masks to ensure data type compatibility"""
        if isinstance(masks, np.ndarray):
            if masks.max() > 65535:
                # Remap to sequential labels
                unique_labels = np.unique(masks)
                unique_labels = unique_labels[unique_labels > 0]
                processed_masks = np.zeros_like(masks, dtype=np.uint16)
                for i, label in enumerate(unique_labels):
                    processed_masks[masks == label] = i + 1
                return processed_masks
            elif masks.max() > 255:
                return masks.astype(np.uint16)
            else:
                return masks
        return masks
        
    def create_mask_visualization(self, masks):
        """Create a colored visualization of masks"""
        if masks.max() == 0:
            return np.zeros((*masks.shape, 3), dtype=np.uint8)
            
        # Create random colors for each label
        colors = np.random.randint(0, 255, (masks.max() + 1, 3), dtype=np.uint8)
        colors[0] = [0, 0, 0]  # Background black
        
        # Apply colors
        mask_rgb = colors[masks]
        return mask_rgb

class GUILogHandler(logging.Handler):
    """Custom logging handler to display logs in GUI text widget"""
    
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        
    def emit(self, record):
        try:
            msg = self.format(record)
            self.text_widget.insert(tk.END, msg + '\n')
            self.text_widget.see(tk.END)
            self.text_widget.update_idletasks()
        except:
            pass

def main():
    """Main function to run the enhanced GUI"""
    root = tk.Tk()
    app = EnhancedCellposeGUI(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Application interrupted by user")
        
if __name__ == "__main__":
    main()